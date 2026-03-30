# ─────────────────────────────────────────────────────────────
#  Stock Sentiment Tracker — Developer Makefile
#  Usage: make <target>
# ─────────────────────────────────────────────────────────────
.PHONY: help install dev dev-docker prod test lint format typecheck security clean db-up db-down db-migrate seed

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

# ─── Development ─────────────────────────────────────────────
dev: ## Start full dev stack with hot-reload
	$(DOCKER_COMPOSE) up --build -d db redis
	@cd backend && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

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
	cd frontend && npm audit

clean: ## Clean generated files
	cd backend && rm -rf .coverage htmlcov/ .mypy_cache/ .ruff_cache/ .pytest_cache/
	cd frontend && rm -rf dist/ node_modules/.cache/
