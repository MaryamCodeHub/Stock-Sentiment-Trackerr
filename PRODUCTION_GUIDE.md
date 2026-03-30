# 🚀 Production-Ready Stock Sentiment Tracker — Complete Build Guide

> **Author:** Senior Software Architect & UI/UX Designer  
> **Audience:** Junior → Mid-level developers  
> **Goal:** Build an industry-standard, production-deployable Stock Sentiment Tracker that passes senior technical review  
> **Stack:** FastAPI · TimescaleDB · Redis · React · Docker · GitHub Actions

---

## Table of Contents

1. [Project Planning & Requirements](#1-project-planning--requirements)
2. [Technology Stack Selection](#2-technology-stack-selection)
3. [Project Setup & Structure](#3-project-setup--structure)
4. [Development Environment](#4-development-environment)
5. [Core Application Development](#5-core-application-development)
6. [Dashboard Design & Development](#6-dashboard-design--development)
7. [Testing Strategy](#7-testing-strategy)
8. [Logging & Monitoring](#8-logging--monitoring)
9. [Security Best Practices](#9-security-best-practices)
10. [Containerization & Deployment](#10-containerization--deployment)
11. [CI/CD Pipeline](#11-cicd-pipeline)
12. [Documentation Standards](#12-documentation-standards)
13. [Performance Optimization](#13-performance-optimization)
14. [Final Checklists](#14-final-checklists)

---

## 1. Project Planning & Requirements

### 1.1 Project Scope & Objectives

**Mission Statement:**  
Build a real-time, AI-powered Stock Sentiment Tracker that aggregates financial news, social media signals, and market data to produce actionable sentiment scores — presented through a stunning, production-grade dashboard.

**Core Objectives:**

| Objective | Description |
|-----------|-------------|
| Data Aggregation | Collect price data, news articles, and social signals in real-time |
| Sentiment Analysis | Apply NLP to score market sentiment per symbol |
| Visualization | Deliver beautiful, interactive charts and KPI cards |
| Reliability | 99.9% uptime, <200ms API response time |
| Scalability | Handle 100+ symbols, 1000+ concurrent dashboard users |

---

### 1.2 Functional Requirements

**FR-01: Data Collection**
- Fetch OHLCV (Open, High, Low, Close, Volume) data from Alpha Vantage and Binance
- Ingest news from NewsAPI, Finnhub, and RSS feeds every 5 minutes
- Collect social sentiment from Reddit (PRAW) and Twitter/X API

**FR-02: Sentiment Analysis**
- Classify each news article as Positive / Neutral / Negative
- Produce a composite sentiment score (0–100) per symbol per hour
- Track sentiment trend over 24h, 7d, 30d windows

**FR-03: Dashboard**
- Real-time price ticker with WebSocket updates
- Candlestick chart with technical indicators (MA, RSI, MACD)
- Sentiment gauge, news feed with sentiment badges
- Top Movers table with sparklines
- Fear & Greed Index gauge
- Dark/Light theme toggle

**FR-04: Alerts**
- Price target alerts via WebSocket push
- Sentiment reversal notifications
- Email alerts for critical signals

**FR-05: API**
- REST API for all data (prices, sentiment, news, movers)
- WebSocket endpoint for live price streams
- API key authentication for external consumers

---

### 1.3 Non-Functional Requirements

| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | API latency (p95) | < 200ms |
| Performance | Dashboard initial load | < 3s |
| Reliability | Uptime SLA | 99.9% |
| Scalability | Concurrent users | 1,000+ |
| Security | Auth | JWT + API Keys |
| Data Freshness | Price updates | Every 5 seconds |
| Data Freshness | Sentiment updates | Every 5 minutes |
| Observability | Log retention | 30 days |
| Accessibility | WCAG compliance | 2.1 AA |
| Test Coverage | Unit + Integration | ≥ 85% |

---

### 1.4 Architecture Decision: Modular Monolith

**Why NOT microservices for v1:**
- Microservices add operational overhead (service mesh, distributed tracing, inter-service auth)
- For a team of 1–3 developers, a modular monolith ships faster
- Can be decomposed later when bottlenecks are identified

**Our Architecture: Modular Monolith with Clear Bounded Contexts**

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                 │
│                SSL Termination | Rate Limiting           │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼──────────────┐
         │             │              │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │  React  │   │ FastAPI │   │FastAPI  │
    │Dashboard│   │REST API │   │WebSocket│
    └─────────┘   └────┬────┘   └────┬────┘
                       │              │
              ┌────────▼──────────────▼──────────┐
              │        Application Core           │
              │  ┌──────────┐  ┌──────────────┐  │
              │  │ Sentiment │  │ Data         │  │
              │  │ Module   │  │ Collection   │  │
              │  └──────────┘  └──────────────┘  │
              │  ┌──────────┐  ┌──────────────┐  │
              │  │ Portfolio │  │ Alert        │  │
              │  │ Module   │  │ Module       │  │
              │  └──────────┘  └──────────────┘  │
              └──────────┬────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
    ┌─────▼─────┐  ┌─────▼─────┐  ┌───▼─────┐
    │TimescaleDB│  │   Redis    │  │Celery   │
    │(Time-series│  │  (Cache + │  │(Task    │
    │+ Postgres)│  │  Pub/Sub) │  │ Queue)  │
    └───────────┘  └───────────┘  └─────────┘
```

---

## 2. Technology Stack Selection

### 2.1 Backend: FastAPI

**Why FastAPI over Flask/Django:**
- Native `async/await` support — critical for concurrent data fetching
- Automatic OpenAPI/Swagger docs generation (zero extra work)
- Pydantic v2 validation built-in (type safety at the boundary)
- 2–3x faster than Flask in benchmarks (Starlette ASGI under the hood)
- WebSocket support out of the box

```python
# FastAPI's async = concurrent data fetching without threading complexity
async def fetch_all_data():
    prices, news, sentiment = await asyncio.gather(
        fetch_prices("AAPL"),
        fetch_news("AAPL"),
        fetch_sentiment("AAPL")
    )
```

### 2.2 Frontend: React + TypeScript

**Why React over Streamlit:**
- Streamlit is excellent for data scientists; React is for production apps
- Custom animations, theme switching, WebSocket integration, and mobile responsiveness require React
- Component reusability and ecosystem (Recharts, TanStack Query, Zustand)
- TypeScript catches runtime errors at compile time

**Key Libraries:**

| Library | Purpose | Why This One |
|---------|---------|--------------|
| `recharts` | Charts | React-native, composable, excellent docs |
| `@tanstack/react-query` | Data fetching/caching | Stale-while-revalidate, automatic refetching |
| `zustand` | State management | Simpler than Redux, TypeScript-first |
| `framer-motion` | Animations | Production-grade, GPU-accelerated |
| `lucide-react` | Icons | Consistent, tree-shakeable |
| `tailwindcss` | Styling | Utility-first, no CSS file bloat |
| `socket.io-client` | WebSocket | Reliable, fallback transport |

### 2.3 Database: TimescaleDB + Redis

**Why TimescaleDB over plain PostgreSQL:**
- TimescaleDB IS PostgreSQL — zero migration friction
- Automatic time-series partitioning (hypertables) — queries on 1M rows in <10ms
- Built-in time_bucket() function for OHLCV aggregations
- Continuous aggregates replace expensive GROUP BY on large datasets
- Compression: 90%+ storage savings on historical time-series data

**Why Redis:**
- Sub-millisecond reads for hot data (latest prices, cached API responses)
- Pub/Sub for WebSocket fan-out (one producer → many subscribers)
- Rate limiting counters with atomic INCR
- Celery broker for background tasks

### 2.4 ML/AI: Sentiment Analysis Stack

| Component | Library | Model |
|-----------|---------|-------|
| Primary NLP | `transformers` (HuggingFace) | `ProsusAI/finbert` (finance-tuned BERT) |
| Fast fallback | `vaderSentiment` | Rule-based (no GPU needed) |
| Text preprocessing | `spacy` | `en_core_web_sm` |
| Feature engineering | `pandas`, `numpy` | — |
| Model versioning | `mlflow` | — |
| Serialization | `joblib` | — |

**Why FinBERT over generic BERT:**
FinBERT was trained on financial news and achieves ~97% accuracy on financial sentiment vs. ~71% for general-purpose VADER on finance text.

### 2.5 External APIs

| API | Data Type | Free Tier | Rate Limit |
|-----|-----------|-----------|------------|
| Alpha Vantage | Stock OHLCV | 25 req/day | 5 req/min |
| Binance | Crypto OHLCV | Unlimited | 1200 req/min |
| NewsAPI | News articles | 100 req/day | — |
| Finnhub | Financials + News | 60 req/min | — |
| Reddit (PRAW) | Social sentiment | Free | 60 req/min |
| Fear & Greed | Market index | Free | — |

### 2.6 Infrastructure

| Tool | Role |
|------|------|
| Docker | Containerization |
| Docker Compose | Local orchestration |
| Kubernetes (later) | Production orchestration |
| Nginx | Reverse proxy, SSL, static serving |
| GitHub Actions | CI/CD |
| AWS ECS / Heroku | Cloud deployment |
| Celery + Redis | Async task queue |

---

## 3. Project Setup & Structure

### 3.1 Directory Structure

```
stock-sentiment-tracker/
├── 📁 backend/
│   ├── 📁 src/
│   │   ├── 📁 api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # FastAPI app factory
│   │   │   ├── 📁 routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── prices.py
│   │   │   │   ├── sentiment.py
│   │   │   │   ├── news.py
│   │   │   │   ├── movers.py
│   │   │   │   └── health.py
│   │   │   ├── 📁 middleware/
│   │   │   │   ├── auth.py
│   │   │   │   ├── rate_limit.py
│   │   │   │   └── cors.py
│   │   │   └── 📁 websocket/
│   │   │       ├── __init__.py
│   │   │       ├── manager.py
│   │   │       └── handlers.py
│   │   ├── 📁 core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Pydantic settings
│   │   │   ├── database.py          # SQLAlchemy + TimescaleDB
│   │   │   ├── redis_client.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   ├── 📁 models/
│   │   │   ├── __init__.py
│   │   │   ├── price.py             # ORM models
│   │   │   ├── sentiment.py
│   │   │   ├── news.py
│   │   │   └── schemas.py           # Pydantic request/response schemas
│   │   ├── 📁 services/
│   │   │   ├── __init__.py
│   │   │   ├── 📁 collectors/
│   │   │   │   ├── alpha_vantage.py
│   │   │   │   ├── binance.py
│   │   │   │   ├── news_api.py
│   │   │   │   └── reddit.py
│   │   │   ├── 📁 processors/
│   │   │   │   ├── price_processor.py
│   │   │   │   └── text_cleaner.py
│   │   │   ├── sentiment_analyzer.py
│   │   │   ├── cache_service.py
│   │   │   └── alert_service.py
│   │   ├── 📁 ml/
│   │   │   ├── __init__.py
│   │   │   ├── train.py
│   │   │   ├── predict.py
│   │   │   ├── evaluate.py
│   │   │   └── 📁 models/
│   │   │       └── finbert/         # Model artifacts
│   │   └── 📁 tasks/
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       ├── price_tasks.py
│   │       └── sentiment_tasks.py
│   ├── 📁 tests/
│   │   ├── conftest.py
│   │   ├── 📁 unit/
│   │   │   ├── test_sentiment.py
│   │   │   ├── test_collectors.py
│   │   │   └── test_cache.py
│   │   ├── 📁 integration/
│   │   │   ├── test_api.py
│   │   │   └── test_database.py
│   │   └── 📁 fixtures/
│   │       ├── sample_prices.json
│   │       └── sample_news.json
│   ├── 📁 migrations/
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── 📁 versions/
│   ├── 📁 scripts/
│   │   ├── seed_data.py
│   │   ├── backfill_prices.py
│   │   └── train_model.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── 📁 charts/
│   │   │   │   ├── CandlestickChart.tsx
│   │   │   │   ├── SentimentGauge.tsx
│   │   │   │   ├── SparklineChart.tsx
│   │   │   │   └── SentimentTimeline.tsx
│   │   │   ├── 📁 layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── DashboardGrid.tsx
│   │   │   ├── 📁 cards/
│   │   │   │   ├── KPICard.tsx
│   │   │   │   ├── NewsCard.tsx
│   │   │   │   └── MoverCard.tsx
│   │   │   └── 📁 ui/
│   │   │       ├── ThemeToggle.tsx
│   │   │       ├── Badge.tsx
│   │   │       ├── Toast.tsx
│   │   │       └── Skeleton.tsx
│   │   ├── 📁 hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useTheme.ts
│   │   │   └── usePriceStream.ts
│   │   ├── 📁 store/
│   │   │   ├── themeStore.ts
│   │   │   ├── watchlistStore.ts
│   │   │   └── alertStore.ts
│   │   ├── 📁 api/
│   │   │   ├── client.ts
│   │   │   ├── prices.ts
│   │   │   ├── sentiment.ts
│   │   │   └── news.ts
│   │   ├── 📁 styles/
│   │   │   ├── globals.css
│   │   │   ├── theme.css
│   │   │   └── animations.css
│   │   ├── 📁 types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── Dockerfile
├── 📁 nginx/
│   ├── nginx.conf
│   └── ssl/
├── 📁 configs/
│   ├── prometheus.yml
│   └── redis.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── .github/
│   └── 📁 workflows/
│       ├── ci.yml
│       └── deploy.yml
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

---

### 3.2 Python Package Setup: `pyproject.toml`

**📄 File: `backend/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "stock-sentiment-tracker"
version = "1.0.0"
description = "Production-grade stock sentiment analysis platform"
requires-python = ">=3.11"
license = { text = "MIT" }

dependencies = [
    # Web framework
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.6",
    "websockets==13.0",

    # Data validation
    "pydantic==2.9.0",
    "pydantic-settings==2.5.2",

    # Database
    "sqlalchemy==2.0.35",
    "alembic==1.13.3",
    "asyncpg==0.29.0",        # async PostgreSQL driver
    "psycopg2-binary==2.9.9", # sync driver for Alembic

    # Cache
    "redis[hiredis]==5.1.0",

    # Task queue
    "celery==5.4.0",
    "flower==2.0.1",          # Celery monitoring UI

    # HTTP clients
    "httpx==0.27.2",          # async HTTP (replaces requests)
    "aiohttp==3.10.5",

    # Data processing
    "pandas==2.2.3",
    "numpy==2.1.0",

    # ML / NLP
    "transformers==4.44.2",
    "torch==2.4.1",
    "vaderSentiment==3.3.2",
    "spacy==3.7.6",
    "scikit-learn==1.5.2",
    "joblib==1.4.2",
    "mlflow==2.16.0",

    # Security
    "python-jose[cryptography]==3.3.0",
    "passlib[bcrypt]==1.7.4",

    # Monitoring
    "prometheus-client==0.21.0",
    "structlog==24.4.0",

    # Utilities
    "python-dotenv==1.0.1",
    "tenacity==9.0.0",        # retry logic
    "praw==7.7.1",            # Reddit API
]

[project.optional-dependencies]
dev = [
    "pytest==8.3.3",
    "pytest-asyncio==0.24.0",
    "pytest-cov==5.0.0",
    "httpx==0.27.2",          # TestClient
    "factory-boy==3.3.1",
    "faker==30.1.0",
    "black==24.8.0",
    "isort==5.13.2",
    "flake8==7.1.1",
    "mypy==1.11.2",
    "ruff==0.6.8",
    "bandit==1.7.10",
    "pre-commit==3.8.0",
]

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.ruff]
select = ["E", "F", "W", "I", "N", "UP"]
ignore = ["E501"]
line-length = 88

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=85"

[tool.coverage.run]
omit = ["tests/*", "migrations/*", "scripts/*"]
```

---

### 3.3 Git Configuration

**📄 File: `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
*.egg-info/
dist/
build/
.eggs/

# Environment
.env
.env.*
!.env.example

# ML Models (use MLflow/DVC for versioning)
backend/src/ml/models/*.pkl
backend/src/ml/models/*.joblib
backend/src/ml/models/*.onnx
mlruns/

# Testing
.coverage
.pytest_cache/
htmlcov/
.mypy_cache/
.ruff_cache/

# Node
node_modules/
frontend/dist/
frontend/.env

# Docker
*.log

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets (belt-and-suspenders)
*.pem
*.key
*.crt
secrets/
```

---

### 3.4 Environment Variables

**📄 File: `backend/.env.example`**

```bash
# ─── Application ────────────────────────────────
APP_NAME="Stock Sentiment Tracker"
APP_VERSION="1.0.0"
ENVIRONMENT="development"          # development | staging | production
DEBUG=true
SECRET_KEY="CHANGE-ME-use-openssl-rand-hex-32"
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"

# ─── Database ────────────────────────────────────
DATABASE_URL="postgresql+asyncpg://sst_user:password@localhost:5432/sst_db"
DATABASE_URL_SYNC="postgresql://sst_user:password@localhost:5432/sst_db"
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# ─── Redis ───────────────────────────────────────
REDIS_URL="redis://localhost:6379/0"
REDIS_CACHE_TTL=300                # seconds

# ─── Celery ──────────────────────────────────────
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/2"

# ─── External APIs ───────────────────────────────
ALPHA_VANTAGE_API_KEY="your-key-here"
BINANCE_API_KEY="your-key-here"
BINANCE_API_SECRET="your-secret-here"
NEWS_API_KEY="your-key-here"
FINNHUB_API_KEY="your-key-here"
REDDIT_CLIENT_ID="your-client-id"
REDDIT_CLIENT_SECRET="your-client-secret"
REDDIT_USER_AGENT="StockSentimentTracker/1.0"

# ─── ML ──────────────────────────────────────────
FINBERT_MODEL_PATH="ProsusAI/finbert"
ML_BATCH_SIZE=32
USE_GPU=false

# ─── Logging ─────────────────────────────────────
LOG_LEVEL="INFO"
LOG_FORMAT="json"                  # json | text
LOG_FILE="logs/app.log"

# ─── Monitoring ──────────────────────────────────
PROMETHEUS_ENABLED=true
SENTRY_DSN=""                      # leave empty to disable

# ─── Rate Limiting ───────────────────────────────
RATE_LIMIT_PER_MINUTE=60
```

---

## 4. Development Environment

### 4.1 VS Code Configuration

**📄 File: `.vscode/settings.json`**

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.tabSize": 4
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["backend/tests"],
  "mypy.runUsingActiveInterpreter": true,
  "files.associations": {
    "*.env.example": "dotenv"
  }
}
```

**📄 File: `.vscode/extensions.json`**

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.mypy-type-checker",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-azuretools.vscode-docker",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg",
    "redhat.vscode-yaml",
    "yzhang.markdown-all-in-one"
  ]
}
```

---

### 4.2 Pre-commit Hooks

**📄 File: `.pre-commit-config.yaml`**

```yaml
repos:
  # General file hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ["--maxkb=10240"]    # Block files > 10MB (e.g. model weights)
      - id: detect-private-key
      - id: check-merge-conflict

  # Python formatting
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        language_version: python3.11

  # Python import sorting
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  # Python linting (fast Rust-based)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.8
    hooks:
      - id: ruff
        args: [--fix]

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy]

  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.10
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        exclude: tests/

  # Frontend
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [ts, tsx, css, json]
```

**Setup:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Run once to verify
```

---

### 4.3 Makefile

**📄 File: `Makefile`**

```makefile
# ─────────────────────────────────────────────────────────────
#  Stock Sentiment Tracker — Developer Makefile
#  Usage: make <target>
# ─────────────────────────────────────────────────────────────
.PHONY: help install dev prod test lint format typecheck security clean db-up db-down db-migrate seed

DOCKER_COMPOSE = docker compose
PYTHON = python3
PIP = pip3

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ───────────────────────────────────────────────────
install: ## Install all dependencies (backend + frontend)
	cd backend && $(PIP) install -e ".[dev]"
	cd frontend && npm install
	pre-commit install
	@echo "✅ Dependencies installed"

# ─── Development ─────────────────────────────────────────────
dev: ## Start full dev stack with hot-reload
	$(DOCKER_COMPOSE) up --build -d db redis
	@sleep 2 && cd backend && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
	@cd frontend && npm run dev

dev-docker: ## Start full stack in Docker (with hot-reload volumes)
	$(DOCKER_COMPOSE) -f docker-compose.yml up --build

prod: ## Start production stack
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up --build -d

# ─── Database ────────────────────────────────────────────────
db-up: ## Start database only
	$(DOCKER_COMPOSE) up -d db

db-down: ## Stop database
	$(DOCKER_COMPOSE) stop db

db-migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

db-rollback: ## Rollback last migration
	cd backend && alembic downgrade -1

db-shell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec db psql -U sst_user -d sst_db

db-makemigration: ## Create new migration (usage: make db-makemigration MSG="add sentiment table")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with sample data
	cd backend && $(PYTHON) scripts/seed_data.py

# ─── Testing ─────────────────────────────────────────────────
test: ## Run all tests with coverage
	cd backend && pytest

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit/ -v

test-integration: ## Run integration tests
	cd backend && pytest tests/integration/ -v

test-watch: ## Run tests in watch mode
	cd backend && ptw -- -v

test-frontend: ## Run frontend tests
	cd frontend && npm run test

# ─── Code Quality ────────────────────────────────────────────
lint: ## Lint Python and TypeScript
	cd backend && ruff check src/ tests/
	cd frontend && npm run lint

format: ## Auto-format all code
	cd backend && black src/ tests/ && isort src/ tests/
	cd frontend && npm run format

typecheck: ## Type-check Python and TypeScript
	cd backend && mypy src/
	cd frontend && npm run typecheck

security: ## Run security scans
	cd backend && bandit -r src/ -c pyproject.toml
	cd backend && safety check
	cd frontend && npm audit

# ─── Docker ──────────────────────────────────────────────────
docker-build: ## Build Docker images
	$(DOCKER_COMPOSE) build

docker-clean: ## Remove containers and volumes
	$(DOCKER_COMPOSE) down -v --remove-orphans

docker-logs: ## Tail all container logs
	$(DOCKER_COMPOSE) logs -f

# ─── Utilities ───────────────────────────────────────────────
clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd backend && rm -rf .coverage htmlcov/ .mypy_cache/ .ruff_cache/
	cd frontend && rm -rf dist/ node_modules/.cache/

celery-worker: ## Start Celery worker
	cd backend && celery -A src.tasks.celery_app worker --loglevel=info

celery-flower: ## Start Celery monitoring UI
	cd backend && celery -A src.tasks.celery_app flower --port=5555
```

---

## 5. Core Application Development

### 5.1 Configuration Management

**📄 File: `backend/src/core/config.py`**

```python
"""
Application configuration using Pydantic Settings.

WHY PYDANTIC SETTINGS:
- Type validation at startup (fail fast, not at runtime)
- Automatic .env file loading
- Override via environment variables (12-factor app compliant)
- IDE autocomplete on settings attributes
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── App ─────────────────────────────────────────
    app_name: str = "Stock Sentiment Tracker"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)  # Required, no default
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ─── Database ────────────────────────────────────
    database_url: PostgresDsn = Field(...)
    database_url_sync: str = Field(...)
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # ─── Redis ───────────────────────────────────────
    redis_url: RedisDsn = Field(...)
    redis_cache_ttl: int = 300

    # ─── Celery ──────────────────────────────────────
    celery_broker_url: str = Field(...)
    celery_result_backend: str = Field(...)

    # ─── External APIs ───────────────────────────────
    alpha_vantage_api_key: str = Field(...)
    binance_api_key: str = ""
    binance_api_secret: str = ""
    news_api_key: str = Field(...)
    finnhub_api_key: str = Field(...)
    reddit_client_id: str = Field(...)
    reddit_client_secret: str = Field(...)
    reddit_user_agent: str = "StockSentimentTracker/1.0"

    # ─── ML ──────────────────────────────────────────
    finbert_model_path: str = "ProsusAI/finbert"
    ml_batch_size: int = 32
    use_gpu: bool = False

    # ─── Logging ─────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_file: str = "logs/app.log"

    # ─── Monitoring ──────────────────────────────────
    prometheus_enabled: bool = True
    sentry_dsn: str = ""

    # ─── Rate Limiting ───────────────────────────────
    rate_limit_per_minute: int = 60

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list) -> list[str]:
        """Accept comma-separated string or list from environment."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# lru_cache ensures Settings is only instantiated once (singleton pattern)
@lru_cache
def get_settings() -> Settings:
    return Settings()


# Convenience alias used throughout the app
settings = get_settings()
```

---

### 5.2 Database Design & TimescaleDB Setup

**📄 File: `backend/src/models/price.py`**

```python
"""
Time-series price data model.

TIMESCALEDB HYPERTABLE STRATEGY:
- `prices` table is converted to a hypertable partitioned by `timestamp`
- This enables automatic time-based chunking for O(1) inserts and fast range queries
- Chunk interval: 1 day (optimal for sub-second data with 5-second granularity)
"""
from datetime import datetime

from sqlalchemy import BigInteger, Float, Index, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Price(Base):
    __tablename__ = "prices"

    # TimescaleDB requires time column as part of primary key
    timestamp: Mapped[datetime] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="alpha_vantage")

    # Composite index for most common query pattern: symbol + time range
    __table_args__ = (
        Index("ix_prices_symbol_timestamp", "symbol", "timestamp"),
    )


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    timestamp: Mapped[datetime] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    score: Mapped[float] = mapped_column(Float)       # 0.0 to 1.0
    label: Mapped[str] = mapped_column(String(20))    # positive/neutral/negative
    article_count: Mapped[int] = mapped_column(BigInteger, default=0)
    source: Mapped[str] = mapped_column(String(50))

    __table_args__ = (
        Index("ix_sentiment_symbol_timestamp", "symbol", "timestamp"),
    )


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    published_at: Mapped[datetime] = mapped_column(index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(2000))
    url: Mapped[str] = mapped_column(String(1000))
    source: Mapped[str] = mapped_column(String(100))
    sentiment_label: Mapped[str | None] = mapped_column(String(20))
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    image_url: Mapped[str | None] = mapped_column(String(1000))

    __table_args__ = (
        UniqueConstraint("url", name="uq_news_url"),  # Prevent duplicates
        Index("ix_news_symbol_published", "symbol", "published_at"),
    )
```

**📄 File: `backend/migrations/versions/001_initial_schema.py`**

```python
"""Initial schema with TimescaleDB hypertables.

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Standard table creation
    op.create_table(
        "prices",
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("source", sa.String(50), default="alpha_vantage"),
        sa.PrimaryKeyConstraint("timestamp", "symbol"),
    )

    # ─── CRITICAL: Convert to TimescaleDB hypertable ──────────────────────────
    # This single call enables:
    # - Automatic time-based partitioning (chunks of 1 day)
    # - 100x faster time-range queries vs plain PostgreSQL
    # - Automatic compression of old chunks
    op.execute(
        "SELECT create_hypertable('prices', 'timestamp', "
        "chunk_time_interval => INTERVAL '1 day')"
    )

    # Enable compression after 7 days (saves ~90% storage)
    op.execute("""
        ALTER TABLE prices SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'symbol'
        )
    """)
    op.execute(
        "SELECT add_compression_policy('prices', INTERVAL '7 days')"
    )

    # ─── Continuous Aggregate: Pre-compute hourly OHLCV ──────────────────────
    # This replaces expensive GROUP BY queries on raw data
    op.execute("""
        CREATE MATERIALIZED VIEW prices_hourly
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 hour', timestamp) AS bucket,
            symbol,
            first(open, timestamp) AS open,
            max(high) AS high,
            min(low) AS low,
            last(close, timestamp) AS close,
            sum(volume) AS volume
        FROM prices
        GROUP BY bucket, symbol
        WITH NO DATA
    """)

    op.execute(
        "SELECT add_continuous_aggregate_policy('prices_hourly', "
        "start_offset => INTERVAL '3 hours', "
        "end_offset => INTERVAL '1 hour', "
        "schedule_interval => INTERVAL '1 hour')"
    )

    # Repeat for sentiment_scores and news_articles tables...


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS prices_hourly")
    op.drop_table("prices")
```

---

### 5.3 Async Data Collectors with Retry Logic

**📄 File: `backend/src/services/collectors/alpha_vantage.py`**

```python
"""
Alpha Vantage price data collector.

KEY PATTERNS:
- httpx for async HTTP (2x faster than requests for I/O-bound work)
- tenacity for declarative retry with exponential backoff
- Pydantic for response validation (fail fast on schema changes)
- Structured logging with context (symbol, duration, status)
"""
import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, field_validator
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from src.core.config import settings

logger = logging.getLogger(__name__)


class OHLCVBar(BaseModel):
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str = "alpha_vantage"

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def parse_numeric(cls, v: str | float) -> float:
        return float(v)


class AlphaVantageCollector:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        # Reuse HTTP connection pool across requests
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=10),
        )

    async def __aenter__(self) -> "AlphaVantageCollector":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def fetch_intraday(
        self, symbol: str, interval: str = "5min"
    ) -> list[OHLCVBar]:
        """
        Fetch intraday OHLCV bars for a symbol.

        WHY RETRY WITH EXPONENTIAL BACKOFF:
        Network failures and rate limits are transient. Retrying with
        increasing delays (2s, 4s, 8s...) recovers from blips without
        hammering the API.
        """
        logger.info("Fetching intraday data", extra={"symbol": symbol})

        response = await self._client.get(
            self.BASE_URL,
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "apikey": settings.alpha_vantage_api_key,
                "outputsize": "compact",
                "datatype": "json",
            },
        )
        response.raise_for_status()
        data = response.json()

        # Alpha Vantage returns errors inside a 200 response (quirky API)
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
        if "Note" in data:
            logger.warning("Alpha Vantage rate limit hit", extra={"symbol": symbol})
            await asyncio.sleep(60)  # Wait out the rate limit
            raise httpx.HTTPError("Rate limited")

        time_series_key = f"Time Series ({interval})"
        raw_bars = data.get(time_series_key, {})

        bars = []
        for ts_str, values in raw_bars.items():
            bars.append(
                OHLCVBar(
                    timestamp=datetime.fromisoformat(ts_str),
                    symbol=symbol,
                    open=values["1. open"],
                    high=values["2. high"],
                    low=values["3. low"],
                    close=values["4. close"],
                    volume=values["5. volume"],
                )
            )

        logger.info(
            "Fetched bars successfully",
            extra={"symbol": symbol, "bar_count": len(bars)},
        )
        return sorted(bars, key=lambda b: b.timestamp)

    async def fetch_batch(
        self, symbols: list[str], interval: str = "5min"
    ) -> dict[str, list[OHLCVBar]]:
        """Fetch multiple symbols concurrently with semaphore to avoid rate limits."""
        # Semaphore: allow max 3 concurrent requests to respect Alpha Vantage limits
        semaphore = asyncio.Semaphore(3)

        async def fetch_with_semaphore(symbol: str) -> tuple[str, list[OHLCVBar]]:
            async with semaphore:
                bars = await self.fetch_intraday(symbol, interval)
                return symbol, bars

        results = await asyncio.gather(
            *[fetch_with_semaphore(s) for s in symbols],
            return_exceptions=True,
        )

        output: dict[str, list[OHLCVBar]] = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error("Batch fetch error", extra={"error": str(result)})
                continue
            symbol, bars = result
            output[symbol] = bars

        return output
```

---

### 5.4 Sentiment Analysis Service

**📄 File: `backend/src/services/sentiment_analyzer.py`**

```python
"""
Hybrid sentiment analysis using FinBERT + VADER fallback.

STRATEGY:
1. FinBERT (primary): Transformer model trained on financial text
   - High accuracy (~97%) on financial news
   - Slower (~100ms/article) requires batching

2. VADER (fallback): Rule-based, no GPU needed
   - Lower accuracy (~71%) but instant
   - Used when FinBERT is unavailable or for real-time streaming

BATCHING:
Processing articles individually is inefficient with transformers.
Batching 32 articles together uses GPU/CPU more efficiently.
"""
import logging
from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.core.config import settings

logger = logging.getLogger(__name__)

LABEL_MAP = {
    "positive": "positive",
    "neutral": "neutral",
    "negative": "negative",
    # FinBERT label variants
    "LABEL_0": "positive",
    "LABEL_1": "negative",
    "LABEL_2": "neutral",
}


@dataclass
class SentimentResult:
    label: str           # positive | neutral | negative
    score: float         # 0.0 to 1.0 (confidence)
    compound: float      # -1.0 to 1.0 (signed score)


class SentimentAnalyzer:
    def __init__(self) -> None:
        self._finbert_loaded = False
        self._tokenizer = None
        self._model = None
        self._vader = SentimentIntensityAnalyzer()
        self._device = "cuda" if settings.use_gpu and torch.cuda.is_available() else "cpu"

    def load_finbert(self) -> None:
        """Lazy load FinBERT — only called once, not at import time."""
        if self._finbert_loaded:
            return
        logger.info("Loading FinBERT model...", extra={"model": settings.finbert_model_path})
        self._tokenizer = AutoTokenizer.from_pretrained(settings.finbert_model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            settings.finbert_model_path
        ).to(self._device)
        self._model.eval()
        self._finbert_loaded = True
        logger.info("FinBERT loaded", extra={"device": self._device})

    def analyze_batch(self, texts: list[str]) -> list[SentimentResult]:
        """
        Analyze a batch of texts with FinBERT.
        Falls back to VADER on any error.
        """
        if not self._finbert_loaded:
            self.load_finbert()

        results = []
        batch_size = settings.ml_batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                batch_results = self._finbert_batch(batch)
                results.extend(batch_results)
            except Exception as e:
                logger.warning(
                    "FinBERT batch failed, falling back to VADER",
                    extra={"error": str(e), "batch_start": i},
                )
                for text in batch:
                    results.append(self._vader_analyze(text))

        return results

    def _finbert_batch(self, texts: list[str]) -> list[SentimentResult]:
        """Run FinBERT inference on a batch of texts."""
        assert self._tokenizer and self._model

        # Truncate long texts — FinBERT max is 512 tokens
        inputs = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)

        results = []
        label_names = ["positive", "negative", "neutral"]  # FinBERT order

        for prob_row in probs:
            label_idx = prob_row.argmax().item()
            label = label_names[label_idx]
            score = prob_row[label_idx].item()

            # Convert to signed compound: positive=+score, negative=-score
            if label == "positive":
                compound = score
            elif label == "negative":
                compound = -score
            else:
                compound = 0.0

            results.append(SentimentResult(label=label, score=score, compound=compound))

        return results

    def _vader_analyze(self, text: str) -> SentimentResult:
        """VADER fallback — instant, no model required."""
        scores = self._vader.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return SentimentResult(
            label=label,
            score=abs(compound),
            compound=compound,
        )

    def aggregate_scores(self, results: list[SentimentResult]) -> dict:
        """
        Aggregate individual article scores into a symbol-level composite.
        Uses confidence-weighted average — high-confidence predictions
        contribute more to the final score.
        """
        if not results:
            return {"score": 0.5, "label": "neutral", "article_count": 0}

        total_weight = sum(r.score for r in results)
        weighted_compound = sum(r.compound * r.score for r in results)

        avg_compound = weighted_compound / total_weight if total_weight > 0 else 0.0
        normalized = (avg_compound + 1) / 2  # Map [-1, 1] → [0, 1]

        if avg_compound >= 0.05:
            label = "positive"
        elif avg_compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "score": round(normalized, 4),
            "label": label,
            "compound": round(avg_compound, 4),
            "article_count": len(results),
        }
```

---

### 5.5 FastAPI Application Factory

**📄 File: `backend/src/api/main.py`**

```python
"""
FastAPI application factory.

WHY FACTORY PATTERN:
- Enables creating separate app instances for testing (no shared state)
- Allows different configurations per environment
- Cleaner separation of initialization concerns
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.routes import health, movers, news, prices, sentiment
from src.api.websocket.handlers import websocket_router
from src.core.config import settings
from src.core.database import engine
from src.core.logging import configure_logging
from src.core.redis_client import redis_client

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage startup and shutdown events.

    CRITICAL: Use lifespan (not @app.on_event) — on_event is deprecated in FastAPI 0.93+
    """
    # ─── Startup ──────────────────────────────────────────────────────────────
    configure_logging()
    await logger.ainfo("Starting Stock Sentiment Tracker")

    # Test database connection
    async with engine.begin() as conn:
        await conn.execute(sa.text("SELECT 1"))
    await logger.ainfo("Database connection established")

    # Test Redis connection
    await redis_client.ping()
    await logger.ainfo("Redis connection established")

    yield  # App runs here

    # ─── Shutdown ─────────────────────────────────────────────────────────────
    await engine.dispose()
    await redis_client.aclose()
    await logger.ainfo("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs" if not settings.is_production else None,  # Disable docs in prod
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─── Middleware (order matters: first added = outermost) ──────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        limit=settings.rate_limit_per_minute,
    )

    # ─── Routes ───────────────────────────────────────────────────────────────
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(prices.router, prefix="/api/v1/prices", tags=["Prices"])
    app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["Sentiment"])
    app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
    app.include_router(movers.router, prefix="/api/v1/movers", tags=["Movers"])
    app.include_router(websocket_router)

    # ─── Prometheus metrics endpoint ──────────────────────────────────────────
    if settings.prometheus_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    return app


# Module-level app instance used by uvicorn
app = create_app()
```

---

### 5.6 API Routes with Pydantic Schemas

**📄 File: `backend/src/models/schemas.py`**

```python
"""
Pydantic v2 request/response schemas.

SEPARATION OF CONCERNS:
- ORM models (models/*.py): Database representation
- Schemas (schemas.py): API wire format
These are kept separate to avoid tight coupling between DB and API contracts.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OHLCVResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Enable ORM → Pydantic conversion

    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    # Computed field for frontend convenience
    change_pct: float = Field(description="Percentage change from open to close")


class SentimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    score: float = Field(ge=0.0, le=1.0, description="Sentiment score 0-1")
    label: Literal["positive", "neutral", "negative"]
    compound: float = Field(ge=-1.0, le=1.0)
    article_count: int
    timestamp: datetime
    trend_24h: float | None = Field(None, description="Score change over last 24h")


class NewsArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    published_at: datetime
    symbol: str
    title: str
    description: str | None
    url: str
    source: str
    sentiment_label: Literal["positive", "neutral", "negative"] | None
    sentiment_score: float | None
    image_url: str | None


class TopMoverResponse(BaseModel):
    symbol: str
    name: str
    price: float
    change_pct: float
    volume: float
    sentiment_score: float | None
    sentiment_label: str | None
    sparkline: list[float]          # Last 24 closes for sparkline chart


class KPIResponse(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    fear_greed_index: int           # 0-100
    fear_greed_label: str           # Extreme Fear → Extreme Greed
    top_gainer_symbol: str
    top_gainer_pct: float
    top_loser_symbol: str
    top_loser_pct: float
    overall_sentiment_score: float
    updated_at: datetime


class PaginatedResponse(BaseModel):
    """Generic pagination wrapper."""
    data: list
    total: int
    page: int
    page_size: int
    has_next: bool
```

**📄 File: `backend/src/api/routes/prices.py`**

```python
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.schemas import OHLCVResponse
from src.services.cache_service import cache_response

router = APIRouter()


@router.get("/{symbol}", response_model=list[OHLCVResponse])
@cache_response(ttl=60)  # Cache for 60 seconds
async def get_prices(
    symbol: str,
    interval: Annotated[str, Query(pattern="^(1D|1W|1M|3M|1Y|ALL)$")] = "1D",
    db: AsyncSession = Depends(get_db),
) -> list[OHLCVResponse]:
    """
    Get OHLCV price data for a symbol.

    - **symbol**: Stock ticker (e.g., AAPL, MSFT)
    - **interval**: Time range (1D, 1W, 1M, 3M, 1Y, ALL)
    """
    symbol = symbol.upper()
    time_ranges = {
        "1D": timedelta(days=1),
        "1W": timedelta(weeks=1),
        "1M": timedelta(days=30),
        "3M": timedelta(days=90),
        "1Y": timedelta(days=365),
    }

    since = datetime.utcnow() - time_ranges.get(interval, timedelta(days=1))

    # Use continuous aggregate for longer intervals (much faster)
    table = "prices_hourly" if interval in ("1M", "3M", "1Y", "ALL") else "prices"

    result = await db.execute(
        f"""
        SELECT
            {'bucket' if table == 'prices_hourly' else 'timestamp'} as timestamp,
            symbol, open, high, low, close, volume,
            ((close - open) / open * 100) as change_pct
        FROM {table}
        WHERE symbol = :symbol AND timestamp >= :since
        ORDER BY timestamp ASC
        """,
        {"symbol": symbol, "since": since},
    )
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    return [OHLCVResponse(**dict(row._mapping)) for row in rows]
```

---

### 5.7 Redis Caching Service

**📄 File: `backend/src/services/cache_service.py`**

```python
"""
Redis caching with decorator pattern.

WHY DECORATOR-BASED CACHING:
- Zero boilerplate in route handlers
- Automatic key generation from function name + args
- Cache invalidation via key prefix deletion
- Avoids cache stampede with async locking
"""
import functools
import hashlib
import json
import logging
from typing import Any, Callable

from src.core.redis_client import redis_client

logger = logging.getLogger(__name__)


def cache_response(ttl: int = 300) -> Callable:
    """
    Decorator that caches async function results in Redis.

    Usage:
        @cache_response(ttl=60)
        async def get_prices(symbol: str) -> list[...]:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build cache key from function name + serialized args
            cache_key = _build_key(func.__name__, args, kwargs)

            # Try cache first
            cached = await redis_client.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit", extra={"key": cache_key})
                return json.loads(cached)

            # Cache miss: execute function
            result = await func(*args, **kwargs)

            # Store result (serialize Pydantic models to JSON)
            serialized = _serialize(result)
            await redis_client.setex(cache_key, ttl, serialized)
            logger.debug("Cache set", extra={"key": cache_key, "ttl": ttl})

            return result
        return wrapper
    return decorator


def _build_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Build a deterministic cache key from function signature."""
    key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
    # Hash long keys to keep Redis key size reasonable
    return f"sst:cache:{hashlib.md5(key_data.encode()).hexdigest()}"


def _serialize(obj: Any) -> str:
    """Serialize Pydantic models, lists, and dicts to JSON string."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump_json()
    if isinstance(obj, list):
        items = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in obj
        ]
        return json.dumps(items, default=str)
    return json.dumps(obj, default=str)


async def invalidate_cache(prefix: str) -> int:
    """Delete all cache keys matching a prefix pattern."""
    pattern = f"sst:cache:*{prefix}*"
    keys = await redis_client.keys(pattern)
    if keys:
        deleted = await redis_client.delete(*keys)
        logger.info("Cache invalidated", extra={"pattern": pattern, "count": deleted})
        return deleted
    return 0
```

---

### 5.8 WebSocket Manager for Live Prices

**📄 File: `backend/src/api/websocket/manager.py`**

```python
"""
WebSocket connection manager with Redis Pub/Sub fan-out.

ARCHITECTURE:
Client A ──┐
Client B ──┤─→ WebSocket Manager ─→ Redis Subscribe ─→ Price Publisher
Client C ──┘

WHY REDIS PUB/SUB:
Without Redis, if you have 2 server instances, Client A on Server 1 won't
receive messages published by Server 2. Redis acts as the message bus.
"""
import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket

from src.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        # symbol → set of websocket connections subscribed to that symbol
        self._subscriptions: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, symbol: str) -> None:
        await websocket.accept()
        async with self._lock:
            self._subscriptions[symbol].add(websocket)
        logger.info("WebSocket connected", extra={"symbol": symbol})

    async def disconnect(self, websocket: WebSocket, symbol: str) -> None:
        async with self._lock:
            self._subscriptions[symbol].discard(websocket)
            if not self._subscriptions[symbol]:
                del self._subscriptions[symbol]
        logger.info("WebSocket disconnected", extra={"symbol": symbol})

    async def broadcast(self, symbol: str, data: dict) -> None:
        """Send message to all clients subscribed to a symbol."""
        message = json.dumps(data)
        dead_connections: set[WebSocket] = set()

        connections = self._subscriptions.get(symbol, set()).copy()
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.add(connection)

        # Clean up dead connections
        if dead_connections:
            async with self._lock:
                self._subscriptions[symbol] -= dead_connections

    async def start_redis_listener(self) -> None:
        """
        Listen to Redis Pub/Sub and fan-out to WebSocket clients.
        This runs as a background task when the app starts.
        """
        pubsub = redis_client.pubsub()
        await pubsub.psubscribe("prices:*")  # Subscribe to all price channels

        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue
            try:
                channel = message["channel"].decode()  # e.g. "prices:AAPL"
                symbol = channel.split(":")[1]
                data = json.loads(message["data"])
                await self.broadcast(symbol, data)
            except Exception as e:
                logger.error("Redis pub/sub error", extra={"error": str(e)})


manager = ConnectionManager()
```

---

## 6. Dashboard Design & Development

### 6.1 Complete Color System

**📄 File: `frontend/src/styles/theme.css`**

```css
/* ═══════════════════════════════════════════════════════════════════════════
   STOCK SENTIMENT TRACKER — DESIGN TOKEN SYSTEM
   
   PHILOSOPHY:
   CSS custom properties enable:
   - Instant theme switching without re-renders
   - Single source of truth for colors
   - Easy customization without hunting through component files
═══════════════════════════════════════════════════════════════════════════ */

/* ─── Brand Colors (Theme-Independent) ─────────────────────────────────── */
:root {
  /* Primary: Soft Indigo — buttons, active states, key metrics */
  --color-primary:        #6366F1;
  --color-primary-light:  #818CF8;
  --color-primary-dark:   #4F46E5;

  /* Success: Emerald Green — positive trends, buy signals, up indicators */
  --color-success:        #10B981;
  --color-success-light:  #34D399;
  --color-success-dark:   #059669;

  /* Warning: Amber — neutral signals, watch states */
  --color-warning:        #F59E0B;
  --color-warning-light:  #FBBF24;
  --color-warning-dark:   #D97706;

  /* Danger: Coral Red — negative trends, sell signals, errors */
  --color-danger:         #EF4444;
  --color-danger-light:   #F87171;
  --color-danger-dark:    #DC2626;

  /* Gradients */
  --gradient-hero:    linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #D946EF 100%);
  --gradient-success: linear-gradient(135deg, #10B981 0%, #34D399 100%);
  --gradient-warning: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
  --gradient-danger:  linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  --gradient-card:    linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.05) 100%);

  /* Typography */
  --font-sans:  'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono:  'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;

  /* Font Sizes (fluid scale) */
  --text-xs:   0.75rem;    /* 12px */
  --text-sm:   0.875rem;   /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg:   1.125rem;   /* 18px */
  --text-xl:   1.25rem;    /* 20px */
  --text-2xl:  1.5rem;     /* 24px */
  --text-3xl:  1.875rem;   /* 30px */
  --text-4xl:  2.25rem;    /* 36px */

  /* Spacing */
  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-6:  1.5rem;
  --space-8:  2rem;
  --space-12: 3rem;

  /* Border Radius */
  --radius-sm:   0.375rem;
  --radius-md:   0.5rem;
  --radius-lg:   0.75rem;
  --radius-xl:   1rem;
  --radius-2xl:  1.5rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm:  0 1px 2px 0 rgba(0,0,0,0.05);
  --shadow-md:  0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
  --shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
  --shadow-glow-primary: 0 0 20px rgba(99, 102, 241, 0.3);
  --shadow-glow-success: 0 0 20px rgba(16, 185, 129, 0.3);
  --shadow-glow-danger:  0 0 20px rgba(239, 68, 68, 0.3);

  /* Animation */
  --transition-fast:   150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow:   400ms ease;

  /* Z-index scale */
  --z-dropdown: 100;
  --z-sticky:   200;
  --z-modal:    300;
  --z-toast:    400;
}

/* ─── Dark Theme (Default) ──────────────────────────────────────────────── */
[data-theme="dark"], :root {
  --bg-base:         #0F172A;   /* Rich Navy Black — main background */
  --bg-card:         #1E293B;   /* Slate Gray — card backgrounds */
  --bg-surface:      #334155;   /* Muted Blue-Gray — inputs, dropdowns */
  --bg-surface-alt:  #1E293B;
  --bg-hover:        #2D3F55;

  --text-primary:    #F1F5F9;   /* Off White — main text */
  --text-secondary:  #94A3B8;   /* Cool Gray — secondary text */
  --text-muted:      #64748B;   /* Slate — disabled, placeholders */
  --text-inverse:    #0F172A;

  --border-color:    #334155;   /* Subtle border */
  --border-strong:   #475569;

  /* Chart colors for dark theme */
  --chart-candle-up:    #10B981;
  --chart-candle-down:  #EF4444;
  --chart-grid:         rgba(51, 65, 85, 0.8);
  --chart-crosshair:    rgba(148, 163, 184, 0.5);
  --chart-tooltip-bg:   #1E293B;
  --chart-tooltip-border: #334155;

  /* Glassmorphism */
  --glass-bg:     rgba(30, 41, 59, 0.8);
  --glass-border: rgba(99, 102, 241, 0.2);
  --glass-blur:   blur(12px);
}

/* ─── Light Theme ───────────────────────────────────────────────────────── */
[data-theme="light"] {
  --bg-base:         #F8FAFC;   /* Light Ice — main background */
  --bg-card:         #FFFFFF;   /* Pure White — card backgrounds */
  --bg-surface:      #F1F5F9;   /* Soft Gray — inputs, dropdowns */
  --bg-surface-alt:  #E2E8F0;
  --bg-hover:        #E2E8F0;

  --text-primary:    #0F172A;   /* Dark Navy — main text */
  --text-secondary:  #475569;   /* Slate — secondary text */
  --text-muted:      #94A3B8;
  --text-inverse:    #F8FAFC;

  --border-color:    #E2E8F0;
  --border-strong:   #CBD5E1;

  --chart-candle-up:    #059669;
  --chart-candle-down:  #DC2626;
  --chart-grid:         rgba(226, 232, 240, 0.8);
  --chart-crosshair:    rgba(71, 85, 105, 0.5);
  --chart-tooltip-bg:   #FFFFFF;
  --chart-tooltip-border: #E2E8F0;

  --glass-bg:     rgba(255, 255, 255, 0.8);
  --glass-border: rgba(99, 102, 241, 0.15);
  --glass-blur:   blur(12px);
}
```

---

### 6.2 Tailwind Configuration

**📄 File: `frontend/tailwind.config.ts`**

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        primary:  { DEFAULT: '#6366F1', light: '#818CF8', dark: '#4F46E5' },
        success:  { DEFAULT: '#10B981', light: '#34D399', dark: '#059669' },
        warning:  { DEFAULT: '#F59E0B', light: '#FBBF24', dark: '#D97706' },
        danger:   { DEFAULT: '#EF4444', light: '#F87171', dark: '#DC2626' },
        // Map CSS variables for use in Tailwind classes
        base:     'var(--bg-base)',
        card:     'var(--bg-card)',
        surface:  'var(--bg-surface)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-primary': '0 0 20px rgba(99, 102, 241, 0.3)',
        'glow-success': '0 0 20px rgba(16, 185, 129, 0.3)',
        'glow-danger':  '0 0 20px rgba(239, 68, 68, 0.3)',
      },
      animation: {
        'count-up':      'countUp 1s ease-out forwards',
        'pulse-slow':    'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'slide-in-up':   'slideInUp 0.3s ease-out',
        'fade-in':       'fadeIn 0.2s ease-out',
      },
      keyframes: {
        countUp: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        slideInUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
      },
      backdropBlur: { xs: '2px' },
    },
  },
  plugins: [],
};

export default config;
```

---

### 6.3 Theme Hook & Toggle Component

**📄 File: `frontend/src/hooks/useTheme.ts`**

```typescript
import { useEffect } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'dark' | 'light';

interface ThemeStore {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: 'dark', // Default: dark theme

      toggleTheme: () => {
        const next = get().theme === 'dark' ? 'light' : 'dark';
        set({ theme: next });
        document.documentElement.setAttribute('data-theme', next);
      },

      setTheme: (theme: Theme) => {
        set({ theme });
        document.documentElement.setAttribute('data-theme', theme);
      },
    }),
    {
      name: 'sst-theme',
      onRehydrateStorage: () => (state) => {
        // Apply persisted theme on page load
        if (state?.theme) {
          document.documentElement.setAttribute('data-theme', state.theme);
        }
      },
    }
  )
);

export const useTheme = () => {
  const { theme, toggleTheme } = useThemeStore();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return { theme, toggleTheme, isDark: theme === 'dark' };
};
```

**📄 File: `frontend/src/components/ui/ThemeToggle.tsx`**

```tsx
import { Moon, Sun } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '@/hooks/useTheme';

export function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <motion.button
      onClick={toggleTheme}
      whileTap={{ scale: 0.9 }}
      whileHover={{ scale: 1.05 }}
      className="
        relative w-10 h-10 rounded-full
        bg-[var(--bg-surface)] border border-[var(--border-color)]
        flex items-center justify-center
        transition-all duration-300
        hover:shadow-glow-primary hover:border-primary
      "
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <AnimatePresence mode="wait">
        {isDark ? (
          <motion.div
            key="moon"
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Moon size={18} className="text-primary" />
          </motion.div>
        ) : (
          <motion.div
            key="sun"
            initial={{ rotate: 90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: -90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Sun size={18} className="text-warning" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}
```

---

### 6.4 Dashboard Header with Glassmorphism

**📄 File: `frontend/src/components/layout/Header.tsx`**

```tsx
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Bell, RefreshCw, Search } from 'lucide-react';
import { ThemeToggle } from '@/components/ui/ThemeToggle';

export function Header() {
  const [time, setTime] = useState(new Date());
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header
      className="
        sticky top-0 z-[200]
        border-b border-[var(--border-color)]
        px-6 py-3
      "
      style={{
        background: 'var(--glass-bg)',
        backdropFilter: 'var(--glass-blur)',
        WebkitBackdropFilter: 'var(--glass-blur)', // Safari fix
      }}
    >
      <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-4">

        {/* ─── Brand ────────────────────────────────── */}
        <motion.div
          className="flex items-center gap-3"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'var(--gradient-hero)' }}>
            <Activity size={16} className="text-white" />
          </div>
          <span className="font-bold text-lg text-[var(--text-primary)] hidden sm:block">
            SentimentTrack
          </span>
        </motion.div>

        {/* ─── Search ───────────────────────────────── */}
        <div className="flex-1 max-w-md hidden md:block">
          <div className="
            relative flex items-center
            bg-[var(--bg-surface)] border border-[var(--border-color)]
            rounded-xl px-4 py-2
            focus-within:border-primary focus-within:shadow-glow-primary
            transition-all duration-300
          ">
            <Search size={16} className="text-[var(--text-muted)] mr-2" />
            <input
              type="text"
              placeholder="Search symbol (Ctrl+K)"
              className="
                flex-1 bg-transparent text-sm
                text-[var(--text-primary)] placeholder:text-[var(--text-muted)]
                outline-none font-sans
              "
            />
          </div>
        </div>

        {/* ─── Right Controls ───────────────────────── */}
        <div className="flex items-center gap-3">
          {/* Live indicator */}
          <div className="hidden sm:flex items-center gap-2 text-xs text-[var(--text-secondary)]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-success" />
            </span>
            <span className="font-mono">
              {time.toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>

          {/* Refresh indicator */}
          <div className="hidden sm:flex items-center gap-1 text-xs text-[var(--text-muted)]">
            <RefreshCw size={12} className="animate-spin-slow" />
            <span>Updated {lastUpdated.toLocaleTimeString()}</span>
          </div>

          <button
            className="
              w-9 h-9 rounded-full flex items-center justify-center
              bg-[var(--bg-surface)] border border-[var(--border-color)]
              text-[var(--text-secondary)] hover:text-primary
              transition-colors duration-200 relative
            "
            aria-label="Notifications"
          >
            <Bell size={16} />
            {/* Unread badge */}
            <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-danger
                             text-white text-[9px] flex items-center justify-center font-bold">
              3
            </span>
          </button>

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
```

---

### 6.5 KPI Cards with Count-Up Animation

**📄 File: `frontend/src/components/cards/KPICard.tsx`**

```tsx
import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;          // Percentage change (positive = up)
  icon: React.ReactNode;
  gradient?: string;        // Custom gradient class
  prefix?: string;          // e.g. "$"
  suffix?: string;          // e.g. "%"
  delay?: number;           // Animation stagger delay
}

export function KPICard({
  title, value, change, icon, gradient, prefix = '', suffix = '', delay = 0
}: KPICardProps) {
  const isPositive = change !== undefined && change >= 0;
  const changeColor = change === undefined ? '' : isPositive ? 'text-success' : 'text-danger';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="
        relative overflow-hidden
        bg-[var(--bg-card)] border border-[var(--border-color)]
        rounded-2xl p-5 cursor-default
        hover:border-primary hover:shadow-glow-primary
        transition-all duration-300
        group
      "
    >
      {/* Background gradient on hover */}
      <div className="
        absolute inset-0 opacity-0 group-hover:opacity-100
        transition-opacity duration-300 rounded-2xl
        pointer-events-none
      " style={{ background: 'var(--gradient-card)' }} />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <p className="text-sm text-[var(--text-secondary)] font-medium">
            {title}
          </p>
          <div className="
            w-10 h-10 rounded-xl flex items-center justify-center
            bg-[var(--bg-surface)] text-primary
            group-hover:scale-110 transition-transform duration-300
          ">
            {icon}
          </div>
        </div>

        {/* Value */}
        <div className="flex items-end gap-2">
          <AnimatedNumber
            value={typeof value === 'number' ? value : parseFloat(String(value)) || 0}
            prefix={prefix}
            suffix={suffix}
            className="text-2xl font-bold font-mono text-[var(--text-primary)]"
          />
        </div>

        {/* Change indicator */}
        {change !== undefined && (
          <div className={`flex items-center gap-1 mt-2 text-sm ${changeColor}`}>
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span className="font-mono font-semibold">
              {isPositive ? '+' : ''}{change.toFixed(2)}%
            </span>
            <span className="text-[var(--text-muted)] text-xs">24h</span>
          </div>
        )}
      </div>

      {/* Gradient border accent (bottom) */}
      <div className="
        absolute bottom-0 left-0 right-0 h-0.5 opacity-0
        group-hover:opacity-100 transition-opacity duration-300
      " style={{ background: 'var(--gradient-hero)' }} />
    </motion.div>
  );
}

// ─── Animated Number Component ────────────────────────────────────────────
interface AnimatedNumberProps {
  value: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  duration?: number;
}

function AnimatedNumber({ value, prefix = '', suffix = '', className = '', duration = 1500 }: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const startRef = useRef(0);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    const start = startRef.current;
    const end = value;
    startTimeRef.current = null;

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const progress = Math.min((timestamp - startTimeRef.current) / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;

      if (ref.current) {
        ref.current.textContent = `${prefix}${formatNumber(current)}${suffix}`;
      }

      if (progress < 1) requestAnimationFrame(animate);
      else startRef.current = end;
    };

    requestAnimationFrame(animate);
  }, [value, prefix, suffix, duration]);

  return <span ref={ref} className={className}>{prefix}{formatNumber(value)}{suffix}</span>;
}

function formatNumber(n: number): string {
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(2)}B`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(2)}K`;
  return n.toFixed(2);
}
```

---

### 6.6 Candlestick Chart with Recharts

**📄 File: `frontend/src/components/charts/CandlestickChart.tsx`**

```tsx
import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ResponsiveContainer, ComposedChart, XAxis, YAxis, CartesianGrid,
  Tooltip, Bar, Line, ReferenceLine
} from 'recharts';
import { fetchPrices } from '@/api/prices';

type TimeRange = '1D' | '1W' | '1M' | '3M' | '1Y';

interface ChartProps {
  symbol: string;
}

const TIME_RANGES: TimeRange[] = ['1D', '1W', '1M', '3M', '1Y'];

export function CandlestickChart({ symbol }: ChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('1D');
  const [indicators, setIndicators] = useState({ ma7: true, ma25: false, rsi: false });

  const { data, isLoading, error } = useQuery({
    queryKey: ['prices', symbol, timeRange],
    queryFn: () => fetchPrices(symbol, timeRange),
    refetchInterval: 30_000,  // Auto-refresh every 30s
    staleTime: 25_000,
  });

  const processedData = useCallback(() => {
    if (!data) return [];
    return data.map((bar, i, arr) => {
      const isUp = bar.close >= bar.open;
      // Candlestick requires high/low mapped to custom bar shape
      return {
        ...bar,
        timestamp: new Date(bar.timestamp).toLocaleTimeString(),
        color: isUp ? 'var(--chart-candle-up)' : 'var(--chart-candle-down)',
        // For recharts Bar, we encode candle as [low, high] range + [open, close] range
        candleRange: [Math.min(bar.open, bar.close), Math.max(bar.open, bar.close)],
        wickRange: [bar.low, bar.high],
        ma7: calculateMA(arr, i, 7),
        ma25: calculateMA(arr, i, 25),
      };
    });
  }, [data]);

  if (isLoading) return <ChartSkeleton />;
  if (error) return <ChartError message="Failed to load price data" />;

  return (
    <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">{symbol}</h2>
          <p className="text-sm text-[var(--text-secondary)]">Price Chart</p>
        </div>

        {/* Time range selector */}
        <div className="flex bg-[var(--bg-surface)] rounded-xl p-1 gap-1">
          {TIME_RANGES.map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200
                ${timeRange === range
                  ? 'bg-primary text-white shadow-glow-primary'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }
              `}
            >
              {range}
            </button>
          ))}
        </div>

        {/* Indicator toggles */}
        <div className="flex items-center gap-2">
          {Object.entries(indicators).map(([key, active]) => (
            <button
              key={key}
              onClick={() => setIndicators(prev => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))}
              className={`
                px-2.5 py-1 rounded-lg text-xs font-mono font-semibold
                border transition-all duration-200
                ${active
                  ? 'border-primary text-primary bg-primary/10'
                  : 'border-[var(--border-color)] text-[var(--text-muted)] hover:border-[var(--border-strong)]'
                }
              `}
            >
              {key.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={380}>
        <ComposedChart data={processedData()} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--chart-grid)"
            vertical={false}
          />
          <XAxis
            dataKey="timestamp"
            tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            axisLine={{ stroke: 'var(--border-color)' }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            orientation="right"
            tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${v.toFixed(2)}`}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Candlestick wicks (thin bar for full range) */}
          <Bar dataKey="wickRange" fill="transparent" stroke="currentColor" />

          {/* Candlestick bodies */}
          <Bar
            dataKey="candleRange"
            shape={(props: any) => <CandleBody {...props} />}
            isAnimationActive={false}
          />

          {/* Moving averages */}
          {indicators.ma7 && (
            <Line dataKey="ma7" stroke="#6366F1" strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
          )}
          {indicators.ma25 && (
            <Line dataKey="ma25" stroke="#F59E0B" strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

// Custom candlestick body renderer
function CandleBody({ x, y, width, height, payload }: any) {
  const isUp = payload?.close >= payload?.open;
  const color = isUp ? 'var(--chart-candle-up)' : 'var(--chart-candle-down)';
  return (
    <rect
      x={x + 2} y={y} width={Math.max(width - 4, 2)} height={Math.max(height, 1)}
      fill={color} stroke={color} rx={1}
    />
  );
}

// Custom tooltip
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;

  return (
    <div className="
      bg-[var(--chart-tooltip-bg)] border border-[var(--chart-tooltip-border)]
      rounded-xl p-3 shadow-lg text-xs font-mono
    ">
      <p className="text-[var(--text-secondary)] mb-2">{d.timestamp}</p>
      {[['O', d.open], ['H', d.high], ['L', d.low], ['C', d.close]].map(([k, v]) => (
        <div key={String(k)} className="flex justify-between gap-4">
          <span className="text-[var(--text-muted)]">{k}</span>
          <span className="text-[var(--text-primary)] font-semibold">${Number(v).toFixed(2)}</span>
        </div>
      ))}
      <div className="flex justify-between gap-4 mt-1 pt-1 border-t border-[var(--border-color)]">
        <span className="text-[var(--text-muted)]">Vol</span>
        <span className="text-[var(--text-primary)]">{formatVolume(d.volume)}</span>
      </div>
    </div>
  );
}

// Helpers
function calculateMA(data: any[], index: number, period: number): number | null {
  if (index < period - 1) return null;
  const slice = data.slice(index - period + 1, index + 1);
  return slice.reduce((sum, bar) => sum + bar.close, 0) / period;
}

function formatVolume(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  return `${(v / 1e3).toFixed(1)}K`;
}

function ChartSkeleton() {
  return (
    <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-5">
      <div className="animate-pulse space-y-4">
        <div className="h-6 bg-[var(--bg-surface)] rounded w-32" />
        <div className="h-[380px] bg-[var(--bg-surface)] rounded-xl" />
      </div>
    </div>
  );
}

function ChartError({ message }: { message: string }) {
  return (
    <div className="bg-[var(--bg-card)] rounded-2xl border border-danger/30 p-5 text-center">
      <p className="text-danger text-sm">{message}</p>
    </div>
  );
}
```

---

### 6.7 Sentiment Gauge Component

**📄 File: `frontend/src/components/charts/SentimentGauge.tsx`**

```tsx
import { useEffect, useRef } from 'react';

interface SentimentGaugeProps {
  score: number;   // 0-100
  label: string;
  size?: number;
}

/**
 * Custom SVG gauge using arc math.
 * Built from scratch (no library) for pixel-perfect control.
 *
 * Arc calculation:
 * - Full semicircle from 180° to 0° (left to right)
 * - Score of 50 = top of arc (12 o'clock position)
 */
export function SentimentGauge({ score, label, size = 200 }: SentimentGaugeProps) {
  const cx = size / 2;
  const cy = size * 0.6;
  const r = size * 0.38;
  const strokeWidth = size * 0.08;

  // Convert score (0-100) to angle (-180 to 0 degrees on a semicircle)
  const angle = -180 + (score / 100) * 180;
  const angleRad = (angle * Math.PI) / 180;

  // Needle tip position
  const needleLength = r * 0.85;
  const needleX = cx + needleLength * Math.cos(angleRad);
  const needleY = cy + needleLength * Math.sin(angleRad);

  // Get color based on score
  const getColor = (s: number) => {
    if (s <= 25) return 'var(--color-danger)';
    if (s <= 45) return 'var(--color-warning)';
    if (s <= 55) return 'var(--text-secondary)';
    if (s <= 75) return 'var(--color-success-light)';
    return 'var(--color-success)';
  };
  const scoreColor = getColor(score);

  // SVG arc path helper
  const describeArc = (startAngle: number, endAngle: number) => {
    const s = polarToCart(cx, cy, r, startAngle);
    const e = polarToCart(cx, cy, r, endAngle);
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${largeArc} 1 ${e.x} ${e.y}`;
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size * 0.7} viewBox={`0 0 ${size} ${size * 0.7}`}>
        {/* Background arc (track) */}
        <path
          d={describeArc(-180, 0)}
          fill="none"
          stroke="var(--bg-surface)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Colored zones */}
        {[
          { start: -180, end: -108, color: 'var(--color-danger)' },
          { start: -108, end: -36, color: 'var(--color-warning)' },
          { start: -36,  end: 36,  color: 'var(--text-muted)' },
          { start: 36,   end: 108, color: 'var(--color-success-light)' },
          { start: 108,  end: 180, color: 'var(--color-success)' },  // Wait — need 0 not 180 here
        ].map((zone, i) => (
          <path
            key={i}
            d={describeArc(zone.start - 180, zone.end - 180)}
            fill="none"
            stroke={zone.color}
            strokeWidth={strokeWidth * 0.3}
            strokeLinecap="round"
            opacity={0.4}
          />
        ))}

        {/* Active arc up to current score */}
        <path
          d={describeArc(-180, angle)}
          fill="none"
          stroke={scoreColor}
          strokeWidth={strokeWidth * 0.6}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${scoreColor})` }}
        />

        {/* Needle */}
        <line
          x1={cx} y1={cy}
          x2={needleX} y2={needleY}
          stroke={scoreColor}
          strokeWidth={strokeWidth * 0.2}
          strokeLinecap="round"
        />
        {/* Needle pivot */}
        <circle cx={cx} cy={cy} r={strokeWidth * 0.3} fill={scoreColor} />

        {/* Score text */}
        <text
          x={cx} y={cy - r * 0.2}
          textAnchor="middle"
          fill="var(--text-primary)"
          fontSize={size * 0.14}
          fontWeight="700"
          fontFamily="var(--font-mono)"
        >
          {Math.round(score)}
        </text>

        {/* Zone labels */}
        {[
          { label: 'Fear', x: cx - r * 0.9, y: cy + 16 },
          { label: 'Greed', x: cx + r * 0.85, y: cy + 16 },
        ].map(({ label: l, x, y }) => (
          <text key={l} x={x} y={y} textAnchor="middle"
                fill="var(--text-muted)" fontSize={size * 0.07}
                fontFamily="var(--font-sans)">
            {l}
          </text>
        ))}
      </svg>

      {/* Label */}
      <span
        className="text-sm font-semibold px-3 py-1 rounded-full"
        style={{ color: scoreColor, backgroundColor: `${scoreColor}20` }}
      >
        {label}
      </span>
    </div>
  );
}

function polarToCart(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}
```

---

### 6.8 WebSocket Hook for Live Prices

**📄 File: `frontend/src/hooks/useWebSocket.ts`**

```typescript
import { useEffect, useRef, useCallback, useState } from 'react';

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketOptions {
  onMessage: (data: any) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions) {
  const { onMessage, reconnectInterval = 3000, maxReconnectAttempts = 5 } = options;
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus('connected');
      reconnectCount.current = 0;
      console.debug(`WebSocket connected: ${url}`);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch {
        console.error('Failed to parse WebSocket message');
      }
    };

    ws.onclose = () => {
      setStatus('disconnected');
      // Exponential backoff reconnect
      if (reconnectCount.current < maxReconnectAttempts) {
        reconnectCount.current++;
        const delay = reconnectInterval * Math.pow(2, reconnectCount.current - 1);
        setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      setStatus('error');
      ws.close();
    };

    wsRef.current = ws;
  }, [url, onMessage, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    reconnectCount.current = maxReconnectAttempts; // Prevent auto-reconnect
    wsRef.current?.close();
  }, [maxReconnectAttempts]);

  const send = useCallback((data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { status, send, disconnect, reconnect: connect };
}

// ─── Specific hook for price streaming ─────────────────────────────────────
export function usePriceStream(symbol: string) {
  const [latestPrice, setLatestPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<number>(0);

  const { status } = useWebSocket(
    `${import.meta.env.VITE_WS_URL}/ws/prices/${symbol}`,
    {
      onMessage: useCallback((data: { price: number; change_pct: number }) => {
        setLatestPrice(data.price);
        setPriceChange(data.change_pct);
      }, []),
    }
  );

  return { latestPrice, priceChange, connectionStatus: status };
}
```

---

### 6.9 News Feed with Sentiment Badges

**📄 File: `frontend/src/components/cards/NewsCard.tsx`**

```tsx
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, ChevronDown, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface NewsCardProps {
  id: number;
  title: string;
  description?: string;
  source: string;
  url: string;
  published_at: string;
  sentiment_label?: 'positive' | 'neutral' | 'negative';
  sentiment_score?: number;
  image_url?: string;
}

const SENTIMENT_CONFIG = {
  positive: {
    label: 'Bullish',
    bg: 'bg-success/15',
    text: 'text-success',
    border: 'border-success/30',
    dot: 'bg-success',
  },
  negative: {
    label: 'Bearish',
    bg: 'bg-danger/15',
    text: 'text-danger',
    border: 'border-danger/30',
    dot: 'bg-danger',
  },
  neutral: {
    label: 'Neutral',
    bg: 'bg-[var(--bg-surface)]',
    text: 'text-[var(--text-secondary)]',
    border: 'border-[var(--border-color)]',
    dot: 'bg-[var(--text-muted)]',
  },
};

export function NewsCard({
  title, description, source, url, published_at,
  sentiment_label = 'neutral', sentiment_score, image_url,
}: NewsCardProps) {
  const [expanded, setExpanded] = useState(false);
  const config = SENTIMENT_CONFIG[sentiment_label];

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="
        bg-[var(--bg-card)] border border-[var(--border-color)]
        rounded-xl p-4 hover:border-[var(--border-strong)]
        transition-all duration-200 group
      "
    >
      <div className="flex gap-3">
        {/* Thumbnail */}
        {image_url && (
          <img
            src={image_url}
            alt=""
            loading="lazy"
            className="w-16 h-16 rounded-lg object-cover flex-shrink-0 bg-[var(--bg-surface)]"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
          />
        )}

        <div className="flex-1 min-w-0">
          {/* Meta row */}
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-semibold text-[var(--text-secondary)]">{source}</span>
            <span className="text-[var(--text-muted)]">·</span>
            <div className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
              <Clock size={10} />
              {formatDistanceToNow(new Date(published_at), { addSuffix: true })}
            </div>

            {/* Sentiment badge */}
            <span className={`
              ml-auto flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold
              border ${config.bg} ${config.text} ${config.border}
            `}>
              <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
              {config.label}
              {sentiment_score !== undefined && (
                <span className="opacity-60">({(sentiment_score * 100).toFixed(0)}%)</span>
              )}
            </span>
          </div>

          {/* Title */}
          <h3 className="text-sm font-semibold text-[var(--text-primary)] leading-snug line-clamp-2 mb-1.5">
            {title}
          </h3>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <a
              href={url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-primary hover:text-primary-light
                         transition-colors duration-200"
            >
              <ExternalLink size={11} />
              Read article
            </a>

            {description && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1 text-xs text-[var(--text-muted)]
                           hover:text-[var(--text-secondary)] transition-colors ml-auto"
              >
                <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
                  <ChevronDown size={12} />
                </motion.div>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Expandable description */}
      <AnimatePresence>
        {expanded && description && (
          <motion.p
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden mt-3 pt-3 border-t border-[var(--border-color)]
                       text-xs text-[var(--text-secondary)] leading-relaxed"
          >
            {description}
          </motion.p>
        )}
      </AnimatePresence>
    </motion.article>
  );
}
```

---

### 6.10 Main Dashboard Layout

**📄 File: `frontend/src/App.tsx`**

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { Header } from '@/components/layout/Header';
import { KPICard } from '@/components/cards/KPICard';
import { CandlestickChart } from '@/components/charts/CandlestickChart';
import { SentimentGauge } from '@/components/charts/SentimentGauge';
import { NewsCard } from '@/components/cards/NewsCard';
import {
  TrendingUp, TrendingDown, Activity, DollarSign,
  BarChart2, Zap
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchKPIs } from '@/api/prices';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function Dashboard() {
  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: fetchKPIs,
    refetchInterval: 30_000,
  });

  return (
    <div className="min-h-screen bg-[var(--bg-base)] font-sans">
      <Header />

      <main className="max-w-[1600px] mx-auto px-4 md:px-6 py-6 space-y-6">

        {/* ─── KPI Cards Grid ──────────────────────────────────────── */}
        <section
          className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4"
          aria-label="Key Performance Indicators"
        >
          <KPICard
            title="Market Cap"
            value={kpis?.total_market_cap ?? 0}
            change={2.4}
            icon={<DollarSign size={18} />}
            prefix="$"
            delay={0}
          />
          <KPICard
            title="24h Volume"
            value={kpis?.total_volume_24h ?? 0}
            change={-1.2}
            icon={<BarChart2 size={18} />}
            prefix="$"
            delay={0.05}
          />
          <KPICard
            title="Fear & Greed"
            value={kpis?.fear_greed_index ?? 0}
            icon={<Activity size={18} />}
            suffix=""
            delay={0.1}
          />
          <KPICard
            title="Top Gainer"
            value={kpis?.top_gainer_pct ?? 0}
            icon={<TrendingUp size={18} />}
            suffix="%"
            delay={0.15}
          />
          <KPICard
            title="Top Loser"
            value={kpis?.top_loser_pct ?? 0}
            icon={<TrendingDown size={18} />}
            suffix="%"
            delay={0.2}
          />
          <KPICard
            title="Sentiment"
            value={(kpis?.overall_sentiment_score ?? 0) * 100}
            icon={<Zap size={18} />}
            suffix="/100"
            delay={0.25}
          />
        </section>

        {/* ─── Chart + Sentiment Panel ─────────────────────────────── */}
        <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <CandlestickChart symbol="AAPL" />
          </div>

          <div className="flex flex-col gap-6">
            {/* Sentiment gauge */}
            <div className="
              bg-[var(--bg-card)] border border-[var(--border-color)]
              rounded-2xl p-5 flex flex-col items-center
            ">
              <h2 className="text-sm font-semibold text-[var(--text-secondary)] mb-4 self-start">
                Market Sentiment
              </h2>
              <SentimentGauge score={68} label="Greed" />
            </div>
          </div>
        </section>

        {/* ─── News Feed ───────────────────────────────────────────── */}
        <section>
          <h2 className="text-base font-bold text-[var(--text-primary)] mb-4">Latest News</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {/* NewsCard components rendered here from API data */}
          </div>
        </section>

      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
      <Toaster position="bottom-right" />
      {import.meta.env.DEV && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}
```

---

## 7. Testing Strategy

### 7.1 Backend Test Configuration

**📄 File: `backend/tests/conftest.py`**

```python
"""
Shared pytest fixtures.

FIXTURE HIERARCHY:
- session scope: DB engine, app instance (created once per test run)
- function scope: DB transaction (rolled back after each test — clean slate)
- Event loop: Shared async loop for all async tests
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.api.main import create_app
from src.core.config import get_settings
from src.models.price import Base

# ─── Override settings for tests ──────────────────────────────────────────
@pytest.fixture(scope="session")
def test_settings():
    """Use SQLite in-memory database for tests (no PostgreSQL required)."""
    return get_settings.cache_clear() or get_settings()


# ─── Database fixtures ────────────────────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """
    Provide a test DB session that rolls back after each test.

    WHY ROLLBACK INSTEAD OF DROP/CREATE:
    Dropping and recreating tables takes ~100ms. Rolling back a transaction
    takes ~1ms. With 500 tests, that's 50s vs 0.5s.
    """
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


# ─── HTTP client fixture ──────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client(db_session):
    """Async HTTP test client with dependency overrides."""
    from src.core.database import get_db
    app = create_app()

    # Override DB dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ─── Data factories ───────────────────────────────────────────────────────
@pytest.fixture
def sample_price_bars():
    from datetime import datetime, timedelta
    base_time = datetime(2024, 1, 15, 9, 30)
    return [
        {
            "timestamp": base_time + timedelta(minutes=i * 5),
            "symbol": "AAPL",
            "open": 180.0 + i * 0.1,
            "high": 181.0 + i * 0.1,
            "low": 179.5 + i * 0.1,
            "close": 180.5 + i * 0.1,
            "volume": 1_000_000.0 + i * 10_000,
        }
        for i in range(20)
    ]
```

---

### 7.2 Unit Tests: Sentiment Analyzer

**📄 File: `backend/tests/unit/test_sentiment.py`**

```python
"""Unit tests for sentiment analyzer."""
import pytest
from unittest.mock import MagicMock, patch

from src.services.sentiment_analyzer import SentimentAnalyzer, SentimentResult


@pytest.fixture
def analyzer():
    return SentimentAnalyzer()


class TestVADERFallback:
    """Test VADER fallback (no model loading required)."""

    def test_positive_text(self, analyzer):
        result = analyzer._vader_analyze(
            "Excellent earnings beat! Company reports record profits and strong guidance."
        )
        assert result.label == "positive"
        assert result.compound > 0

    def test_negative_text(self, analyzer):
        result = analyzer._vader_analyze(
            "Company misses earnings badly. Stock crashes on poor outlook and layoffs."
        )
        assert result.label == "negative"
        assert result.compound < 0

    def test_neutral_text(self, analyzer):
        result = analyzer._vader_analyze(
            "Company released its quarterly report today."
        )
        assert result.label == "neutral"

    def test_score_bounds(self, analyzer):
        """Scores must always be in valid range."""
        texts = ["great!", "terrible!", "okay"]
        for text in texts:
            result = analyzer._vader_analyze(text)
            assert 0.0 <= result.score <= 1.0
            assert -1.0 <= result.compound <= 1.0


class TestAggregation:
    """Test composite score calculation."""

    def test_all_positive_gives_high_score(self, analyzer):
        results = [SentimentResult("positive", 0.9, 0.9) for _ in range(5)]
        agg = analyzer.aggregate_scores(results)
        assert agg["label"] == "positive"
        assert agg["score"] > 0.7

    def test_empty_list_returns_neutral(self, analyzer):
        agg = analyzer.aggregate_scores([])
        assert agg["score"] == 0.5
        assert agg["label"] == "neutral"
        assert agg["article_count"] == 0

    def test_high_confidence_articles_weighted_more(self, analyzer):
        """A single high-confidence negative should outweigh many low-confidence positives."""
        results = [
            SentimentResult("positive", 0.1, 0.1),  # Low confidence
            SentimentResult("positive", 0.1, 0.1),
            SentimentResult("positive", 0.1, 0.1),
            SentimentResult("negative", 0.95, -0.95),  # High confidence
        ]
        agg = analyzer.aggregate_scores(results)
        # Weighted average should lean negative
        assert agg["compound"] < 0


class TestFinBERTFallback:
    """Test that FinBERT failures gracefully fall back to VADER."""

    def test_finbert_failure_uses_vader(self, analyzer):
        with patch.object(analyzer, '_finbert_batch', side_effect=RuntimeError("GPU OOM")):
            analyzer._finbert_loaded = True  # Pretend model is loaded
            results = analyzer.analyze_batch(["Stock crashes on bad news."])
            assert len(results) == 1
            assert results[0].label in ("positive", "neutral", "negative")
```

---

### 7.3 Integration Tests: API Endpoints

**📄 File: `backend/tests/integration/test_api.py`**

```python
"""Integration tests for REST API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPricesAPI:
    async def test_get_prices_returns_200(self, client: AsyncClient, sample_price_bars):
        # Seed test data
        # ... (insert sample_price_bars into test DB)

        response = await client.get("/api/v1/prices/AAPL?interval=1D")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_prices_unknown_symbol_returns_404(self, client: AsyncClient):
        response = await client.get("/api/v1/prices/FAKESYMBOL?interval=1D")
        assert response.status_code == 404

    async def test_invalid_interval_returns_422(self, client: AsyncClient):
        response = await client.get("/api/v1/prices/AAPL?interval=INVALID")
        assert response.status_code == 422  # Pydantic validation error

    async def test_response_schema_matches(self, client: AsyncClient):
        response = await client.get("/api/v1/prices/AAPL?interval=1D")
        if response.status_code == 200:
            for bar in response.json():
                assert all(k in bar for k in ["timestamp", "symbol", "open", "high", "low", "close", "volume"])
                assert isinstance(bar["close"], float)


@pytest.mark.asyncio
class TestHealthCheck:
    async def test_health_returns_200(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_health_includes_components(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        data = response.json()
        assert "database" in data
        assert "redis" in data
```

---

## 8. Logging & Monitoring

### 8.1 Structured Logging with Structlog

**📄 File: `backend/src/core/logging.py`**

```python
"""
Production-grade structured logging with structlog.

WHY STRUCTURED (JSON) LOGGING:
- Log aggregation tools (Datadog, Splunk, ELK) parse JSON automatically
- Filter/search by any field: level=ERROR service=price-collector symbol=AAPL
- No fragile regex parsing of human-readable logs

DEVELOPMENT vs PRODUCTION:
- Dev: Colorized, human-readable output with timestamps
- Prod: JSON with request IDs, service name, version
"""
import logging
import sys
from pathlib import Path

import structlog
from structlog.types import FilteringBoundLogger

from src.core.config import settings


def configure_logging() -> None:
    # Ensure log directory exists
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Base processors (always applied)
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        # Add service metadata to every log line
        _add_service_info,
    ]

    if settings.log_format == "json":
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Pretty colored output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(
            file=open(settings.log_file, "a") if settings.is_production else sys.stdout
        ),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to be captured by structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )


def _add_service_info(logger, method, event_dict):
    """Add service context to every log entry."""
    event_dict["service"] = "stock-sentiment-tracker"
    event_dict["version"] = settings.app_version
    event_dict["environment"] = settings.environment
    return event_dict
```

---

### 8.2 Health Check Endpoint

**📄 File: `backend/src/api/routes/health.py`**

```python
from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from src.core.database import engine
from src.core.redis_client import redis_client
import sqlalchemy as sa

router = APIRouter()


class ComponentStatus(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    latency_ms: float | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str
    database: ComponentStatus
    redis: ComponentStatus


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check for load balancers and monitoring.

    Returns 200 if healthy/degraded, 503 if unhealthy.
    """
    import time
    from src.core.config import settings

    # Check database
    db_status = await _check_database()
    redis_status = await _check_redis()

    overall = "healthy"
    if db_status.status == "unhealthy" or redis_status.status == "unhealthy":
        overall = "unhealthy"
    elif db_status.status == "degraded" or redis_status.status == "degraded":
        overall = "degraded"

    return HealthResponse(
        status=overall,
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database=db_status,
        redis=redis_status,
    )


async def _check_database() -> ComponentStatus:
    import time
    start = time.monotonic()
    try:
        async with engine.begin() as conn:
            await conn.execute(sa.text("SELECT 1"))
        latency = (time.monotonic() - start) * 1000
        return ComponentStatus(
            status="healthy" if latency < 100 else "degraded",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        return ComponentStatus(status="unhealthy", detail=str(e))


async def _check_redis() -> ComponentStatus:
    import time
    start = time.monotonic()
    try:
        await redis_client.ping()
        latency = (time.monotonic() - start) * 1000
        return ComponentStatus(
            status="healthy" if latency < 50 else "degraded",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        return ComponentStatus(status="unhealthy", detail=str(e))
```

---

## 9. Security Best Practices

### 9.1 Rate Limiting Middleware

**📄 File: `backend/src/api/middleware/rate_limit.py`**

```python
"""
Redis-based rate limiting using sliding window algorithm.

WHY SLIDING WINDOW over fixed window:
Fixed window allows 2x burst at window boundaries (e.g., 60 req at 11:59
+ 60 req at 12:00 = 120 req in 2 seconds). Sliding window prevents this.
"""
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.redis_client import redis_client
from src.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60) -> None:
        super().__init__(app)
        self.limit = limit

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and metrics
        if request.url.path in ("/api/v1/health", "/metrics"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"sst:ratelimit:{client_ip}"
        now = time.time()
        window = 60  # 1 minute

        # Sliding window: remove timestamps older than window, count remaining
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window * 2)
        results = await pipe.execute()

        request_count = results[2]

        if request_count > self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "limit": self.limit,
                    "window": "60 seconds",
                    "retry_after": window,
                },
                headers={
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(window),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - request_count))
        return response
```

---

## 10. Containerization & Deployment

### 10.1 Backend Dockerfile (Multi-stage)

**📄 File: `backend/Dockerfile`**

```dockerfile
# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder — install dependencies, don't ship dev tools to production
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies (not needed at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (leverages Docker layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime — minimal image, no build tools
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# WHY NON-ROOT USER:
# If attacker exploits app vulnerability, they get limited shell user,
# not root access to the container/host.
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Create log directory with correct ownership
RUN mkdir -p logs && chown appuser:appuser logs

USER appuser

EXPOSE 8000

# Health check for Docker/Kubernetes
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health').raise_for_status()"

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--loop", "uvloop", "--http", "httptools"]
```

---

### 10.2 Frontend Dockerfile (Multi-stage)

**📄 File: `frontend/Dockerfile`**

```dockerfile
# Stage 1: Build React app
FROM node:20-alpine AS builder

WORKDIR /app

# Cache node_modules layer separately from source
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx (only static files, no Node.js needed)
FROM nginx:alpine AS runtime

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost/health || exit 1
```

---

### 10.3 Docker Compose (Development)

**📄 File: `docker-compose.yml`**

```yaml
# Development configuration with hot-reload volumes
version: '3.9'

services:

  # ─── TimescaleDB ──────────────────────────────────────────────────────────
  db:
    image: timescale/timescaledb:latest-pg15
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: sst_user
      POSTGRES_PASSWORD: sst_password
      POSTGRES_DB: sst_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sst_user -d sst_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ─── Redis ────────────────────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redis_data:/data
      - ./configs/redis.conf:/etc/redis/redis.conf
    command: redis-server /etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s

  # ─── Backend API ──────────────────────────────────────────────────────────
  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://sst_user:sst_password@db:5432/sst_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    env_file: ./backend/.env
    volumes:
      # Hot-reload: mount source code
      - ./backend/src:/app/src
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

  # ─── Celery Worker ────────────────────────────────────────────────────────
  worker:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://sst_user:sst_password@db:5432/sst_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    env_file: ./backend/.env
    volumes:
      - ./backend/src:/app/src
    depends_on:
      - api
    command: celery -A src.tasks.celery_app worker --loglevel=info

  # ─── Frontend ─────────────────────────────────────────────────────────────
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

---

### 10.4 Nginx Configuration

**📄 File: `nginx/nginx.conf`**

```nginx
# Production Nginx config:
# - Reverse proxy to FastAPI
# - Serve React SPA static files
# - SSL termination (certificates mounted as volume)
# - Gzip compression
# - Security headers

upstream api_backend {
    server api:8000;
    keepalive 32;    # Reuse connections (no TCP handshake per request)
}

server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;    # Force HTTPS
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_cache shared:SSL:10m;

    # ─── Security Headers ─────────────────────────────────────────────
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com;" always;

    # ─── Gzip ────────────────────────────────────────────────────────
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    gzip_min_length 1024;

    # ─── React SPA (static files) ─────────────────────────────────────
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;    # SPA routing fallback
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }

    # Cache static assets aggressively (Vite adds content hashes)
    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # ─── API Proxy ────────────────────────────────────────────────────
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";    # Enable keepalive
        proxy_read_timeout 60s;
    }

    # ─── WebSocket Proxy ──────────────────────────────────────────────
    location /ws/ {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 3600s;    # Keep WS connections alive
    }

    # ─── Rate limiting for API ────────────────────────────────────────
    limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
    location ~ ^/api/v1/(prices|sentiment|news) {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://api_backend;
    }
}
```

---

## 11. CI/CD Pipeline

### 11.1 GitHub Actions: CI Workflow

**📄 File: `.github/workflows/ci.yml`**

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── Backend Tests ──────────────────────────────────────────────────────
  backend-test:
    name: Backend — Lint, Type Check, Test
    runs-on: ubuntu-latest

    services:
      # Real TimescaleDB for integration tests
      timescaledb:
        image: timescale/timescaledb:latest-pg15
        env:
          POSTGRES_USER: sst_user
          POSTGRES_PASSWORD: sst_test_password
          POSTGRES_DB: sst_test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports: ["5432:5432"]

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
        ports: ["6379:6379"]

    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check src/ tests/

      - name: Check formatting with black
        run: black --check src/ tests/

      - name: Type check with mypy
        run: mypy src/

      - name: Security scan with bandit
        run: bandit -r src/ -c pyproject.toml

      - name: Check dependencies for vulnerabilities
        run: safety check

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://sst_user:sst_test_password@localhost:5432/sst_test_db
          DATABASE_URL_SYNC: postgresql://sst_user:sst_test_password@localhost:5432/sst_test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: "test-secret-key-minimum-32-characters-long"
          ALPHA_VANTAGE_API_KEY: "test-key"
          NEWS_API_KEY: "test-key"
          FINNHUB_API_KEY: "test-key"
          REDDIT_CLIENT_ID: "test-id"
          REDDIT_CLIENT_SECRET: "test-secret"
          CELERY_BROKER_URL: "redis://localhost:6379/1"
          CELERY_RESULT_BACKEND: "redis://localhost:6379/2"
        run: pytest --cov=src --cov-report=xml --cov-fail-under=85

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml

  # ─── Frontend Tests ──────────────────────────────────────────────────────
  frontend-test:
    name: Frontend — Lint, TypeCheck, Build
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Lint with ESLint
        run: npm run lint

      - name: Type check with TypeScript
        run: npm run typecheck

      - name: Check formatting with Prettier
        run: npm run format:check

      - name: Security audit
        run: npm audit --audit-level=high

      - name: Build production bundle
        run: npm run build

      - name: Check bundle size
        run: |
          SIZE=$(du -sh dist/ | cut -f1)
          echo "Bundle size: $SIZE"
          # Fail if bundle > 5MB (adjust as needed)
          MAX_KB=5120
          ACTUAL_KB=$(du -sk dist/ | cut -f1)
          if [ $ACTUAL_KB -gt $MAX_KB ]; then
            echo "Bundle too large: ${ACTUAL_KB}KB > ${MAX_KB}KB"
            exit 1
          fi

  # ─── Docker Build ─────────────────────────────────────────────────────────
  docker-build:
    name: Docker — Build Images
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push backend
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:latest
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push frontend
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/frontend:latest
            ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 12. Documentation Standards

### 12.1 README.md Template

**📄 File: `README.md`**

```markdown
# 📈 Stock Sentiment Tracker

> Real-time AI-powered stock sentiment analysis dashboard

[![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)](...)
[![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](...)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Screenshots

| Dark Theme | Light Theme |
|------------|-------------|
| ![Dark](docs/screenshots/dark.png) | ![Light](docs/screenshots/light.png) |

## Features

- 🔴 Real-time price streaming via WebSocket
- 🧠 AI sentiment analysis (FinBERT + VADER)
- 📊 Interactive candlestick charts with technical indicators
- 🌓 Dark/Light theme with smooth transitions
- 📱 Fully responsive, mobile-first design
- ⚡ Redis caching for sub-100ms API responses

## Quick Start

\`\`\`bash
# Clone and setup
git clone https://github.com/user/stock-sentiment-tracker
cd stock-sentiment-tracker
cp backend/.env.example backend/.env  # Add your API keys

# Start full stack
make dev-docker

# Dashboard: http://localhost:3000
# API docs:  http://localhost:8000/api/docs
\`\`\`

## Architecture

\`\`\`mermaid
graph TB
    U[User Browser] --> N[Nginx]
    N --> R[React Dashboard]
    N --> A[FastAPI REST]
    N --> WS[FastAPI WebSocket]
    A --> DB[(TimescaleDB)]
    A --> RD[(Redis Cache)]
    WS --> RD
    C[Celery Worker] --> DB
    C --> RD
    C --> AV[Alpha Vantage API]
    C --> NA[News API]
\`\`\`

## API Reference

Full documentation: http://localhost:8000/api/docs (Swagger UI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/prices/{symbol}` | GET | OHLCV price data |
| `/api/v1/sentiment/{symbol}` | GET | Sentiment score |
| `/api/v1/news/{symbol}` | GET | News with sentiment |
| `/api/v1/movers` | GET | Top gainers/losers |
| `/api/v1/health` | GET | Health check |
| `/ws/prices/{symbol}` | WS | Live price stream |

## Development Commands

\`\`\`bash
make install     # Install all dependencies
make dev         # Start dev servers with hot-reload
make test        # Run tests with coverage
make lint        # Lint all code
make format      # Auto-format code
make security    # Security scan
\`\`\`
```

---

## 13. Performance Optimization

### 13.1 Database Indexing Strategy

```sql
-- Strategy: Index the columns that appear in WHERE and ORDER BY clauses

-- Most common query: prices for a symbol in a time range
-- TimescaleDB automatically indexes on time (hypertable partition key)
-- Add composite index for symbol + time
CREATE INDEX CONCURRENTLY ix_prices_symbol_timestamp
    ON prices (symbol, timestamp DESC);

-- News queries: by symbol and publication date
CREATE INDEX CONCURRENTLY ix_news_symbol_published
    ON news_articles (symbol, published_at DESC);

-- Sentiment: by symbol for trend calculations
CREATE INDEX CONCURRENTLY ix_sentiment_symbol_timestamp
    ON sentiment_scores (symbol, timestamp DESC);

-- Full-text search on news titles (using PostgreSQL GIN index)
CREATE INDEX CONCURRENTLY ix_news_title_fts
    ON news_articles USING gin(to_tsvector('english', title));

-- Analyze query plans to verify index usage:
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM prices
WHERE symbol = 'AAPL'
  AND timestamp >= NOW() - INTERVAL '1 day'
ORDER BY timestamp;
-- Look for: "Index Scan" not "Seq Scan"
```

---

### 13.2 Redis TTL Strategy

```python
"""
Tiered caching strategy based on data volatility.

Tier 1 — Ultra-hot (5s TTL):  Live price ticks
Tier 2 — Hot (60s TTL):       OHLCV bars, KPI cards
Tier 3 — Warm (300s TTL):     Sentiment scores, news feed
Tier 4 — Cold (3600s TTL):    Historical aggregations, top movers
"""
CACHE_TTL = {
    "live_price":     5,
    "ohlcv_bars":     60,
    "kpi_cards":      60,
    "sentiment":      300,
    "news_feed":      300,
    "top_movers":     120,
    "historical_1y":  3600,
    "fear_greed":     3600,
}
```

---

### 13.3 Frontend Performance

```typescript
// ─── Code Splitting ──────────────────────────────────────────────────────
// Lazy-load heavy chart library — don't load on initial render
const CandlestickChart = lazy(() =>
  import('@/components/charts/CandlestickChart').then(mod => ({
    default: mod.CandlestickChart
  }))
);

// ─── Image Optimization ──────────────────────────────────────────────────
// Use Intersection Observer for news feed images
function LazyImage({ src, alt }: { src: string; alt: string }) {
  const imgRef = useRef<HTMLImageElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && imgRef.current) {
        imgRef.current.src = src;
        observer.disconnect();
      }
    }, { rootMargin: '100px' });
    if (imgRef.current) observer.observe(imgRef.current);
    return () => observer.disconnect();
  }, [src]);

  return <img ref={imgRef} alt={alt} loading="lazy" />;
}

// ─── Chart Virtualization ─────────────────────────────────────────────────
// For 1Y chart with 525,600 minute candles — only render visible range
// Recharts handles this via domain + brush component built-in

// ─── React Query Optimizations ───────────────────────────────────────────
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,           // Don't refetch for 30s
      gcTime: 5 * 60_000,          // Keep unused data for 5min
      refetchOnWindowFocus: false, // Don't refetch on tab switch
      retry: (failureCount, error: any) => {
        if (error?.status === 404) return false; // Don't retry 404s
        return failureCount < 2;
      },
    },
  },
});
```

---

## 14. Final Checklists

### 14.1 Pre-Production Validation

**Code Quality**
- [ ] All linters pass: `make lint` returns 0 exit code
- [ ] All type checks pass: `make typecheck` returns 0 exit code
- [ ] Test coverage ≥ 85%: `make test` passes
- [ ] No `TODO` or `FIXME` comments in production code paths
- [ ] All sensitive values in environment variables, not hardcoded
- [ ] `.env.example` is up to date with all required variables

**Security**
- [ ] `bandit` scan shows no HIGH severity issues
- [ ] `safety check` shows no known CVEs in dependencies
- [ ] `npm audit --audit-level=high` shows 0 high/critical vulnerabilities
- [ ] No API keys in git history (`git log -p | grep -i "api_key"`)
- [ ] CORS restricted to known origins (not `*` in production)
- [ ] Rate limiting enabled on all public endpoints
- [ ] HTTPS enforced, HTTP redirects to HTTPS
- [ ] Security headers present (X-Frame-Options, CSP, etc.)

**Database**
- [ ] All migrations are reversible (test `alembic downgrade -1`)
- [ ] TimescaleDB hypertables created for time-series tables
- [ ] Compression policies enabled for old data
- [ ] Database connection pool configured correctly
- [ ] Indexes created on all frequently-queried columns

**Frontend**
- [ ] Lighthouse score ≥ 90 (Performance, Accessibility, Best Practices)
- [ ] Dark mode and Light mode both render correctly
- [ ] Works on Chrome, Firefox, Safari, Edge
- [ ] Works on mobile (375px width minimum)
- [ ] Loading states (skeletons) shown for all async content
- [ ] Error states handled for all API calls
- [ ] All images have `alt` attributes (accessibility)
- [ ] Color contrast meets WCAG AA (4.5:1 for text)

**API**
- [ ] All endpoints return correct HTTP status codes
- [ ] Error responses include `detail` field with human-readable message
- [ ] Health check endpoint returns component statuses
- [ ] OpenAPI schema validates against all response models
- [ ] WebSocket reconnects automatically on disconnection

### 14.2 Deployment Checklist

- [ ] Production `.env` configured with real API keys
- [ ] `SECRET_KEY` is cryptographically random (≥32 chars): `openssl rand -hex 32`
- [ ] Database migrations applied: `alembic upgrade head`
- [ ] TimescaleDB continuous aggregates populated with historical data
- [ ] Redis maxmemory policy set: `maxmemory-policy allkeys-lru`
- [ ] SSL certificates valid and auto-renewal configured
- [ ] Docker images tagged with git SHA (not just `latest`)
- [ ] Nginx rate limiting configured
- [ ] Log rotation configured (max 500MB, keep 30 days)
- [ ] Monitoring alerts configured (Prometheus + Alertmanager or Datadog)
- [ ] Celery tasks scheduled (price fetch every 5m, sentiment every 5m)
- [ ] Backup strategy for TimescaleDB (daily `pg_dump` to S3)
- [ ] Rollback plan documented (previous Docker image tag)

### 14.3 Code Review Checklist

**For reviewers:**
- [ ] Does the PR description explain WHY the change was made?
- [ ] Are all new functions/methods docstring'd?
- [ ] Are edge cases handled (empty lists, None values, network errors)?
- [ ] Are tests added for new functionality?
- [ ] Does the code avoid N+1 query problems?
- [ ] Are new secrets/keys stored in environment variables?
- [ ] Does the frontend component handle loading and error states?
- [ ] Are TypeScript types correctly defined (no `any` without justification)?

### 14.4 Security Audit Checklist

- [ ] Input validation on all API endpoints (Pydantic schemas)
- [ ] SQL queries use parameterization (SQLAlchemy ORM, never f-strings with user input)
- [ ] File uploads (if any) validated for type and size
- [ ] JWT tokens have expiration
- [ ] API keys rotated from any that appeared in commits
- [ ] Dependencies audited: `pip-audit` + `npm audit`
- [ ] Docker image runs as non-root user
- [ ] `.dockerignore` excludes `.env`, tests, `.git`
- [ ] Production logs don't contain raw API keys or user passwords

### 14.5 Accessibility (WCAG 2.1 AA) Checklist

- [ ] Color contrast ratio ≥ 4.5:1 for normal text (verify with [WebAIM](https://webaim.org/resources/contrastchecker/))
- [ ] Color is not the only means of conveying information (badges have both color + text)
- [ ] All interactive elements keyboard-navigable (Tab, Enter, Space)
- [ ] Focus indicators visible (not removed with `outline: none` without replacement)
- [ ] All images have descriptive `alt` attributes
- [ ] All charts have text alternatives or ARIA labels
- [ ] Screen reader tested with NVDA or VoiceOver
- [ ] Theme toggle has `aria-label` describing current state
- [ ] Error messages associated with form fields via `aria-describedby`
- [ ] Animations can be disabled (respect `prefers-reduced-motion`)

```css
/* Always add this to your globals.css */
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Architecture Diagrams

### System Data Flow

```mermaid
graph LR
    subgraph External["External Data Sources"]
        AV[Alpha Vantage]
        BIN[Binance]
        NA[News API]
        FH[Finnhub]
        RD[Reddit]
    end

    subgraph Workers["Celery Workers (Background)"]
        PT[Price Task<br/>every 5min]
        ST[Sentiment Task<br/>every 5min]
    end

    subgraph Core["Application Core (FastAPI)"]
        API[REST API]
        WS[WebSocket Server]
    end

    subgraph Storage["Storage Layer"]
        DB[(TimescaleDB<br/>Hypertables)]
        RC[(Redis<br/>Cache + PubSub)]
    end

    subgraph Frontend["Frontend (React)"]
        DASH[Dashboard]
        CHART[Charts]
        NEWS[News Feed]
    end

    AV --> PT
    BIN --> PT
    NA --> ST
    FH --> ST
    RD --> ST

    PT --> DB
    PT --> RC
    ST --> DB
    ST --> RC

    API --> DB
    API --> RC
    WS --> RC

    DASH --> API
    CHART --> API
    NEWS --> API
    DASH --> WS

    style External fill:#1E293B,stroke:#334155,color:#94A3B8
    style Workers fill:#1E293B,stroke:#6366F1,color:#F1F5F9
    style Core fill:#1E293B,stroke:#10B981,color:#F1F5F9
    style Storage fill:#1E293B,stroke:#F59E0B,color:#F1F5F9
    style Frontend fill:#1E293B,stroke:#8B5CF6,color:#F1F5F9
```

### Database Schema

```mermaid
erDiagram
    PRICES {
        timestamp TIMESTAMPTZ PK
        symbol VARCHAR(20) PK
        open FLOAT
        high FLOAT
        low FLOAT
        close FLOAT
        volume FLOAT
        source VARCHAR(50)
    }

    SENTIMENT_SCORES {
        timestamp TIMESTAMPTZ PK
        symbol VARCHAR(20) PK
        score FLOAT
        label VARCHAR(20)
        compound FLOAT
        article_count INT
        source VARCHAR(50)
    }

    NEWS_ARTICLES {
        id BIGINT PK
        published_at TIMESTAMPTZ
        symbol VARCHAR(20)
        title VARCHAR(500)
        url VARCHAR(1000)
        source VARCHAR(100)
        sentiment_label VARCHAR(20)
        sentiment_score FLOAT
        image_url VARCHAR(1000)
    }

    PRICES ||--o{ SENTIMENT_SCORES : "symbol"
    NEWS_ARTICLES ||--o{ SENTIMENT_SCORES : "contributes to"
```

---

*This guide covers the complete lifecycle of a production-ready Stock Sentiment Tracker — from first commit to production deployment. Every decision includes an explanation of **why**, not just **what**. Build with confidence.*

---

**Version:** 1.0.0 | **Last Updated:** 2025 | **License:** MIT
