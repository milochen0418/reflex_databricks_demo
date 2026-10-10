# Reflex Databricks Demo

A blank [Reflex](https://reflex.dev/) project, set up with the same dev conventions as
`codoc_in_md` (for publishing to the agentic app store).

## Getting Started

Requirements: **Python 3.11** and [Poetry](https://python-poetry.org/).

```bash
poetry install                    # first time only (and after dependency changes)
cp .env.template .env             # first time only, then fill in your Databricks values
poetry run ./reflex_rerun.sh      # start / restart the app
```

`.env` holds your Databricks connection (`DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`). It is git-ignored, so never commit real values.

Then open http://localhost:3000

## E2E Tests

```bash
poetry run playwright install chromium   # first time only
poetry run ./run_test_suite.sh smoke_home
```

Add `HEADLESS=0` to watch the browser. See [testcases/README.md](testcases/README.md) for more options.

## Troubleshooting

If Poetry picks a Python other than 3.11:

```bash
poetry env use python3.11
poetry install
```

## License

[MIT](LICENSE)
