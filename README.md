# Reflex Databricks Demo

A blank [Reflex](https://reflex.dev/) project, set up with the same dev conventions as
`codoc_in_md` (for publishing to the agentic app store).

## Getting Started

This project uses [Poetry](https://python-poetry.org/) for dependency management.
Make sure you have **Python 3.11** and Poetry installed.

### 1) Ensure Poetry uses Python 3.11

```bash
poetry env use python3.11
poetry env info
```

If `python3.11` is not on your PATH, specify the full executable path:

```bash
poetry env use /absolute/path/to/python3.11
```

### 2) Install dependencies

```bash
poetry install
poetry run playwright install chromium   # for E2E tests
```

### 3) Run the app

```bash
poetry run ./reflex_rerun.sh
```

Then open:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## E2E Tests (Playwright)

E2E suites live under `testcases/<suite_name>/run_test.py`.

Run suites via the repo runner (it starts/stops the Reflex server and collects artifacts):

```bash
poetry run ./run_test_suite.sh smoke_home
```

### Useful environment variables

- `BASE_URL` (default `http://127.0.0.1:3000`)
- `HEADLESS=0` to show the Chromium window
- `PW_SLOWMO_MS=100` to slow actions down so you can watch what happens
- `PW_TIMEOUT_MS=60000` to increase Playwright timeouts on slower machines

Artifacts (screenshots/logs) are written to `testcases/<suite_name>/output/`.

## Deploy files

- `requirements.txt`: Python dependencies for deployment (keep in sync with `pyproject.toml`).
- `apt-packages.txt`: native apt packages needed at deploy time (one per line).
- `backend-paths.txt`: extra URL paths proxied to the backend port instead of the frontend.

## Tech Stack

- **Reflex** 0.8.24
- **Python 3.11**

## License

[MIT](LICENSE)
