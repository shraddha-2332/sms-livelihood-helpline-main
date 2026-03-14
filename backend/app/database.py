from app import db
from app.models import Agent, ResponseTemplate
import json
import os

class DatabaseSession:
    """Wrapper to provide db.query() interface"""
    def query(self, *args, **kwargs):
        return db.session.query(*args, **kwargs)

def get_db():
    """Get database session for querying"""
    return DatabaseSession()

def init_default_data():
    """Initialize database with default data"""
    
    # Check if agents exist
    if Agent.query.count() == 0:
        # Create default agents
        default_agents = [
            Agent(
                name='Admin Agent',
                email='admin@helpline.com',
                phone='+919999999999',
                role='admin',
                specialization='general',
                is_active=True
            ),
            Agent(
                name='Agriculture Expert',
                email='agri@helpline.com',
                phone='+919999999998',
                role='agent',
                specialization='agriculture',
                is_active=True
            ),
            Agent(
                name='Loan Advisor',
                email='loan@helpline.com',
                phone='+919999999997',
                role='agent',
                specialization='finance',
                is_active=True
            )
        ]
        
        for agent in default_agents:
            agent.set_password('password123')
            db.session.add(agent)
        
        print("[OK] Created default agents")
    
    # Check if response templates exist
    if ResponseTemplate.query.count() == 0:
        # Load templates from JSON file
        templates_path = os.path.join('data', 'templates', 'response_templates.json')
        
        if os.path.exists(templates_path):
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            for intent, languages in templates_data.items():
                for lang, text in languages.items():
                    template = ResponseTemplate(
                        intent=intent,
                        language=lang,
                        template_text=text,
                        is_active=True
                    )
                    db.session.add(template)
            
            print("[OK] Loaded response templates")
    
    db.session.commit()