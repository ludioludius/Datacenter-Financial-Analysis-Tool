# AGENTS.md

## What this is

Filing Thesis Engine: a tool that tests an AI-infrastructure investment thesis against SEC filings. A user writes a thesis in plain English. The system splits it into testable claims, pulls evidence from 10-K, 10-Q, 8-K (and S-1/20-F/6-K) filings for hyperscalers, neoclouds and AI labs, and returns a verdict on each claim with exact citations and correct numbers.

## Tech stack

- **Backend:** Python 3.12, uv, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic
- **Database:** PostgreSQL 16 + pgvector (relational data, XBRL facts, full-text search, vectors, job queue)
- **Ingestion:** SEC EDGAR JSON APIs, httpx, Arelle (XBRL), selectolax / BeautifulSoup + lxml
- **Retrieval:** hybrid vector + full-text search with RRF and a cross-encoder reranker
- **Agent:** LangGraph pipeline, Anthropic Python SDK (Haiku for cheap calls, Sonnet for judgment)
- **Frontend:** Next.js (App Router), TypeScript, Tailwind, shadcn/ui, Recharts, TanStack Query, openapi-typescript, SSE
- **Tooling:** ruff, pyright, pytest, Docker Compose, GitHub Actions, Langfuse

## Core rule

The LLM writes language; the database supplies numbers. Every financial figure must come from `xbrl_facts`, never from the model's computation or memory. If the model produces a number, that is a bug.

## Repo layout (planned)

```
apps/web/          # Next.js frontend
services/api/      # FastAPI app
services/worker/   # ingestion + scheduled jobs
packages/core/     # shared Python: db models, EDGAR client, retrieval, agent
evals/             # golden set + eval runner
infra/             # docker-compose.yml, migrations, seed data
```

## Commands (planned; update once they exist)

- Install: `uv sync`
- Run everything: `docker compose up`
- Lint / types: `uv run ruff check .` and `uv run pyright`
- Test: `uv run pytest`
- Migrations: `uv run alembic upgrade head`

## Conventions

- Schema changes go through SQLAlchemy models plus an Alembic migration.
- Regenerate TypeScript types with openapi-typescript after any API schema change.
- Never commit secrets; list new env vars in `.env.example`.
