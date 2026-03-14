from flask import Blueprint, request, jsonify
from app import db
from app.models import Ticket, Message, User, Agent
from app.services.sms_service import send_sms
from datetime import datetime
from sqlalchemy import or_, and_

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filters"""
    try:
        # Get query parameters
        status = request.args.get('status')
        agent_id = request.args.get('agent_id')
        category = request.args.get('category')
        priority = request.args.get('priority')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Build query
        query = Ticket.query
        
        if status:
            query = query.filter_by(status=status)
        if agent_id:
            query = query.filter_by(agent_id=int(agent_id))
        if category:
            query = query.filter_by(category=category)
        if priority:
            query = query.filter_by(priority=priority)
        
        # Order by updated time (most recent first)
        query = query.order_by(Ticket.updated_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        tickets = [ticket.to_dict() for ticket in pagination.items]
        
        return jsonify({
            'tickets': tickets,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting tickets: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get specific ticket with messages"""
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        return jsonify(ticket.to_dict(include_messages=True)), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('', methods=['POST'])
def create_ticket():
    """Create a new ticket"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('user_id'):
            return jsonify({'error': 'user_id is required'}), 400
        
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create ticket
        ticket = Ticket(
            user_id=data['user_id'],
            subject=data.get('subject', 'New inquiry'),
            category=data.get('category', 'other'),
            priority=data.get('priority', 'medium'),
            status='open'
        )
        
        # Auto-assign to agent if specified
        if data.get('agent_id'):
            agent = Agent.query.get(data['agent_id'])
            if agent and agent.is_active:
                ticket.agent_id = agent.id
                ticket.status = 'assigned'
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify(ticket.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error creating ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<int:ticket_id>/reply', methods=['POST'])
def reply_to_ticket(ticket_id):
    """Send reply to ticket (agent response)"""
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'text is required'}), 400
        
        # Create outbound message
        message = Message(
            user_id=ticket.user_id,
            ticket_id=ticket.id,
            direction='out',
            text=text,
            status='pending'
        )
        db.session.add(message)
        
        # Update ticket
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send SMS
        user = User.query.get(ticket.user_id)
        success = send_sms(user.phone, text)
        
        if success:
            message.status = 'sent'
            message.processed_at = datetime.utcnow()
        else:
            message.status = 'failed'
        
        db.session.commit()
        
        return jsonify({
            'message': message.to_dict(),
            'ticket': ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error replying to ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<int:ticket_id>/assign', methods=['POST'])
def assign_ticket(ticket_id):
    """Assign ticket to an agent"""
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'agent_id is required'}), 400
        
        agent = Agent.query.get(agent_id)
        
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        if not agent.is_active:
            return jsonify({'error': 'Agent is not active'}), 400
        
        # Check agent capacity
        active_tickets = Ticket.query.filter_by(
            agent_id=agent_id,
            status='assigned'
        ).count()
        
        if active_tickets >= agent.max_concurrent_tickets:
            return jsonify({'error': 'Agent has reached maximum ticket capacity'}), 400
        
        # Assign ticket
        ticket.agent_id = agent_id
        ticket.status = 'assigned'
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(ticket.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error assigning ticket: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<int:ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """Update ticket status"""
    try:
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        valid_statuses = ['open', 'assigned', 'resolved', 'closed']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()
        
        if new_status == 'resolved':
            ticket.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(ticket.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error updating ticket status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/stats', methods=['GET'])
def get_ticket_stats():
    """Get ticket statistics"""
    try:
        stats = {
            'total': Ticket.query.count(),
            'open': Ticket.query.filter_by(status='open').count(),
            'assigned': Ticket.query.filter_by(status='assigned').count(),
            'resolved': Ticket.query.filter_by(status='resolved').count(),
            'closed': Ticket.query.filter_by(status='closed').count(),
            'by_category': {},
            'by_priority': {}
        }
        
        # Category breakdown
        categories = ['agriculture', 'loan', 'job', 'training', 'other']
        for category in categories:
            stats['by_category'][category] = Ticket.query.filter_by(category=category).count()
        
        # Priority breakdown
        priorities = ['low', 'medium', 'high', 'urgent']
        for priority in priorities:
            stats['by_priority'][priority] = Ticket.query.filter_by(priority=priority).count()
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting ticket stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
