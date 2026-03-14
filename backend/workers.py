import os
import sys
import time
import json
import redis
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.utils.redis_client import get_redis_client
from app.models import Message, Ticket, User, Agent
from app.classifier import get_classifier
from app.services.sms_service import send_sms
from app.utils.helpers import (
    detect_language, 
    calculate_priority, 
    get_response_template,
    categorize_intent
)

# Create Flask app context
app = create_app()

# Redis connection
redis_client = get_redis_client(decode_responses=True)

# Get classifier
classifier = get_classifier()

def process_message(payload):
    """Process incoming message"""
    try:
        message_id = payload['message_id']
        user_id = payload['user_id']
        phone = payload['phone']
        text = payload['text']
        
        print(f"\n{'='*60}")
        print(f"🔄 Processing message {message_id} from {phone}")
        print(f"📝 Text: {text}")
        
        with app.app_context():
            # Get message from database
            message = db.session.get(Message, message_id)
            if not message:
                print(f"❌ Message {message_id} not found")
                return
            
            # Get user
            user = db.session.get(User, user_id)
            
            # Detect language if not set
            if not user.language or user.language == 'en':
                detected_lang = detect_language(text)
                user.language = detected_lang
                print(f"🌍 Detected language: {detected_lang}")
            
            # Classify intent
            intent, confidence, entities = classifier.classify(text)
            
            print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")
            print(f"📊 Entities: {entities}")
            
            # Update message
            message.intent = intent
            message.confidence = confidence
            message.entities = json.dumps(entities) if entities else None
            message.processed_at = datetime.utcnow()
            
            # Determine if auto-reply or ticket creation
            auto_reply_threshold = 0.7
            
            if confidence >= auto_reply_threshold and intent != 'unknown':
                # Auto-reply
                print(f"🤖 Auto-replying (confidence >= {auto_reply_threshold})")
                
                # Get response template
                response_text = get_response_template(intent, user.language)
                
                if response_text:
                    # Send response
                    success = send_sms(phone, response_text)
                    
                    # Create outbound message
                    outbound_msg = Message(
                        user_id=user_id,
                        direction='out',
                        text=response_text,
                        status='sent' if success else 'failed',
                        processed_at=datetime.utcnow()
                    )
                    db.session.add(outbound_msg)
                    
                    message.status = 'processed'
                    
                    print(f"✅ Auto-reply sent: {response_text[:50]}...")
                else:
                    print(f"⚠️  No template found for {intent}/{user.language}")
                    create_ticket_for_message(message, user, intent, confidence)
            else:
                # Create ticket for agent
                print(f"🎫 Creating ticket (confidence < {auto_reply_threshold} or unknown intent)")
                create_ticket_for_message(message, user, intent, confidence)
            
            db.session.commit()
            print(f"✅ Message {message_id} processed successfully")
            print(f"{'='*60}\n")
            
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()

def create_ticket_for_message(message, user, intent, confidence):
    """Create a ticket for agent handling"""
    try:
        # Check if user has an open ticket
        existing_ticket = Ticket.query.filter_by(
            user_id=user.id,
            status='open'
        ).first()
        
        if existing_ticket:
            # Add message to existing ticket
            message.ticket_id = existing_ticket.id
            existing_ticket.updated_at = datetime.utcnow()
            print(f"📎 Added to existing ticket #{existing_ticket.id}")
        else:
            # Create new ticket
            category = categorize_intent(intent)
            priority = calculate_priority(message.text, intent, confidence)
            
            ticket = Ticket(
                user_id=user.id,
                subject=message.text[:100] if len(message.text) > 100 else message.text,
                category=category,
                priority=priority,
                status='open'
            )
            db.session.add(ticket)
            db.session.flush()
            
            message.ticket_id = ticket.id
            
            print(f"🎫 Created new ticket #{ticket.id} (category: {category}, priority: {priority})")
            
            # Try to auto-assign to available agent
            assign_ticket_to_agent(ticket, category)
        
        message.status = 'processed'
        
    except Exception as e:
        print(f"❌ Error creating ticket: {str(e)}")
        raise

def assign_ticket_to_agent(ticket, category):
    """Auto-assign ticket to available agent"""
    try:
        # Find available agent with matching specialization
        agents = Agent.query.filter_by(
            is_active=True
        ).filter(
            (Agent.specialization == category) | 
            (Agent.specialization == 'general')
        ).all()
        
        for agent in agents:
            # Check capacity
            active_tickets = Ticket.query.filter_by(
                agent_id=agent.id,
                status='assigned'
            ).count()
            
            if active_tickets < agent.max_concurrent_tickets:
                ticket.agent_id = agent.id
                ticket.status = 'assigned'
                print(f"👤 Assigned to agent: {agent.name}")
                return
        
        print(f"⚠️  No available agent found")
        
    except Exception as e:
        print(f"❌ Error assigning agent: {str(e)}")

def worker_loop():
    """Main worker loop"""
    print("🚀 Starting SMS Worker")
    print(f"📡 Connected to Redis: {redis_client.ping()}")
    print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("⏳ Waiting for messages...\n")
    
    while True:
        try:
            # Blocking pop from queue (timeout: 5 seconds)
            item = redis_client.brpop('incoming_sms', timeout=5)
            
            if item:
                queue_name, payload_json = item
                payload = json.loads(payload_json)
                
                # Process message
                process_message(payload)
            else:
                # No message, just wait
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Worker stopped by user")
            break
        except Exception as e:
            print(f"❌ Worker error: {str(e)}")
            import traceback
            traceback.print_exc()
            time.sleep(5)  # Wait before retrying

if __name__ == '__main__':
    worker_loop()
