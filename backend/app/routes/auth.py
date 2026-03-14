from flask import Blueprint, request, jsonify
from app import db
from app.models import Agent
from datetime import datetime, timedelta
import jwt
import os

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT token generation (should be in environment variables in production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

def generate_token(agent_id):
    """Generate JWT token for agent"""
    payload = {
        'agent_id': agent_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return agent_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['agent_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new agent"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if '@' not in data['email']:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password length
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if email already exists
        existing = Agent.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create agent
        agent = Agent(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            role=data.get('role', 'agent'),
            specialization=data.get('specialization', 'general'),
            max_concurrent_tickets=data.get('max_concurrent_tickets', 10),
            is_active=True
        )
        
        # Set password
        agent.set_password(data['password'])
        
        db.session.add(agent)
        db.session.commit()
        
        # Generate token
        token = generate_token(agent.id)
        
        print(f"[OK] Agent registered: {agent.email}")
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'agent': agent.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error registering agent: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login an agent"""
    try:
        data = request.get_json()
        
        # Validation
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find agent
        agent = Agent.query.filter_by(email=data['email']).first()
        
        if not agent:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if agent is active
        if not agent.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if not agent.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        agent.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(agent.id)
        
        print(f"[OK] Agent logged in: {agent.email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error during login: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout an agent (client-side token removal)"""
    # JWT is stateless, so logout is handled client-side by removing the token
    # This endpoint exists for consistency and future session management
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_agent():
    """Get current authenticated agent's information"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        # Extract token (format: "Bearer <token>")
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        token = parts[1]
        
        # Verify token
        agent_id = verify_token(token)
        
        if not agent_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get agent
        agent = Agent.query.get(agent_id)
        
        if not agent:
           return jsonify({'error': 'Agent not found'}), 404
        
        if not agent.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        return jsonify(agent.to_dict()), 200
        
    except Exception as e:
        print(f"[ERROR] Error getting current agent: {str(e)}")
        return jsonify({'error': 'Failed to get agent information'}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Verify if a token is valid"""
    try:
        data = request.get_json()
        
        if 'token' not in data:
            return jsonify({'valid': False, 'error': 'Token is required'}), 400
        
        agent_id = verify_token(data['token'])
        
        if not agent_id:
            return jsonify({'valid': False}), 200
        
        agent = Agent.query.get(agent_id)
        
        if not agent or not agent.is_active:
            return jsonify({'valid': False}), 200
        
        return jsonify({
            'valid': True,
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error verifying token: {str(e)}")
        return jsonify({'valid': False, 'error': str(e)}), 500
