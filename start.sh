#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

PORT="${PORT:-10000}"
echo "==> Starting Swarna Khata ERP ASGI server on 0.0.0.0:$PORT..."

cd backend
exec uv run uvicorn config.asgi:application --host 0.0.0.0 --port "$PORT"
