"""Quick CSV export script for demo purposes"""
from app import create_app
from app.database import get_db
from app.models import Ticket, Message, Agent
import csv

app = create_app()

with app.app_context():
    db = get_db()
    
    # Get all tickets
    tickets = db.query(Ticket).all()
    print(f"Found {len(tickets)} tickets")
    
    # Create CSV
    with open('tickets_export_manual.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Ticket ID', 'Phone Number', 'Status', 'Category', 
            'Priority', 'Assigned Agent', 'Created At', 'Updated At',
            'First Message', 'Last Message'
        ])
        
        # Data
        for ticket in tickets:
            phone = ticket.user.phone if ticket.user else 'No User'
            agent_name = ''
            if ticket.assigned_to:
                agent = db.query(Agent).filter(Agent.id == ticket.assigned_to).first()
                agent_name = agent.name if agent else ''
            
            messages = db.query(Message).filter(Message.ticket_id == ticket.id).order_by(Message.created_at).all()
            first_msg = messages[0].text[:100] if messages else ''
            last_msg = messages[-1].text[:100] if len(messages) > 1 else first_msg
            
            writer.writerow([
                ticket.id,
                phone,
                ticket.status,
                ticket.intent or 'Uncategorized',
                ticket.priority or 'medium',
                agent_name,
                ticket.created_at,
                ticket.updated_at,
                first_msg,
                last_msg
            ])
    
    print("✓ CSV exported to: tickets_export_manual.csv")
