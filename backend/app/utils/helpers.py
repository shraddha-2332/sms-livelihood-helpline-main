import re
from datetime import datetime, timedelta
from typing import Optional

def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format"""
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

def detect_language(text: str) -> str:
    """
    Detect language from text
    Simple detection based on script/characters
    """
    # Check for Devanagari script (Hindi)
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'
    
    # Check for Tamil script
    if re.search(r'[\u0B80-\u0BFF]', text):
        return 'ta'
    
    # Check for Telugu script
    if re.search(r'[\u0C00-\u0C7F]', text):
        return 'te'
    
    # Check for Bengali script
    if re.search(r'[\u0980-\u09FF]', text):
        return 'bn'
    
    # Default to English
    return 'en'

def transliterate_to_latin(text: str, source_lang: str = 'hi') -> str:
    """
    Transliterate Indic script to Latin/English characters
    For better processing by ML models
    """
    # This is a simplified version
    # In production, use libraries like: indic-transliteration, Aksharamukha
    
    # Basic Hindi to Latin mapping (very simplified)
    if source_lang == 'hi':
        # This is just a placeholder
        # In production, use proper transliteration libraries
        return text
    
    return text

def truncate_sms(text: str, max_length: int = 160) -> str:
    """Truncate text to SMS length limit"""
    if len(text) <= max_length:
        return text
    
    # Truncate and add ellipsis
    return text[:max_length-3] + '...'

def calculate_sms_parts(text: str) -> int:
    """Calculate number of SMS parts needed"""
    length = len(text)
    
    # Standard SMS: 160 chars per message
    # Concatenated SMS: 153 chars per message (7 chars for header)
    if length <= 160:
        return 1
    else:
        return (length + 152) // 153

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove potentially dangerous characters
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    return text

def format_datetime(dt: datetime, format_type: str = 'default') -> str:
    """Format datetime for display"""
    if not dt:
        return ''
    
    formats = {
        'default': '%Y-%m-%d %H:%M:%S',
        'date': '%Y-%m-%d',
        'time': '%H:%M:%S',
        'friendly': '%b %d, %Y at %I:%M %p',
        'relative': None  # Special handling
    }
    
    if format_type == 'relative':
        return get_relative_time(dt)
    
    fmt = formats.get(format_type, formats['default'])
    return dt.strftime(fmt)

def get_relative_time(dt: datetime) -> str:
    """Get relative time string (e.g., '2 hours ago')"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    else:
        return dt.strftime('%b %d, %Y')

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """Extract keywords from text"""
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Split into words
    words = text.split()
    
    # Remove common stop words (simplified)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been'}
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequency
    from collections import Counter
    word_freq = Counter(keywords)
    
    # Return top keywords
    return [word for word, count in word_freq.most_common(max_keywords)]

def generate_ticket_id() -> str:
    """Generate unique ticket ID"""
    import uuid
    return str(uuid.uuid4())[:8].upper()

def mask_phone_number(phone: str) -> str:
    """Mask phone number for privacy (e.g., +91XXXXX1234)"""
    if len(phone) < 4:
        return phone
    
    return phone[:3] + 'X' * (len(phone) - 7) + phone[-4:]

def parse_intent_entities(text: str) -> dict:
    """Parse entities from text based on patterns"""
    entities = {}
    
    # Extract amounts/numbers
    amount_pattern = r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees|rs|inr)?'
    amounts = re.findall(amount_pattern, text.lower())
    if amounts:
        entities['amount'] = amounts[0].replace(',', '')
    
    # Extract dates
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    dates = re.findall(date_pattern, text)
    if dates:
        entities['date'] = dates[0]
    
    # Extract phone numbers
    phone_pattern = r'\+?\d[\d\s-]{8,}\d'
    phones = re.findall(phone_pattern, text)
    if phones:
        entities['phone'] = phones[0]
    
    return entities

def calculate_priority(text: str, intent: str, confidence: float) -> str:
    """Calculate ticket priority based on various factors"""
    # Urgent keywords
    urgent_keywords = ['urgent', 'emergency', 'immediately', 'asap', 'critical', 
                       'तुरंत', 'आपातकाल', 'जरूरी']
    
    text_lower = text.lower()
    
    # Check for urgent keywords
    if any(keyword in text_lower for keyword in urgent_keywords):
        return 'urgent'
    
    # High priority intents
    high_priority_intents = ['agriculture_help', 'faq_loan']
    if intent in high_priority_intents and confidence > 0.8:
        return 'high'
    
    # Default to medium
    return 'medium'

def get_response_template(intent: str, language: str = 'en') -> Optional[str]:
    """Get response template for given intent and language"""
    from app.models import ResponseTemplate
    from app import db
    
    template = ResponseTemplate.query.filter_by(
        intent=intent,
        language=language,
        is_active=True
    ).first()
    
    if template:
        return template.template_text
    
    # Fallback to English if language not found
    if language != 'en':
        template = ResponseTemplate.query.filter_by(
            intent=intent,
            language='en',
            is_active=True
        ).first()
        
        if template:
            return template.template_text
    
    return None

def categorize_intent(intent: str) -> str:
    """Map intent to ticket category"""
    intent_category_map = {
        'faq_fertilizer': 'agriculture',
        'agriculture_help': 'agriculture',
        'faq_loan': 'loan',
        'market_price': 'agriculture',
        'job_search': 'job',
        'training': 'training',
        'faq_subsidy': 'agriculture',
        'faq_scheme': 'loan'
    }
    
    return intent_category_map.get(intent, 'other')