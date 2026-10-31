#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing dependencies with uv..."
uv sync --frozen && uv cache prune --ci

echo "==> Collecting static files..."
uv run --directory backend python manage.py collectstatic --noinput

echo "==> Running database migrations..."
if [ -n "$DATABASE_URL" ]; then
    uv run --directory backend python manage.py migrate_schemas --noinput || echo "Warning: Migration failed, check database credentials."
else
    echo "DATABASE_URL not set, skipping build-time migrations."
fi

echo "==> Build finished successfully."
