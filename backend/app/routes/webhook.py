from flask import Blueprint, request, jsonify
from app import db
from app.utils.redis_client import get_redis_client
from app.models import User, Message
import redis
import json
import hashlib
import os
from datetime import datetime

webhook_bp = Blueprint('webhook', __name__)

# Redis connection
redis_client = get_redis_client(decode_responses=True)

def hash_text(text):
    """Generate hash for deduplication"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

@webhook_bp.route('/sms', methods=['POST'])
def receive_sms():
    """
    Webhook endpoint to receive incoming SMS messages
    Supports multiple SMS gateway formats
    """
    try:
        # Get payload from JSON or form data
        if request.is_json:
            payload = request.get_json()
        else:
            payload = request.form.to_dict()
        
        # Extract phone number (supports multiple gateway formats)
        phone = (
            payload.get('from') or 
            payload.get('From') or
            payload.get('msisdn') or 
            payload.get('sender') or
            payload.get('phone')
        )
        
        # Extract message text
        text = (
            payload.get('text') or 
            payload.get('Text') or
            payload.get('body') or 
            payload.get('Body') or
            payload.get('message') or
            ''
        )
        
        # Validation
        if not phone:
            return jsonify({
                'error': 'Missing phone number',
                'status': 'failed'
            }), 400
        
        if not text:
            return jsonify({
                'error': 'Missing message text',
                'status': 'failed'
            }), 400
        
        # Normalize phone number
        phone = normalize_phone(phone)
        
        # Deduplication check
        dedup_key = f"msg:{phone}:{hash_text(text)}"
        if redis_client.setnx(dedup_key, 1):
            redis_client.expire(dedup_key, 60)  # 60 seconds dedup window
        else:
            return jsonify({
                'status': 'duplicate',
                'message': 'Message already received'
            }), 200
        
        # Get or create user
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, language='en')
            db.session.add(user)
            db.session.flush()
        else:
            user.last_active = datetime.utcnow()
        
        # Create message record
        message = Message(
            user_id=user.id,
            direction='in',
            text=text,
            status='pending'
        )
        db.session.add(message)
        db.session.commit()
        
        # Queue for processing
        queue_data = {
            'message_id': message.id,
            'user_id': user.id,
            'phone': phone,
            'text': text,
            'timestamp': datetime.utcnow().isoformat()
        }
        redis_client.lpush('incoming_sms', json.dumps(queue_data))
        
        return jsonify({
            'status': 'queued',
            'message_id': message.id,
            'user_id': user.id
        }), 202
        
    except Exception as e:
        print(f"[ERROR] Error in SMS webhook: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'failed'
        }), 500

@webhook_bp.route('/status', methods=['GET'])
def webhook_status():
    """Check webhook health and queue status"""
    try:
        queue_length = redis_client.llen('incoming_sms')
        
        return jsonify({
            'status': 'healthy',
            'queue_length': queue_length,
            'redis_connected': redis_client.ping()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

def normalize_phone(phone):
    """Normalize phone number format"""
    # Remove all non-numeric characters except +
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Ensure it starts with +
    if not phone.startswith('+'):
        # Assume India (+91) if no country code
        if len(phone) == 10:
            phone = '+91' + phone
        else:
            phone = '+' + phone
    
    return phone
