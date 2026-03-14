from flask import Blueprint, request, jsonify
from app import db
from app.models import VoiceCall, User, Message, Ticket
from app.services.voice_service import process_voice_input, text_to_speech
from datetime import datetime
import base64
import os

voice_bp = Blueprint('voice', __name__)

@voice_bp.route('/process', methods=['POST'])
def process_voice():
    """
    Process voice input (speech-to-text conversion)
    Accepts audio file or base64 encoded audio
    """
    try:
        data = request.get_json() if request.is_json else {}
        
        # Get phone number
        phone = data.get('phone') or data.get('from')
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        # Get audio data
        audio_data = None
        if 'audio_base64' in data:
            audio_data = base64.b64decode(data['audio_base64'])
        elif request.files and 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
        
        if not audio_data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Get or create user
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, language='en')
            db.session.add(user)
            db.session.flush()
        
        # Create voice call record
        voice_call = VoiceCall(
            user_id=user.id,
            phone=phone,
            direction='inbound',
            status='processing'
        )
        db.session.add(voice_call)
        db.session.commit()
        
        demo_mode = request.args.get('demo') in ('1', 'true', 'yes') or os.environ.get('DEMO_MODE', 'false').lower() == 'true'
        
        # Process voice to text (mock implementation)
        # In production, integrate with Google Speech-to-Text, Azure Speech, or Whisper
        transcription, duration = process_voice_input(audio_data, user.language)
        
        if demo_mode and not transcription:
            transcription = 'Demo voice message: I need information about loans for farmers.'
            duration = max(1, int(len(audio_data) / 8000))
        
        if not transcription:
            voice_call.status = 'failed'
            db.session.commit()
            return jsonify({
                'error': 'Failed to transcribe audio',
                'voice_call_id': voice_call.id
            }), 500
        
        # Update voice call record
        voice_call.transcription = transcription
        voice_call.duration = duration
        voice_call.status = 'completed'
        
        # Create message from transcription
        demo_intent_map = {
            'loan': 'loan_query',
            'training': 'training_query',
            'scheme': 'scheme_query',
            'job': 'job_query',
            'agri': 'agri_support'
        }
        lower_text = transcription.lower()
        demo_intent = None
        for key, val in demo_intent_map.items():
            if key in lower_text:
                demo_intent = val
                break

        message = Message(
            user_id=user.id,
            direction='in',
            text=transcription,
            status='pending',
            intent=demo_intent,
            confidence=0.8 if demo_intent else None
        )
        db.session.add(message)
        db.session.commit()
        
        if demo_mode:
            # Create ticket immediately (no worker required)
            ticket = Ticket(
                user_id=user.id,
                subject=transcription[:100],
                category='general',
                priority='medium',
                status='open'
            )
            db.session.add(ticket)
            db.session.flush()
            message.ticket_id = ticket.id
            message.status = 'processed'
            db.session.commit()
        else:
            # Queue for processing (similar to SMS)
            import redis
            from app.utils.redis_client import get_redis_client
            import json
            
            redis_client = get_redis_client(decode_responses=True)
            
            queue_data = {
                'message_id': message.id,
                'user_id': user.id,
                'phone': phone,
                'text': transcription,
                'source': 'voice',
                'timestamp': datetime.utcnow().isoformat()
            }
            redis_client.lpush('incoming_sms', json.dumps(queue_data))
        
        return jsonify({
            'status': 'success',
            'voice_call_id': voice_call.id,
            'message_id': message.id,
            'transcription': transcription,
            'duration': duration
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error processing voice: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """
    Convert text to speech
    Returns audio data or URL
    """
    try:
        data = request.get_json()
        
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        language = data.get('language', 'en')
        
        # Generate speech (mock implementation)
        # In production, integrate with Google TTS, Azure TTS, or Amazon Polly
        audio_data, audio_format = text_to_speech(text, language)
        
        if not audio_data:
            return jsonify({'error': 'Failed to synthesize speech'}), 500
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'audio_base64': audio_base64,
            'format': audio_format,
            'text': text,
            'language': language
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error synthesizing speech: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/calls', methods=['GET'])
def get_voice_calls():
    """Get voice call history"""
    try:
        user_id = request.args.get('user_id')
        phone = request.args.get('phone')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        query = VoiceCall.query
        
        if user_id:
            query = query.filter_by(user_id=int(user_id))
        if phone:
            query = query.filter_by(phone=phone)
        
        query = query.order_by(VoiceCall.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        calls = [call.to_dict() for call in pagination.items]
        
        return jsonify({
            'calls': calls,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting voice calls: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/calls/<int:call_id>', methods=['GET'])
def get_voice_call(call_id):
    """Get specific voice call details"""
    try:
        call = VoiceCall.query.get(call_id)
        
        if not call:
            return jsonify({'error': 'Voice call not found'}), 404
        
        return jsonify(call.to_dict()), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting voice call: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/webhook/incoming', methods=['POST'])
def voice_webhook():
    """
    Webhook for incoming voice calls from telephony provider
    Compatible with Twilio, Vonage, etc.
    """
    try:
        # Get data from webhook
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        phone = data.get('From') or data.get('from') or data.get('caller')
        call_sid = data.get('CallSid') or data.get('call_id')
        
        if not phone:
            return jsonify({'error': 'Missing phone number'}), 400
        
        # Get or create user
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, language='en')
            db.session.add(user)
            db.session.flush()
        
        # Create voice call record
        voice_call = VoiceCall(
            user_id=user.id,
            phone=phone,
            direction='inbound',
            status='ringing'
        )
        db.session.add(voice_call)
        db.session.commit()
        
        # Return TwiML response (for Twilio)
        # In production, customize based on your telephony provider
        response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="hi-IN">Swagat hai. Apka sandesh record ho raha hai. Beep ke baad bolna shuru karein.</Say>
    <Record maxLength="60" transcribe="true" transcribeCallback="/api/voice/transcribe/{voice_call.id}"/>
    <Say language="hi-IN">Dhanyavaad. Ek agent jaldi hi aapse sampark karenge.</Say>
</Response>'''
        
        return response, 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error in voice webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/transcribe/<int:call_id>', methods=['POST'])
def handle_transcription(call_id):
    """Handle transcription callback from telephony provider"""
    try:
        call = VoiceCall.query.get(call_id)
        
        if not call:
            return jsonify({'error': 'Voice call not found'}), 404
        
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        transcription = data.get('TranscriptionText') or data.get('transcription')
        duration = data.get('RecordingDuration') or data.get('duration')
        
        if transcription:
            call.transcription = transcription
            call.duration = int(duration) if duration else None
            call.status = 'completed'
            
            # Create message from transcription
            message = Message(
                user_id=call.user_id,
                direction='in',
                text=transcription,
                status='pending'
            )
            db.session.add(message)
            
            # Queue for processing
            import redis
            from app.utils.redis_client import get_redis_client
            import json
            import os
            
            redis_client = get_redis_client(decode_responses=True)
            
            queue_data = {
                'message_id': message.id,
                'user_id': call.user_id,
                'phone': call.phone,
                'text': transcription,
                'source': 'voice',
                'timestamp': datetime.utcnow().isoformat()
            }
            redis_client.lpush('incoming_sms', json.dumps(queue_data))
            
            db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error handling transcription: {str(e)}")
        return jsonify({'error': str(e)}), 500
