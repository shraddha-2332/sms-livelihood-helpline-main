from app import db
from datetime import datetime
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    language = db.Column(db.String(10), default='en')
    location = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    tickets = db.relationship('Ticket', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'language': self.language,
            'location': json.loads(self.location) if self.location else None,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    direction = db.Column(db.String(10), nullable=False)  # 'in' or 'out'
    text = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    entities = db.Column(db.Text)  # JSON string
    status = db.Column(db.String(20), default='pending')  # pending, processed, sent, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ticket_id': self.ticket_id,
            'direction': self.direction,
            'text': self.text,
            'intent': self.intent,
            'confidence': self.confidence,
            'entities': json.loads(self.entities) if self.entities else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'))
    subject = db.Column(db.String(200))
    category = db.Column(db.String(50))  # agriculture, loan, job, training, other
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, assigned, resolved, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    messages = db.relationship('Message', backref='ticket', lazy='dynamic')
    
    def to_dict(self, include_messages=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'user_phone': self.user.phone if self.user else None,
            'user_name': self.user.name if self.user else None,
            'agent_id': self.agent_id,
            'agent_name': self.agent.name if self.agent else None,
            'subject': self.subject,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'last_message': self.messages.order_by(Message.created_at.desc()).first().text if self.messages.count() > 0 else None
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages.order_by(Message.created_at.asc())]
        
        return data

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='agent')  # admin, supervisor, agent
    specialization = db.Column(db.String(50))  # agriculture, finance, training, general
    is_active = db.Column(db.Boolean, default=True)
    max_concurrent_tickets = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='agent', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        import bcrypt
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'specialization': self.specialization,
            'is_active': self.is_active,
            'max_concurrent_tickets': self.max_concurrent_tickets,
            'active_tickets': self.tickets.filter_by(status='assigned').count(),
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class ResponseTemplate(db.Model):
    __tablename__ = 'response_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    intent = db.Column(db.String(50), nullable=False, index=True)
    language = db.Column(db.String(10), nullable=False)
    template_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'intent': self.intent,
            'language': self.language,
            'template_text': self.template_text,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class VoiceCall(db.Model):
    __tablename__ = 'voice_calls'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # inbound, outbound
    duration = db.Column(db.Integer)  # in seconds
    transcription = db.Column(db.Text)
    intent = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='voice_calls')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phone': self.phone,
            'direction': self.direction,
            'duration': self.duration,
            'transcription': self.transcription,
            'intent': self.intent,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    metric_type = db.Column(db.String(50), nullable=False)  # messages_received, tickets_created, etc.
    metric_value = db.Column(db.Integer, default=0)
    meta_data = db.Column(db.Text)  # JSON string for additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'meta_data': json.loads(self.meta_data) if self.meta_data else None,
            'created_at': self.created_at.isoformat()
        }