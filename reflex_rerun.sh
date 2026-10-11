#!/bin/bash

echo "Checking for processes on ports 3000 and 8000..."

# Find PIDs using ports 3000 and 8000
PIDS=$(lsof -ti:3000,8000)

if [ -n "$PIDS" ]; then
  echo "Killing processes: $PIDS"
  kill -9 $PIDS
  echo "Processes killed."
else
  echo "No processes found on ports 3000 or 8000."
fi

echo "Starting Reflex app with args: $@"

# If this script is already running inside the uv-managed venv, avoid nesting uv.
if [ -n "${VIRTUAL_ENV:-}" ]; then
  reflex run "$@"
else
  uv run reflex run "$@"
fi
