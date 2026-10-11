# Reflex Databricks Demo

A blank [Reflex](https://reflex.dev/) project, set up with the same dev conventions as
`codoc_in_md` (for publishing to the agentic app store).

## Getting Started

Requirements: **Python 3.11** and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                           # first time only (and after dependency changes)
cp .env.template .env             # first time only, then fill in your Databricks values
uv run ./reflex_rerun.sh          # start / restart the app
```

`.env` holds your Databricks connection (`DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`). It is git-ignored, so never commit real values.

Then open http://localhost:3000

## E2E Tests

```bash
uv run playwright install chromium   # first time only
uv run ./run_test_suite.sh smoke_home
```

Add `HEADLESS=0` to watch the browser. See [testcases/README.md](testcases/README.md) for more options.

## Troubleshooting

If uv picks a Python other than 3.11:

```bash
uv python install 3.11
uv sync --python 3.11
```

## License

[MIT](LICENSE)
