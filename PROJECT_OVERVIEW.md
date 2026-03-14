## SMS Livelihood Helpline

This project provides a full-stack platform for managing inbound livelihood-support requests submitted over SMS (and optionally future channels). It equips agents with dashboards to triage tickets, view analytics, and generate reports.

### Key Capabilities
- Ticket lifecycle management with agent assignment, prioritization, and resolution tracking.
- Analytics APIs (`/api/analytics/*`) that power dashboards with trends, intent distribution, agent performance, and predictive insights.
- Reporting suite with CSV export, date-range filters, and summary metrics exposed under `/api/reports/*` and consumed by the React `Reports` view.
- Background workers and predictive models (see `backend/train_model.py` and `app/services/predictive_analytics.py`) that learn from historical ticket data to recommend routing, priority, and resolution estimates.
- Voice management placeholders that integrate with the agent UI.

### Repository Layout
- `backend/` – Flask application, database models, APIs, workers, and ML utilities.
- `frontend/` – React + Vite SPA for agents (login, dashboard, analytics, reports, voice recorder).
- `data/` – Sample CSVs and template responses for bootstrapping local datasets.
- `model/` – Serialized ML artifacts (e.g., `intent_clf.joblib`).
- `docker-compose.yml` + service Dockerfiles – Containerized dev/prod setup for API, frontend, and backing services.

### Environment & Integrations
- Uses PostgreSQL/SQLite via SQLAlchemy (default DB points to `backend/instance/helpline.db` for local use).
- Relies on Redis for webhook deduplication/queueing (`app/routes/webhook.py`), configurable through `REDIS_HOST`/`REDIS_PORT`.
- External SMS/voice integrations plug into `services/` modules; credentials are expected via environment variables (see `backend/config.py`).

For detailed run instructions, see `RUNBOOK.md`.

