from flask import Blueprint, request, jsonify
from app import db
from app.models import Message, Ticket, User, Agent, Analytics
from app.services.predictive_analytics import PredictiveAnalytics

predictive_service = PredictiveAnalytics()
from datetime import datetime, timedelta
from sqlalchemy import func, case

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        # Date range (default: last 30 days)
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Message statistics
        total_messages = Message.query.filter(Message.created_at >= start_date).count()
        inbound_messages = Message.query.filter(
            Message.created_at >= start_date,
            Message.direction == 'in'
        ).count()
        outbound_messages = Message.query.filter(
            Message.created_at >= start_date,
            Message.direction == 'out'
        ).count()
        
        # Ticket statistics
        total_tickets = Ticket.query.filter(Ticket.created_at >= start_date).count()
        open_tickets = Ticket.query.filter_by(status='open').count()
        resolved_tickets = Ticket.query.filter(
            Ticket.created_at >= start_date,
            Ticket.status == 'resolved'
        ).count()
        
        # User statistics
        total_users = User.query.count()
        new_users = User.query.filter(User.created_at >= start_date).count()
        active_users = User.query.filter(User.last_active >= start_date).count()
        
        # Agent statistics
        active_agents = Agent.query.filter_by(is_active=True).count()
        
        # Intent breakdown (from messages in date range)
        intent_stats = db.session.query(
            Message.intent,
            func.count(Message.id).label('count')
        ).filter(
            Message.created_at >= start_date,
            Message.intent.isnot(None)
        ).group_by(Message.intent).all()
        
        intent_breakdown = {intent: count for intent, count in intent_stats}
        
        # Response time (average time to first response)
        avg_response_time = calculate_avg_response_time(start_date)
        
        # Daily message trend
        daily_trend = get_daily_message_trend(days)
        
        analytics_data = {
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat()
            },
            'messages': {
                'total': total_messages,
                'inbound': inbound_messages,
                'outbound': outbound_messages,
                'daily_average': round(total_messages / days, 2) if days > 0 else 0
            },
            'tickets': {
                'total': total_tickets,
                'open': open_tickets,
                'resolved': resolved_tickets,
                'resolution_rate': round((resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0, 2)
            },
            'users': {
                'total': total_users,
                'new': new_users,
                'active': active_users
            },
            'agents': {
                'active': active_agents
            },
            'intent_breakdown': intent_breakdown,
            'avg_response_time_minutes': avg_response_time,
            'daily_trend': daily_trend
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting dashboard analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/intents', methods=['GET'])
def get_intent_analytics():
    """Get detailed intent classification analytics"""
    try:
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Intent distribution
        intent_data = db.session.query(
            Message.intent,
            func.count(Message.id).label('count'),
            func.avg(Message.confidence).label('avg_confidence')
        ).filter(
            Message.created_at >= start_date,
            Message.intent.isnot(None)
        ).group_by(Message.intent).all()
        
        intents = []
        for intent, count, avg_conf in intent_data:
            intents.append({
                'intent': intent,
                'count': count,
                'avg_confidence': round(float(avg_conf) if avg_conf else 0, 3),
                'percentage': 0  # Will calculate below
            })
        
        # Calculate percentages
        total = sum(item['count'] for item in intents)
        for item in intents:
            item['percentage'] = round((item['count'] / total * 100) if total > 0 else 0, 2)
        
        # Sort by count
        intents.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'intents': intents,
            'total_classified': total,
            'period_days': days
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting intent analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        days = int(request.args.get('days', 7))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Message processing success rate
        total_messages = Message.query.filter(Message.created_at >= start_date).count()
        processed_messages = Message.query.filter(
            Message.created_at >= start_date,
            Message.status.in_(['processed', 'sent'])
        ).count()
        
        success_rate = round((processed_messages / total_messages * 100) if total_messages > 0 else 0, 2)
        
        # Average response time
        avg_response_time = calculate_avg_response_time(start_date)
        
        # Ticket resolution time
        resolved_tickets = Ticket.query.filter(
            Ticket.resolved_at >= start_date,
            Ticket.resolved_at.isnot(None)
        ).all()
        
        resolution_times = []
        for ticket in resolved_tickets:
            if ticket.resolved_at and ticket.created_at:
                delta = ticket.resolved_at - ticket.created_at
                resolution_times.append(delta.total_seconds() / 3600)  # hours
        
        avg_resolution_time = round(sum(resolution_times) / len(resolution_times), 2) if resolution_times else 0
        
        performance = {
            'message_success_rate': success_rate,
            'avg_response_time_minutes': avg_response_time,
            'avg_ticket_resolution_hours': avg_resolution_time,
            'total_messages_processed': processed_messages,
            'period_days': days
        }
        
        return jsonify(performance), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting performance metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/train', methods=['POST'])
def train_models():
    """Trigger predictive analytics model training"""
    try:
        routing_trained = predictive_service.train_routing_model()
        priority_trained = predictive_service.train_priority_model()
        resolution_trained = predictive_service.train_resolution_time_model()

        response = {
            'routing_model': 'trained' if routing_trained else 'skipped',
            'priority_model': 'trained' if priority_trained else 'skipped',
            'resolution_time_model': 'trained' if resolution_trained else 'skipped',
            'message': 'Training complete. Models marked as "skipped" need more data.'
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"[ERROR] Error training analytics models: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_avg_response_time(start_date):
    """Calculate average response time in minutes"""
    # Get tickets with at least one outbound message
    tickets = Ticket.query.filter(Ticket.created_at >= start_date).all()
    
    response_times = []
    for ticket in tickets:
        first_inbound = Message.query.filter_by(
            ticket_id=ticket.id,
            direction='in'
        ).order_by(Message.created_at.asc()).first()
        
        first_outbound = Message.query.filter_by(
            ticket_id=ticket.id,
            direction='out'
        ).order_by(Message.created_at.asc()).first()
        
        if first_inbound and first_outbound:
            delta = first_outbound.created_at - first_inbound.created_at
            response_times.append(delta.total_seconds() / 60)  # minutes
    
    return round(sum(response_times) / len(response_times), 2) if response_times else 0

def get_daily_message_trend(days):
    """Get daily message counts for trend analysis"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    daily_data = db.session.query(
        func.date(Message.created_at).label('date'),
        func.count(Message.id).label('count')
    ).filter(
        Message.created_at >= start_date
    ).group_by(
        func.date(Message.created_at)
    ).order_by('date').all()
    
    return [
        {
            'date': date if isinstance(date, str) else date.isoformat(),
            'count': count
        }
        for date, count in daily_data
    ]
