"""
Create sample messages and tickets for testing analytics
"""
from app import create_app, db
from app.models import User, Message, Ticket, Agent
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("Creating sample data...")
    
    # Create users
    users_data = [
        {"phone": "+919876543210", "language": "en"},
        {"phone": "+919876543211", "language": "en"},
        {"phone": "+919876543212", "language": "en"},
        {"phone": "+919876543213", "language": "hi"},
        {"phone": "+919876543214", "language": "en"},
    ]
    
    users = []
    for user_data in users_data:
        user = User.query.filter_by(phone=user_data["phone"]).first()
        if not user:
            user = User(**user_data)
            db.session.add(user)
            db.session.flush()
        users.append(user)
    
    # Get or create agent
    agent = Agent.query.first()
    if not agent:
        agent = Agent(
            name="Admin Agent",
            email="admin@example.com",
            phone="+919999999999",
            role="admin",
            is_active=True
        )
        agent.set_password("admin123")
        db.session.add(agent)
        db.session.flush()
    
    # Sample messages
    sample_messages = [
        {"text": "I need help finding a job in construction", "intent": "employment"},
        {"text": "Are there any training programs available?", "intent": "training"},
        {"text": "I need a loan to start a business", "intent": "loan"},
        {"text": "What government schemes can I apply for?", "intent": "schemes"},
        {"text": "Looking for work opportunities", "intent": "employment"},
    ]
    
    # Create tickets and messages
    for i, (user, msg_data) in enumerate(zip(users, sample_messages)):
        # Create ticket
        ticket = Ticket.query.filter_by(user_id=user.id).first()
        if not ticket:
            ticket = Ticket(
                user_id=user.id,
                status=random.choice(['open', 'assigned', 'resolved']),
                priority=random.choice(['low', 'medium', 'high']),
                category=msg_data['intent'],
                subject=msg_data['text'][:100],
                assigned_to=agent.id if random.random() > 0.3 else None,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
            )
            db.session.add(ticket)
            db.session.flush()
        
        # Create inbound message
        inbound_msg = Message(
            user_id=user.id,
            ticket_id=ticket.id,
            direction='in',
            text=msg_data['text'],
            status='processed',
            intent=msg_data['intent'],
            confidence=0.95,
            created_at=ticket.created_at
        )
        db.session.add(inbound_msg)
        
        # Create outbound message (response)
        outbound_msg = Message(
            user_id=user.id,
            ticket_id=ticket.id,
            direction='out',
            text=f"Thank you for contacting us. We've received your request about {msg_data['intent']}.",
            status='sent',
            created_at=ticket.created_at + timedelta(minutes=5)
        )
        db.session.add(outbound_msg)
    
    db.session.commit()
    
    # Print summary
    print("\n✅ Sample data created successfully!")
    print(f"   Users: {User.query.count()}")
    print(f"   Tickets: {Ticket.query.count()}")
    print(f"   Messages: {Message.query.count()}")
    print(f"   Agents: {Agent.query.count()}")
    print("\nNow refresh your Analytics page!")
