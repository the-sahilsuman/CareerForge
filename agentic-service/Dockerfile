# Base
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /app


# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*


# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Dependency files
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project


# Application
COPY app ./app
COPY src ./src


# Runtime
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001


# Health check
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=30s \
            --retries=3 \
            CMD curl -f http://127.0.0.1:8001/health || exit 1


# Start Agentic Service
# app.main -> FastAPI lifespan -> Ingestion Worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]