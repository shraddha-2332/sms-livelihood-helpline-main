import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import joblib
import os
from app.database import get_db
from app.models import Ticket, Agent, Message
from sqlalchemy import func

class PredictiveAnalytics:
    def __init__(self):
        self.routing_model = None
        self.priority_model = None
        self.resolution_time_model = None
        self.label_encoders = {}
        self.model_dir = 'model'
        
        # Create model directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def train_routing_model(self):
        """Train model to predict best agent for a ticket"""
        db = get_db()
        
        # Get historical data
        tickets = db.query(Ticket).filter(
            Ticket.assigned_to.isnot(None),
            Ticket.status == 'resolved'
        ).all()
        
        if len(tickets) < 10:
            print("Not enough data to train routing model")
            return False
        
        # Prepare features
        X = []
        y = []
        
        for ticket in tickets:
            features = self._extract_ticket_features(ticket)
            X.append(features)
            y.append(ticket.assigned_to)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        self.routing_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.routing_model.fit(X, y)
        
        # Save model
        joblib.dump(self.routing_model, os.path.join(self.model_dir, 'routing_model.joblib'))
        
        print(f"Routing model trained with {len(tickets)} samples")
        return True
    
    def train_priority_model(self):
        """Train model to predict ticket priority"""
        db = get_db()
        
        tickets = db.query(Ticket).filter(
            Ticket.priority.isnot(None)
        ).all()
        
        if len(tickets) < 10:
            print("Not enough data to train priority model")
            return False
        
        X = []
        y = []
        
        # Encode priority labels
        le = LabelEncoder()
        priorities = [t.priority for t in tickets]
        le.fit(priorities)
        self.label_encoders['priority'] = le
        
        for ticket in tickets:
            features = self._extract_ticket_features(ticket)
            X.append(features)
            y.append(ticket.priority)
        
        X = np.array(X)
        y = le.transform(y)
        
        # Train model
        self.priority_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.priority_model.fit(X, y)
        
        # Save model and encoder
        joblib.dump(self.priority_model, os.path.join(self.model_dir, 'priority_model.joblib'))
        joblib.dump(le, os.path.join(self.model_dir, 'priority_encoder.joblib'))
        
        print(f"Priority model trained with {len(tickets)} samples")
        return True
    
    def train_resolution_time_model(self):
        """Train model to predict ticket resolution time"""
        db = get_db()
        
        tickets = db.query(Ticket).filter(
            Ticket.status == 'resolved',
            Ticket.created_at.isnot(None),
            Ticket.updated_at.isnot(None)
        ).all()
        
        if len(tickets) < 10:
            print("Not enough data to train resolution time model")
            return False
        
        X = []
        y = []
        
        for ticket in tickets:
            features = self._extract_ticket_features(ticket)
            X.append(features)
            
            # Calculate resolution time in hours
            delta = ticket.updated_at - ticket.created_at
            resolution_time = delta.total_seconds() / 3600
            y.append(resolution_time)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        self.resolution_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.resolution_time_model.fit(X, y)
        
        # Save model
        joblib.dump(self.resolution_time_model, os.path.join(self.model_dir, 'resolution_time_model.joblib'))
        
        print(f"Resolution time model trained with {len(tickets)} samples")
        return True
    
    def _extract_ticket_features(self, ticket):
        """Extract features from ticket for ML models"""
        db = get_db()
        
        # Intent encoding (simplified)
        intent_map = {
            'employment': 1,
            'training': 2,
            'loan': 3,
            'schemes': 4,
            'other': 5
        }
        intent_feature = intent_map.get(ticket.intent, 5)
        
        # Priority encoding
        priority_map = {'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
        priority_feature = priority_map.get(ticket.priority, 2)
        
        # Hour of day
        hour = ticket.created_at.hour if ticket.created_at else 12
        
        # Day of week
        day_of_week = ticket.created_at.weekday() if ticket.created_at else 0
        
        # Message count
        message_count = db.query(func.count(Message.id)).filter(
            Message.ticket_id == ticket.id
        ).scalar() or 1
        
        # Message length (average)
        messages = db.query(Message).filter(Message.ticket_id == ticket.id).all()
        avg_msg_length = np.mean([len(m.content) for m in messages]) if messages else 50
        
        features = [
            intent_feature,
            priority_feature,
            hour,
            day_of_week,
            message_count,
            avg_msg_length
        ]
        
        return features
    
    def predict_best_agent(self, ticket):
        """Predict the best agent to assign a ticket to"""
        try:
            # Load model if not in memory
            if self.routing_model is None:
                model_path = os.path.join(self.model_dir, 'routing_model.joblib')
                if os.path.exists(model_path):
                    self.routing_model = joblib.load(model_path)
                else:
                    return None
            
            features = self._extract_ticket_features(ticket)
            features = np.array(features).reshape(1, -1)
            
            # Get prediction
            agent_id = self.routing_model.predict(features)[0]
            
            # Get agent workload
            db = get_db()
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            
            if agent:
                # Check agent's current workload
                open_tickets = db.query(func.count(Ticket.id)).filter(
                    Ticket.assigned_to == agent_id,
                    Ticket.status.in_(['open', 'assigned'])
                ).scalar()
                
                return {
                    'agent_id': agent_id,
                    'agent_name': agent.name,
                    'current_workload': open_tickets,
                    'confidence': 'high'
                }
            
            return None
            
        except Exception as e:
            print(f"Error predicting agent: {e}")
            return None
    
    def predict_priority(self, ticket):
        """Predict ticket priority"""
        try:
            # Load model if not in memory
            if self.priority_model is None:
                model_path = os.path.join(self.model_dir, 'priority_model.joblib')
                encoder_path = os.path.join(self.model_dir, 'priority_encoder.joblib')
                
                if os.path.exists(model_path) and os.path.exists(encoder_path):
                    self.priority_model = joblib.load(model_path)
                    self.label_encoders['priority'] = joblib.load(encoder_path)
                else:
                    return 'medium'
            
            features = self._extract_ticket_features(ticket)
            features = np.array(features).reshape(1, -1)
            
            # Get prediction
            priority_encoded = self.priority_model.predict(features)[0]
            priority = self.label_encoders['priority'].inverse_transform([priority_encoded])[0]
            
            return priority
            
        except Exception as e:
            print(f"Error predicting priority: {e}")
            return 'medium'
    
    def predict_resolution_time(self, ticket):
        """Predict ticket resolution time in hours"""
        try:
            # Load model if not in memory
            if self.resolution_time_model is None:
                model_path = os.path.join(self.model_dir, 'resolution_time_model.joblib')
                if os.path.exists(model_path):
                    self.resolution_time_model = joblib.load(model_path)
                else:
                    return None
            
            features = self._extract_ticket_features(ticket)
            features = np.array(features).reshape(1, -1)
            
            # Get prediction
            hours = self.resolution_time_model.predict(features)[0]
            
            return {
                'estimated_hours': round(hours, 2),
                'estimated_completion': (datetime.now() + timedelta(hours=hours)).isoformat()
            }
            
        except Exception as e:
            print(f"Error predicting resolution time: {e}")
            return None
    
    def forecast_ticket_volume(self, days_ahead=7):
        """Forecast ticket volume for the next N days"""
        db = get_db()
        
        # Get historical data (last 30 days)
        start_date = datetime.now() - timedelta(days=30)
        
        daily_counts = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            count = db.query(func.count(Ticket.id)).filter(
                Ticket.created_at >= day_start,
                Ticket.created_at <= day_end
            ).scalar()
            
            daily_counts.append(count)
        
        # Simple moving average forecast
        window_size = 7
        if len(daily_counts) >= window_size:
            recent_avg = np.mean(daily_counts[-window_size:])
        else:
            recent_avg = np.mean(daily_counts) if daily_counts else 0
        
        # Generate forecast
        forecast = []
        for i in range(days_ahead):
            forecast_date = datetime.now() + timedelta(days=i+1)
            
            # Adjust for day of week (weekends typically have less tickets)
            day_of_week = forecast_date.weekday()
            weekday_factor = 0.7 if day_of_week >= 5 else 1.0
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_tickets': int(recent_avg * weekday_factor),
                'confidence_range': [
                    int(recent_avg * weekday_factor * 0.8),
                    int(recent_avg * weekday_factor * 1.2)
                ]
            })
        
        return {
            'forecast': forecast,
            'historical_average': round(recent_avg, 2),
            'trend': 'stable'  # Could be calculated based on recent trends
        }
    
    def get_agent_recommendations(self, ticket):
        """Get top 3 agent recommendations for a ticket"""
        db = get_db()
        
        # Get all agents
        agents = db.query(Agent).all()
        
        if not agents:
            return []
        
        recommendations = []
        
        for agent in agents:
            # Calculate score based on multiple factors
            
            # 1. Workload (lower is better)
            workload = db.query(func.count(Ticket.id)).filter(
                Ticket.assigned_to == agent.id,
                Ticket.status.in_(['open', 'assigned'])
            ).scalar()
            
            workload_score = max(0, 100 - (workload * 10))
            
            # 2. Expertise (based on category)
            expertise_score = 50  # Default
            if ticket.intent:
                category_tickets = db.query(func.count(Ticket.id)).filter(
                    Ticket.assigned_to == agent.id,
                    Ticket.intent == ticket.intent,
                    Ticket.status == 'resolved'
                ).scalar()
                expertise_score = min(100, 50 + (category_tickets * 5))
            
            # 3. Resolution rate
            total_tickets = db.query(func.count(Ticket.id)).filter(
                Ticket.assigned_to == agent.id
            ).scalar()
            
            resolved_tickets = db.query(func.count(Ticket.id)).filter(
                Ticket.assigned_to == agent.id,
                Ticket.status == 'resolved'
            ).scalar()
            
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 50
            
            # Combined score
            total_score = (workload_score * 0.4) + (expertise_score * 0.3) + (resolution_rate * 0.3)
            
            recommendations.append({
                'agent_id': agent.id,
                'agent_name': agent.name,
                'score': round(total_score, 2),
                'current_workload': workload,
                'expertise_level': 'high' if expertise_score > 70 else 'medium' if expertise_score > 40 else 'low',
                'resolution_rate': round(resolution_rate, 2)
            })
        
        # Sort by score and return top 3
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:3]


# Initialize global instance
predictive_analytics = PredictiveAnalytics()