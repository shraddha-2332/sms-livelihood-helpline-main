import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///helpline.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = 0
    
    # SMS Configuration
    SMS_PROVIDER = os.environ.get('SMS_PROVIDER') or 'mock'
    SMS_API_KEY = os.environ.get('SMS_API_KEY') or ''
    SMS_SENDER_ID = os.environ.get('SMS_SENDER_ID') or 'HELPLINE'
    
    # Voice Configuration
    VOICE_ENABLED = os.environ.get('VOICE_ENABLED', 'false').lower() == 'true'
    
    # Application Settings
    MAX_MESSAGE_LENGTH = 160
    AUTO_REPLY_CONFIDENCE_THRESHOLD = 0.7
    TICKET_AUTO_CLOSE_DAYS = 7
    
    # Supported Languages
    SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te', 'bn']
    DEFAULT_LANGUAGE = 'en'