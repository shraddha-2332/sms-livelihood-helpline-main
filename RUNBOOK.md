## Runbook

This guide covers local development and containerized deployment for the SMS Livelihood Helpline.

---

### 1. Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Redis (local or container)
- SQLite (bundled) or PostgreSQL if configured
- Docker + Docker Compose (optional but recommended)

Copy `.env.example` files if available or set the required variables (DB URL, JWT secret, SMS credentials, Redis host/port, etc.).

---

### 2. Backend (Flask API)
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows
# or source .venv/bin/activate on Linux/macOS
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=8080
```

Helpful scripts:
- `python train_model.py` – retrain ML classifiers
- `python workers.py` – start background workers (queues, predictions)

Ensure Redis is running and `REDIS_HOST/PORT` match your environment.

---

### 3. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
By default Vite serves on `http://localhost:5173`. Update API base URLs (e.g., via `VITE_API_URL`) if your backend isn’t on `http://localhost:8080`.

To build for production:
```bash
npm run build
npm run preview
```

---

### 4. Docker Compose
```bash
docker-compose up --build
```
The compose file defines services for the Flask API, frontend, database, and Redis. Adjust exposed ports or volumes as needed.

To stop and clean resources:
```bash
docker-compose down -v
```

---

### 5. Health Checks
- API: `GET http://localhost:8080/health`
- Webhook queue: `GET http://localhost:8080/webhook/status`
- Frontend: open `http://localhost:5173`

Troubleshooting tips:
- Check Flask logs for stack traces.
- Verify DB migrations/table creation via `backend/app/__init__.py` (runs `db.create_all()`).
- Use browser dev tools for failing API calls (CORS, auth errors, etc.).

---

### 6. Data & Models
- Seed data lives in `data/`. Update CSVs to retrain or demo specific scenarios.
- Model artifacts are stored in `model/` (git-tracked for convenience). Regenerate via `train_model.py` when datasets change.

---

For architectural context and feature overview, read `PROJECT_OVERVIEW.md`.

