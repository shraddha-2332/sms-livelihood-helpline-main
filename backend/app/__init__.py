from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from app.config import Config
import os
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/webhook/*": {"origins": "*"}})
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes.webhook import webhook_bp
    from app.routes.tickets import tickets_bp
    from app.routes.agents import agents_bp
    from app.routes.analytics import analytics_bp
    from app.routes.voice import voice_bp
    from app.routes.auth import auth_bp
    from app.routes.report import reports_bp
    
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(reports_bp)
    
    # Create tables (best-effort to avoid race on startup)
    with app.app_context():
        try:
            db.create_all()
        except OperationalError as exc:
            # If another process created tables first, ignore and continue
            if "already exists" not in str(exc):
                raise
        # Initialize default data
        from app.database import init_default_data
        init_default_data()
    
    @app.route('/')
    def index():
        return {
            'status': 'running',
            'message': 'SMS Livelihood Helpline API',
            'version': '1.0.0'
        }
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app
