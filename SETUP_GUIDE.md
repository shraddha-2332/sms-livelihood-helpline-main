# 🚀 Setup Guide - SMS Livelihood Support Helpline

Hey there! 👋 This guide will help you get the SMS Livelihood Support Helpline running on your laptop step by step.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker - Recommended)](#quick-start-docker---recommended)
3. [Manual Setup (Without Docker)](#manual-setup-without-docker)
4. [Accessing the Application](#accessing-the-application)
5. [Testing the System](#testing-the-system)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

Before you start, make sure you have these installed on your laptop:

### Required Software

1. **Git** - To clone the repository
   - Download: https://git-scm.com/downloads
   - Verify installation: `git --version`

2. **Docker Desktop** (Recommended Method)
   - Download: https://www.docker.com/products/docker-desktop
   - Verify installation: `docker --version` and `docker-compose --version`
   - Make sure Docker Desktop is running!

**OR** (if you don't want to use Docker):

3. **Python 3.10 or higher**
   - Download: https://www.python.org/downloads/
   - Verify installation: `python --version` or `python3 --version`

4. **Node.js 18 or higher** (includes npm)
   - Download: https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`

5. **Redis** (for background tasks)
   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Or use Docker: `docker run -p 6379:6379 redis:7-alpine`

---

## Quick Start (Docker - Recommended)

This is the easiest way to get everything running! 🎯

### Step 1: Clone the Repository

```bash
git clone https://github.com/pratikjadhav8900/sms-livelihood-helpline.git
cd sms-livelihood-helpline
```

### Step 2: Configure Environment Variables

Copy the example environment file:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

**Optional:** Edit `.env` file if you want to customize settings (but default values work fine for local development!)

### Step 3: Start All Services

```bash
docker-compose up --build
```

This single command will:
- ✅ Start Redis (message queue)
- ✅ Build and start the Backend (Flask API)
- ✅ Build and start the Frontend (React app)
- ✅ Start Background Workers (for processing SMS)

**Note:** First time will take 5-10 minutes to download and build everything. Grab a coffee! ☕

### Step 4: Wait for Services to Start

You'll see logs from all services. Wait until you see:

```
backend_1   | * Running on http://0.0.0.0:8080
frontend_1  | VITE ready in XXX ms
worker_1    | Worker started successfully
```

### Step 5: Access the Application

- **Frontend Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8080

---

## Manual Setup (Without Docker)

If you prefer not to use Docker, follow these steps:

### Step 1: Clone the Repository

```bash
git clone https://github.com/pratikjadhav8900/sms-livelihood-helpline.git
cd sms-livelihood-helpline
```

### Step 2: Setup Backend

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Go back to root directory
cd ..
```

### Step 3: Setup Frontend

Open a **NEW terminal window** (keep the backend terminal open):

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Go back to root directory
cd ..
```

### Step 4: Start Redis

Open a **NEW terminal window**:

```bash
# If you installed Redis locally:
redis-server

# OR if using Docker:
docker run -p 6379:6379 redis:7-alpine
```

### Step 5: Configure Environment

Copy the example environment file:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

### Step 6: Start Backend

In the backend terminal (with virtual environment activated):

```bash
cd backend
set FLASK_APP=app
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=8080
```

### Step 7: Start Background Worker

Open a **NEW terminal window**, activate the virtual environment:

```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac
python workers.py
```

### Step 8: Start Frontend

In the frontend terminal:

```bash
cd frontend
npm run dev
```

---

## Accessing the Application

Once everything is running:

### 🌐 Web Dashboard (Frontend)
- **URL**: http://localhost:3001 (Docker) or http://localhost:5173 (manual setup)
- This is where agents manage tickets and respond to SMS

### 🔧 API Backend
- **URL**: http://localhost:8080
- Health check: http://localhost:8080/health

### 📱 Default Login Credentials

The system creates default admin accounts on first run:

```
Email: admin@helpline.com
Password: admin123

Email: agent1@helpline.com
Password: agent123
```

**⚠️ Important:** Change these passwords in production!

---

## Testing the System

### Option 1: Using PowerShell Script (Windows)

```powershell
.\send_test_sms.ps1
```

This script will:
1. Send a test SMS to the system
2. Create a ticket automatically
3. Show it in the dashboard

### Option 2: Manual API Testing

Send a test SMS via API:

```bash
# Using curl
curl -X POST http://localhost:8080/webhook/incoming \
  -H "Content-Type: application/json" \
  -d "{\"from\": \"+1234567890\", \"body\": \"I need help with loan application\"}"
```

```powershell
# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8080/webhook/incoming" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"from": "+1234567890", "body": "I need help with loan application"}'
```

### Option 3: Using Python Script

```bash
python test_sms.py
```

### Verify it Worked

1. Go to http://localhost:3001
2. Login with default credentials
3. You should see a new ticket in the dashboard!

---

## Common Issues & Solutions

### ❌ "Port already in use" Error

**Problem:** Another service is using the required port.

**Solution:**
```bash
# Stop existing containers
docker-compose down

# Or kill the process using the port (Windows)
netstat -ano | findstr :8080
taskkill /PID <PID_NUMBER> /F

# Or kill the process using the port (Linux/Mac)
lsof -ti:8080 | xargs kill -9
```

### ❌ Docker containers won't start

**Problem:** Docker Desktop not running or out of memory.

**Solutions:**
1. Make sure Docker Desktop is running
2. In Docker Desktop settings, allocate more memory (minimum 4GB recommended)
3. Try: `docker-compose down -v` then `docker-compose up --build`

### ❌ "Module not found" errors (Python)

**Problem:** Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
cd backend
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### ❌ Frontend shows "Network Error" or "Cannot connect to backend"

**Problem:** Backend not running or wrong API URL.

**Solutions:**
1. Check backend is running: http://localhost:8080/health
2. Check frontend `.env.development.local` has correct API URL:
   ```
   VITE_API_URL=http://localhost:8080
   ```
3. Restart frontend: `npm run dev`

### ❌ Redis connection errors

**Problem:** Redis not running.

**Solution:**
```bash
# Check if Redis is running (Docker method)
docker ps | grep redis

# Start Redis if not running
docker run -p 6379:6379 redis:7-alpine

# Or if using Docker Compose
docker-compose up redis
```

### ❌ Database errors / No tables found

**Problem:** Database not initialized.

**Solution:**
The database tables are created automatically on first run. But if you face issues:

```bash
cd backend
python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### ❌ "Permission Denied" errors (Linux/Mac)

**Solution:**
```bash
# Make scripts executable
chmod +x send_test_sms.ps1
chmod +x test_sms.py
```

---

## 🎯 Quick Reference

### Stop Services

**Docker:**
```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

**Manual Setup:**
- Press `Ctrl+C` in each terminal window

### View Logs

**Docker:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs worker

# Follow logs in real-time
docker-compose logs -f
```

### Restart Services

**Docker:**
```bash
docker-compose restart
```

### Clean Start

```bash
# Remove everything and start fresh
docker-compose down -v
docker-compose up --build
```

---

## 📚 Additional Documentation

- **Project Overview**: See `README.md` for high-level description
- **Detailed Runbook**: See `RUNBOOK.md` for advanced operations
- **SMS Testing Guide**: See `SMS_TESTING.md` for testing SMS functionality

---

## 🆘 Need Help?

If you're stuck:

1. Check the **Common Issues** section above
2. Look at the logs for error messages:
   - Docker: `docker-compose logs`
   - Manual: Check each terminal window
3. Make sure all prerequisites are installed correctly
4. Try a clean restart: `docker-compose down -v && docker-compose up --build`

---

## 🎉 Success Checklist

✅ Docker Desktop is running (if using Docker)  
✅ Repository cloned successfully  
✅ All services started without errors  
✅ Frontend accessible at http://localhost:3001  
✅ Backend health check responds  
✅ Able to login with default credentials  
✅ Test SMS creates a ticket in dashboard  

**Congratulations! You're all set! 🚀**

---

**Built with ❤️ for Rural India**

*Bridging the Digital Divide, One SMS at a Time*
