from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Ticket, Message, Agent, VoiceCall
from datetime import datetime, timedelta
import random

demo_bp = Blueprint('demo', __name__)


@demo_bp.route('/api/demo/seed', methods=['POST'])
def seed_demo_data():
    """Create demo tickets and messages for presentations."""
    try:
        count = int(request.args.get('count', 25))
        count = max(5, min(count, 50))
        
        subjects = [
            'Need information about loans for farmers',
            'Looking for skill training programs',
            'Seeking government scheme details',
            'Job opportunities for youth',
            'Need help with microfinance application',
            'Support for crop insurance',
            'Assistance with ration card',
            'Guidance on employment registration'
        ]
        categories = ['loan', 'training', 'schemes', 'employment', 'agriculture', 'finance', 'general']
        intent_map = {
            'loan': 'loan_query',
            'training': 'training_query',
            'schemes': 'scheme_query',
            'employment': 'job_query',
            'agriculture': 'agri_support',
            'finance': 'finance_query',
            'general': 'general_help'
        }
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['open', 'assigned', 'resolved']
        
        # Ensure demo agents exist
        demo_agents = [
            {'name': 'Admin Agent', 'email': 'admin@helpline.com', 'role': 'admin', 'specialization': 'general'},
            {'name': 'Agriculture Expert', 'email': 'agri@helpline.com', 'role': 'agent', 'specialization': 'agriculture'},
            {'name': 'Loan Advisor', 'email': 'loan@helpline.com', 'role': 'agent', 'specialization': 'finance'},
            {'name': 'Training Guide', 'email': 'train@helpline.com', 'role': 'agent', 'specialization': 'training'}
        ]
        agents = []
        for item in demo_agents:
            agent = Agent.query.filter_by(email=item['email']).first()
            if not agent:
                agent = Agent(
                    name=item['name'],
                    email=item['email'],
                    role=item['role'],
                    specialization=item['specialization'],
                    is_active=True,
                    max_concurrent_tickets=10
                )
                agent.set_password('agent123')
                db.session.add(agent)
                db.session.flush()
            agents.append(agent)

        created = 0
        for i in range(count):
            phone = f"+91{random.randint(7000000000, 9999999999)}"
            user = User.query.filter_by(phone=phone).first()
            if not user:
                user = User(phone=phone, language='en')
                db.session.add(user)
                db.session.flush()
            
            subject = random.choice(subjects)
            category = random.choice(categories)
            intent = intent_map.get(category, 'general_help')
            confidence = round(random.uniform(0.6, 0.95), 2)
            priority = random.choice(priorities)
            status = random.choice(statuses)
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 14), hours=random.randint(0, 10))
            
            assigned_agent = random.choice(agents) if agents else None
            ticket = Ticket(
                user_id=user.id,
                subject=subject,
                category=category,
                priority=priority,
                status=status,
                agent_id=assigned_agent.id if assigned_agent else None,
                created_at=created_at,
                updated_at=created_at
            )
            if status == 'resolved':
                ticket.resolved_at = created_at + timedelta(hours=random.randint(2, 24))
            db.session.add(ticket)
            db.session.flush()
            
            inbound = Message(
                user_id=user.id,
                ticket_id=ticket.id,
                direction='in',
                text=subject,
                status='processed',
                intent=intent,
                confidence=confidence,
                created_at=created_at
            )
            db.session.add(inbound)
            
            if status in ['assigned', 'resolved']:
                outbound = Message(
                    user_id=user.id,
                    ticket_id=ticket.id,
                    direction='out',
                    text='Thanks for reaching out. We will assist you shortly.',
                    status='sent',
                    created_at=created_at + timedelta(minutes=random.randint(10, 120))
                )
                db.session.add(outbound)
            
            created += 1
        
        db.session.commit()
        return jsonify({'status': 'ok', 'created': created}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/api/demo/reset', methods=['POST'])
def reset_demo_data():
    """Clear demo tickets/messages/voice calls for a fresh demo."""
    try:
        # Delete messages first, then tickets, then voice calls
        db.session.query(Message).delete()
        db.session.query(Ticket).delete()
        db.session.query(VoiceCall).delete()
        db.session.commit()
        return jsonify({'status': 'ok', 'message': 'Demo data cleared'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
