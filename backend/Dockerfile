# Stage 1: builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Install only the minimal runtime dependencies required for boot.
# (ML/collector dependencies can be added in the next implementation steps.)
RUN pip install --no-cache-dir --prefix=/install \
    fastapi==0.115.0 \
    "uvicorn==0.30.6" \
    pydantic==2.9.0 \
    pydantic-settings==2.5.2 \
    sqlalchemy==2.0.35 \
    alembic==1.13.3 \
    asyncpg==0.29.0 \
    psycopg2-binary==2.9.9 \
    "redis[hiredis]==5.1.0" \
    prometheus-client==0.21.0 \
    structlog==24.4.0 \
    python-dotenv==1.0.1 \
    httpx==0.27.2

# Stage 2: runtime
FROM python:3.11-slim AS runtime

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser src/ ./src/

RUN mkdir -p logs && chown appuser:appuser logs

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health').raise_for_status()"

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
