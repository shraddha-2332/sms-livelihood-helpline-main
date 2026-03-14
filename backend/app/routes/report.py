from flask import Blueprint, jsonify, request, send_file
from app.database import get_db
from app.models import Ticket, Message, Agent
from datetime import datetime, timedelta
import csv
import io
from sqlalchemy import func, and_
from functools import wraps
from app.routes.auth import verify_token

reports_bp = Blueprint('reports', __name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid authorization header format'}), 401
        token = parts[1]
        agent_id = verify_token(token)
        if not agent_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@reports_bp.route('/api/reports/tickets/export', methods=['GET'])
@token_required
def export_tickets():
    try:
        db = get_db()
        query = db.query(Ticket)
        
        # Apply date filters if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        category = request.args.get('category')
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0)
            query = query.filter(Ticket.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59)
            query = query.filter(Ticket.created_at <= end_dt)
        if status:
            query = query.filter(Ticket.status == status)
        if category:
            query = query.filter(Ticket.category == category)
        
        tickets = query.all()
        print(f"[INFO] Exporting {len(tickets)} tickets")
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ticket ID', 'Phone', 'Status', 'Category', 'Priority', 'Agent', 'Created', 'Updated', 'First Message'])
        
        for ticket in tickets:
            phone = ticket.user.phone if ticket.user else ''
            agent_name = ticket.agent.name if ticket.agent else ''
            messages = db.query(Message).filter(Message.ticket_id == ticket.id).order_by(Message.created_at).all()
            first_msg = messages[0].text[:100] if messages else ''
            
            writer.writerow([
                ticket.id,
                phone,
                ticket.status,
                ticket.category or 'Uncategorized',
                ticket.priority or 'medium',
                agent_name,
                ticket.created_at.strftime('%Y-%m-%d %H:%M') if ticket.created_at else '',
                ticket.updated_at.strftime('%Y-%m-%d %H:%M') if ticket.updated_at else '',
                first_msg
            ])
        
        output.seek(0)
        byte_output = io.BytesIO()
        byte_output.write(output.getvalue().encode('utf-8'))
        byte_output.seek(0)
        
        return send_file(byte_output, mimetype='text/csv', as_attachment=True, 
                        download_name=f"tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    except Exception as e:
        print(f"[ERROR] Export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/api/reports/analytics', methods=['GET'])
@token_required
def get_analytics():
    try:
        db = get_db()
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        tickets_by_status = db.query(Ticket.status, func.count(Ticket.id).label('count')).filter(
            Ticket.created_at >= start_date).group_by(Ticket.status).all()
        tickets_by_category = db.query(Ticket.category, func.count(Ticket.id).label('count')).filter(
            Ticket.created_at >= start_date).group_by(Ticket.category).all()
        tickets_by_priority = db.query(Ticket.priority, func.count(Ticket.id).label('count')).filter(
            Ticket.created_at >= start_date).group_by(Ticket.priority).all()
        
        resolved_tickets = db.query(Ticket).filter(and_(Ticket.status == 'resolved', Ticket.created_at >= start_date)).all()
        total_resolution_time = sum([(t.updated_at - t.created_at).total_seconds() / 3600 
                                     for t in resolved_tickets if t.updated_at and t.created_at], 0)
        avg_resolution_time = round(total_resolution_time / len(resolved_tickets), 2) if resolved_tickets else 0
        
        tickets_per_day = []
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59)
            count = db.query(func.count(Ticket.id)).filter(
                and_(Ticket.created_at >= day_start, Ticket.created_at <= day_end)).scalar() or 0
            tickets_per_day.append({'date': day.strftime('%Y-%m-%d'), 'count': count})
        tickets_per_day.reverse()
        
        agent_performance = []
        for agent in db.query(Agent).all():
            total = db.query(func.count(Ticket.id)).filter(
                and_(Ticket.agent_id == agent.id, Ticket.created_at >= start_date)).scalar() or 0
            resolved = db.query(func.count(Ticket.id)).filter(
                and_(Ticket.agent_id == agent.id, Ticket.status == 'resolved', Ticket.created_at >= start_date)).scalar() or 0
            if total > 0:
                agent_performance.append({
                    'agent_id': agent.id,
                    'agent_name': agent.name,
                    'total_tickets': total,
                    'resolved_tickets': resolved,
                    'resolution_rate': round((resolved / total * 100), 2)
                })
        
        return jsonify({
            'tickets_by_status': [{'status': s.status or 'Unknown', 'count': s.count} for s in tickets_by_status],
            'tickets_by_category': [{'category': s.category or 'Uncategorized', 'count': s.count} for s in tickets_by_category],
            'tickets_by_priority': [{'priority': s.priority or 'medium', 'count': s.count} for s in tickets_by_priority],
            'avg_resolution_time_hours': avg_resolution_time,
            'tickets_per_day': tickets_per_day,
            'agent_performance': agent_performance,
            'date_range': {'start': start_date.strftime('%Y-%m-%d'), 'end': datetime.now().strftime('%Y-%m-%d'), 'days': days}
        })
    except Exception as e:
        print(f"[ERROR] Analytics failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/api/reports/summary', methods=['GET'])
@token_required
def get_summary():
    try:
        db = get_db()
        total_tickets = db.query(func.count(Ticket.id)).scalar() or 0
        open_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status == 'open').scalar() or 0
        resolved_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status == 'resolved').scalar() or 0
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_tickets = db.query(func.count(Ticket.id)).filter(Ticket.created_at >= today_start).scalar() or 0
        week_start = datetime.now() - timedelta(days=7)
        week_tickets = db.query(func.count(Ticket.id)).filter(Ticket.created_at >= week_start).scalar() or 0
        
        return jsonify({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'resolved_tickets': resolved_tickets,
            'resolution_rate': round((resolved_tickets / total_tickets * 100), 2) if total_tickets > 0 else 0,
            'today_tickets': today_tickets,
            'week_tickets': week_tickets
        })
    except Exception as e:
        print(f"[ERROR] Summary failed: {str(e)}")
        return jsonify({'error': str(e)}), 500