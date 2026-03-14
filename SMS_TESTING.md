# SMS Testing Guide

## 📱 How to Send Test SMS Messages

You have **3 easy options** to send test SMS messages to your helpline system:

---

## Option 1: PowerShell Script (Easiest for Windows) ⭐

Simply double-click `test_sms.ps1` or run:

```powershell
.\test_sms.ps1
```

This will automatically send 5 test messages with different categories (employment, training, loans, schemes).

---

## Option 2: Python Script

1. Make sure you have `requests` library installed:
   ```bash
   pip install requests
   ```

2. Run the script:
   ```bash
   python test_sms.py
   ```

---

## Option 3: Manual cURL (For Custom Messages)

Send a single message using cURL in PowerShell:

```powershell
curl -X POST http://localhost:8080/webhook/sms `
  -H "Content-Type: application/json" `
  -d '{\"from\": \"+919876543210\", \"text\": \"Your custom message here\"}'
```

Or using Invoke-RestMethod:

```powershell
$body = @{
    from = "+919876543210"
    text = "I need help finding a job"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/webhook/sms" -Method POST -Body $body -ContentType "application/json"
```

---

## 🔍 What Happens When You Send a Message?

1. **Message Received**: The webhook endpoint receives your SMS
2. **User Created/Updated**: System creates or updates the user record
3. **Queued for Processing**: Message is added to Redis queue
4. **AI Classification**: Worker processes the message and classifies the intent (employment, training, loan, schemes, etc.)
5. **Ticket Created**: A ticket is created and assigned to an agent
6. **Dashboard Updated**: The ticket appears in your dashboard

---

## 📊 Check Status

To verify the system is working:

```powershell
curl http://localhost:8080/webhook/status
```

This shows:
- Webhook health status
- Redis connection status
- Current queue length

---

## 🎯 Test Message Examples

### Employment Related
```
"I need a job"
"Looking for construction work"
"Help me find employment opportunities"
```

### Training Related
```
"I want to learn new skills"
"Are there any training programs?"
"Computer training courses"
```

### Loan Related
```
"I need a loan for my business"
"Microfinance options available?"
"How to get agricultural loan"
```

### Schemes Related
```
"What government schemes are available?"
"Farmer welfare programs"
"Benefits for women entrepreneurs"
```

---

## 🐛 Troubleshooting

### "Could not connect to webhook"
- Make sure Docker containers are running: `docker-compose ps`
- Check if backend is accessible: `curl http://localhost:8080/health`

### "Messages not appearing in dashboard"
- Check worker logs: `docker-compose logs worker`
- Wait a few seconds - processing happens in background
- Refresh the dashboard

### "Queue building up"
- Check worker is running: `docker-compose logs worker`
- Restart worker: `docker-compose restart worker`

---

## 📝 Notes

- Phone numbers are automatically normalized to international format
- Duplicate messages (same phone + same text within 60 seconds) are rejected
- Messages are processed asynchronously by background workers
- The ML model classifies messages into categories automatically

Happy Testing! 🚀
