# AGENTS.md

This file describes how an AI coding agent (and humans) should work in this repository.

## 0) Always read the docs first

Before making changes or running commands, **read all README.md files in this repo** and follow them.

- Repo overview & dev workflow: `README.md`
- E2E test runner conventions: `testcases/README.md`

If you already read them earlier in the session, **re-check** when unsure.

## 1) Python / uv requirements (strict)

This project targets **Python 3.11**. The version is pinned in `.python-version`, and uv is the package manager.

- Use the uv-managed environment (`.venv`) created by `uv sync`.
- If uv picked another Python (e.g. 3.12+), re-create it:

```bash
uv python install 3.11
uv sync --python 3.11
```

If `python3.11` is not available on PATH, install it with `uv python install 3.11`.

## 2) Default rule: use `uv run` for scripts

When running any repo scripts, prefer:

- `uv run <command>`

This ensures the correct virtualenv + dependencies are used.

## 3) Running the app: prefer `reflex_rerun.sh`

When you need to start/restart the Reflex app during development, **prefer the repo helper script**.

Typical usage:

```bash
uv run ./reflex_rerun.sh
```

Notes:
- Prefer `uv run ./reflex_rerun.sh` over `uv run reflex run`.
- This keeps the app startup/restart behavior consistent and helps it run stably on the expected ports: frontend `3000`, backend `8000`.
- If you must run Reflex directly, still do it via uv: `uv run reflex run`.

## 4) Running E2E suites: prefer `run_test_suite.sh`

E2E suites live under `testcases/<suite_name>/run_test.py`.

Do **not** run Playwright suites by starting/stopping the server manually unless you have to.
Instead, use the repo runner, which manages:

- starting/stopping the Reflex server
- setting `OUTPUT_DIR`
- collecting artifacts

Run a suite like this:

```bash
uv run ./run_test_suite.sh smoke_home
```

Optional environment variables (see `testcases/README.md`):

- `BASE_URL` (default `http://127.0.0.1:3000`)
- `HEADLESS=0` to watch the browser

## 5) Expectations when acting as an agent

- Prefer the smallest, focused change set.
- After code changes, run the closest relevant check (at minimum the related suite via `run_test_suite.sh`).
- Report outcomes: what you ran, pass/fail, and where artifacts/logs were written.
