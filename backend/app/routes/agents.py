from flask import Blueprint, request, jsonify
from app import db
from app.models import Agent, Ticket
from datetime import datetime

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('', methods=['GET'])
def get_agents():
    """Get all agents"""
    try:
        agents = Agent.query.all()
        return jsonify([agent.to_dict() for agent in agents]), 200
    except Exception as e:
        print(f"[ERROR] Error getting agents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<int:agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent"""
    try:
        agent = Agent.query.get(agent_id)
        
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get agent's tickets
        tickets = Ticket.query.filter_by(agent_id=agent_id).all()
        
        agent_data = agent.to_dict()
        agent_data['tickets'] = [ticket.to_dict() for ticket in tickets]
        
        return jsonify(agent_data), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting agent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('', methods=['POST'])
def create_agent():
    """Create a new agent"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing = Agent.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create agent
        agent = Agent(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            role=data.get('role', 'agent'),
            specialization=data.get('specialization', 'general'),
            max_concurrent_tickets=data.get('max_concurrent_tickets', 10),
            is_active=True
        )
        
        # Set password (required by model)
        password = data.get('password') or 'agent123'
        agent.set_password(password)
        
        db.session.add(agent)
        db.session.commit()
        
        return jsonify(agent.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error creating agent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update agent information"""
    try:
        agent = Agent.query.get(agent_id)
        
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            agent.name = data['name']
        if 'phone' in data:
            agent.phone = data['phone']
        if 'role' in data:
            agent.role = data['role']
        if 'specialization' in data:
            agent.specialization = data['specialization']
        if 'is_active' in data:
            agent.is_active = data['is_active']
        if 'max_concurrent_tickets' in data:
            agent.max_concurrent_tickets = data['max_concurrent_tickets']
        if 'password' in data and data['password']:
            agent.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify(agent.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error updating agent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete (deactivate) an agent"""
    try:
        agent = Agent.query.get(agent_id)
        
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Don't actually delete, just deactivate
        agent.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Agent deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error deleting agent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/available', methods=['GET'])
def get_available_agents():
    """Get agents available for ticket assignment"""
    try:
        specialization = request.args.get('specialization')
        
        # Get active agents
        query = Agent.query.filter_by(is_active=True)
        
        if specialization:
            query = query.filter(
                (Agent.specialization == specialization) | 
                (Agent.specialization == 'general')
            )
        
        agents = query.all()
        
        # Filter by capacity
        available_agents = []
        for agent in agents:
            active_count = Ticket.query.filter_by(
                agent_id=agent.id,
                status='assigned'
            ).count()
            
            if active_count < agent.max_concurrent_tickets:
                agent_data = agent.to_dict()
                agent_data['available_slots'] = agent.max_concurrent_tickets - active_count
                available_agents.append(agent_data)
        
        return jsonify(available_agents), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting available agents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<int:agent_id>/performance', methods=['GET'])
def get_agent_performance(agent_id):
    """Get agent performance metrics"""
    try:
        agent = Agent.query.get(agent_id)
        
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Calculate metrics
        total_tickets = Ticket.query.filter_by(agent_id=agent_id).count()
        resolved_tickets = Ticket.query.filter_by(
            agent_id=agent_id,
            status='resolved'
        ).count()
        active_tickets = Ticket.query.filter_by(
            agent_id=agent_id,
            status='assigned'
        ).count()
        
        performance = {
            'agent_id': agent_id,
            'agent_name': agent.name,
            'total_tickets': total_tickets,
            'resolved_tickets': resolved_tickets,
            'active_tickets': active_tickets,
            'resolution_rate': round((resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0, 2)
        }
        
        return jsonify(performance), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting agent performance: {str(e)}")
        return jsonify({'error': str(e)}), 500
