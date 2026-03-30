# Stock Sentiment Tracker

Production-ready stock sentiment analysis platform.

## Stack

- Backend: FastAPI + TimescaleDB + Redis + Celery
- Frontend: React + TypeScript (Vite) + Tailwind
- Infra: Docker + Nginx + GitHub Actions

## Quick Start

```bash
cp backend/.env.example backend/.env
make dev-docker
```

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/api/docs`
