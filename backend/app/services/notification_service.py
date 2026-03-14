from app.services.sms_service import send_sms
from app.models import User, Agent
from typing import List

def notify_user(user_id: int, message: str) -> bool:
    """Send notification to a user"""
    try:
        from app import db
        user = db.session.get(User, user_id)
        
        if not user:
            print(f"[WARN]  User {user_id} not found")
            return False
        
        return send_sms(user.phone, message)
        
    except Exception as e:
        print(f"[ERROR] Failed to notify user {user_id}: {str(e)}")
        return False

def notify_agent(agent_id: int, message: str) -> bool:
    """Send notification to an agent"""
    try:
        from app import db
        agent = db.session.get(Agent, agent_id)
        
        if not agent or not agent.phone:
            print(f"[WARN]  Agent {agent_id} not found or has no phone")
            return False
        
        return send_sms(agent.phone, message)
        
    except Exception as e:
        print(f"[ERROR] Failed to notify agent {agent_id}: {str(e)}")
        return False

def broadcast_message(user_ids: List[int], message: str) -> dict:
    """Send message to multiple users"""
    results = {
        'success': 0,
        'failed': 0,
        'total': len(user_ids)
    }
    
    from app import db
    
    for user_id in user_ids:
        user = db.session.get(User, user_id)
        if user:
            if send_sms(user.phone, message):
                results['success'] += 1
            else:
                results['failed'] += 1
        else:
            results['failed'] += 1
    
    return results

def send_ticket_notification(ticket_id: int, notification_type: str) -> bool:
    """
    Send notification about ticket status
    notification_type: 'created', 'assigned', 'resolved', 'closed'
    """
    try:
        from app import db
        from app.models import Ticket
        
        ticket = db.session.get(Ticket, ticket_id)
        
        if not ticket:
            return False
        
        messages = {
            'created': f"Your inquiry (Ticket #{ticket.id}) has been received. An agent will respond soon.",
            'assigned': f"Your inquiry (Ticket #{ticket.id}) has been assigned to an agent.",
            'resolved': f"Your inquiry (Ticket #{ticket.id}) has been resolved. Reply if you need more help.",
            'closed': f"Your inquiry (Ticket #{ticket.id}) is now closed. Thank you for contacting us."
        }
        
        message = messages.get(notification_type)
        
        if message:
            return notify_user(ticket.user_id, message)
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to send ticket notification: {str(e)}")
        return False

def send_daily_summary(agent_id: int) -> bool:
    """Send daily summary to agent"""
    try:
        from app import db
        from app.models import Ticket
        from datetime import datetime, timedelta
        
        agent = db.session.get(Agent, agent_id)
        
        if not agent:
            return False
        
        # Get today's stats
        today = datetime.utcnow().date()
        tickets_today = Ticket.query.filter(
            Ticket.agent_id == agent_id,
            Ticket.created_at >= today
        ).count()
        
        resolved_today = Ticket.query.filter(
            Ticket.agent_id == agent_id,
            Ticket.resolved_at >= today
        ).count()
        
        pending = Ticket.query.filter(
            Ticket.agent_id == agent_id,
            Ticket.status == 'assigned'
        ).count()
        
        message = f"Daily Summary:\nNew: {tickets_today}\nResolved: {resolved_today}\nPending: {pending}"
        
        return notify_agent(agent_id, message)
        
    except Exception as e:
        print(f"[ERROR] Failed to send daily summary: {str(e)}")
        return False
