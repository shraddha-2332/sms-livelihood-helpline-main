"""
SMS Test Script - Send test messages to the helpline
"""
import requests
import json

# Configuration
API_URL = "http://localhost:8080"
WEBHOOK_ENDPOINT = f"{API_URL}/webhook/sms"

# Test messages with different categories
test_messages = [
    {
        "phone": "+919876543210",
        "text": "I need help finding a job in construction work"
    },
    {
        "phone": "+919876543211",
        "text": "I want to learn new skills. Are there any training programs?"
    },
    {
        "phone": "+919876543212",
        "text": "I need a loan to start a small business"
    },
    {
        "phone": "+919876543213",
        "text": "What government schemes are available for farmers?"
    },
    {
        "phone": "+919876543214",
        "text": "मुझे नौकरी चाहिए"  # Hindi: I need a job
    }
]

def send_sms(phone, text):
    """Send a test SMS to the webhook"""
    payload = {
        "from": phone,
        "text": text
    }
    
    try:
        response = requests.post(WEBHOOK_ENDPOINT, json=payload)
        print(f"📱 Sent from {phone}")
        print(f"   Message: {text[:50]}...")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("-" * 60)
        return response
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("=" * 60)
    print("🚀 SMS Helpline Test Script")
    print("=" * 60)
    print()
    
    # Check webhook status
    try:
        status_response = requests.get(f"{API_URL}/webhook/status")
        print("✅ Webhook Status:")
        print(json.dumps(status_response.json(), indent=2))
        print()
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to webhook: {str(e)}")
        print()
    
    # Send test messages
    print("📨 Sending test messages...")
    print()
    
    for msg in test_messages:
        send_sms(msg["phone"], msg["text"])
    
    print()
    print("✅ Test complete! Check your dashboard for the new tickets.")
    print()
    print("💡 Tip: The messages are processed by the worker in the background.")
    print("   It may take a few seconds for them to appear in the dashboard.")

if __name__ == "__main__":
    main()
