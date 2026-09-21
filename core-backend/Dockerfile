# Base
FROM python:3.12-slim AS runtime

# Python production settings
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

# Install only production dependencies.
# --no-dev excludes pytest, mypy, ruff, etc.
RUN uv sync --frozen --no-dev --no-install-project


# Application
COPY app ./app

# Keep package metadata/source available if required by the
# project configuration.
COPY src ./src


# Runtime configuration
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000


# Health check
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=20s \
            --retries=3 \
            CMD curl -f http://127.0.0.1:8000/ || exit 1


# Start FastAPI
#
# IMPORTANT:
# app.main:app contains the lifespan that starts the
# Outbox Worker automatically.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]