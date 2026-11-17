# Build context is the repo root (the uv workspace), not services/api.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install third-party dependencies first so this layer is cached until uv.lock changes.
COPY pyproject.toml uv.lock ./
COPY packages/core/pyproject.toml packages/core/
COPY services/api/pyproject.toml services/api/
RUN uv sync --frozen --no-dev --no-install-workspace

# Then our own code, which changes far more often.
COPY packages/ packages/
COPY services/api/ services/api/
COPY alembic.ini ./
COPY infra/migrations/ infra/migrations/
RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["uvicorn", "fte_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
