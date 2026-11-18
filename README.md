# Filing Thesis Engine

Test an AI-infrastructure investment thesis against what companies actually report to the SEC.
Write a thesis in plain English; get a verdict on each claim with exact citations from 10-K,
10-Q and 8-K filings.

> Early development. Setup instructions will land with Phase 0.

## Running it

```sh
cp .env.example .env       # then fill in the keys you need
docker compose up --build   # Postgres, migrations, API and web app
```

- Web app: http://localhost:3000
- API health: http://localhost:8000/health

API docs are at http://localhost:8000/docs.

## Development

```sh
uv sync          # install Python deps
docker compose up -d db                       # just the database
uv run alembic upgrade head                   # apply migrations
uv run uvicorn fte_api.main:app --reload      # API with auto-reload
cd apps/web && npm install && npm run dev     # web app on :3000
uv run ruff check .
uv run pyright
uv run pytest
```

## License

MIT
