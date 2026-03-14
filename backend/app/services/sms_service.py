import os
import requests
from app.config import Config

def send_sms(phone: str, text: str) -> bool:
    """
    Send SMS using configured provider
    Returns True if successful, False otherwise
    """
    provider = Config.SMS_PROVIDER
    
    if provider == 'mock':
        return send_mock_sms(phone, text)
    elif provider == 'twilio':
        return send_twilio_sms(phone, text)
    elif provider == 'msg91':
        return send_msg91_sms(phone, text)
    else:
        print(f"[WARN]  Unknown SMS provider: {provider}")
        return send_mock_sms(phone, text)

def send_mock_sms(phone: str, text: str) -> bool:
    """
    Mock SMS sender for development/testing
    Just logs the SMS instead of actually sending
    """
    print(f"📱 [MOCK SMS] To: {phone}")
    print(f"   Message: {text}")
    print(f"   Length: {len(text)} chars")
    return True

def send_twilio_sms(phone: str, text: str) -> bool:
    """
    Send SMS using Twilio
    Requires: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
    """
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_phone]):
            print("[WARN]  Twilio credentials not configured")
            return send_mock_sms(phone, text)
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=text,
            from_=from_phone,
            to=phone
        )
        
        print(f"[OK] Twilio SMS sent: {message.sid}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Twilio SMS failed: {str(e)}")
        return False

def send_msg91_sms(phone: str, text: str) -> bool:
    """
    Send SMS using MSG91 (popular in India)
    Requires: MSG91_AUTH_KEY, MSG91_SENDER_ID
    """
    try:
        auth_key = os.environ.get('MSG91_AUTH_KEY')
        sender_id = os.environ.get('MSG91_SENDER_ID', Config.SMS_SENDER_ID)
        
        if not auth_key:
            print("[WARN]  MSG91 credentials not configured")
            return send_mock_sms(phone, text)
        
        url = "https://api.msg91.com/api/v5/flow/"
        
        payload = {
            "flow_id": os.environ.get('MSG91_FLOW_ID'),
            "sender": sender_id,
            "mobiles": phone.replace('+91', ''),
            "message": text
        }
        
        headers = {
            "authkey": auth_key,
            "content-type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"[OK] MSG91 SMS sent to {phone}")
            return True
        else:
            print(f"[ERROR] MSG91 SMS failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] MSG91 SMS failed: {str(e)}")
        return False

def send_bulk_sms(recipients: list, text: str) -> dict:
    """
    Send SMS to multiple recipients
    Returns dict with success/failure counts
    """
    results = {
        'success': 0,
        'failed': 0,
        'total': len(recipients)
    }
    
    for phone in recipients:
        if send_sms(phone, text):
            results['success'] += 1
        else:
            results['failed'] += 1
    
    return results

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    import re
    
    # Remove all non-numeric characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Check if it's a valid format
    # Should be +[country code][number] with 10-15 digits total
    pattern = r'^\+\d{10,15}$'
    
    return bool(re.match(pattern, cleaned))

def format_sms_message(template: str, variables: dict) -> str:
    """
    Format SMS message using template and variables
    Example: "Hello {name}, your balance is {amount}" with {'name': 'John', 'amount': '100'}
    """
    try:
        return template.format(**variables)
    except KeyError as e:
        print(f"[WARN]  Missing template variable: {e}")
        return template
