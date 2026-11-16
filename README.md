# Filing Thesis Engine

Test an AI-infrastructure investment thesis against what companies actually report to the SEC.
Write a thesis in plain English; get a verdict on each claim with exact citations from 10-K,
10-Q and 8-K filings.

> Early development. Setup instructions will land with Phase 0.

## Development

```sh
uv sync          # install Python deps
uv run ruff check .
uv run pyright
uv run pytest
```

## License

MIT
