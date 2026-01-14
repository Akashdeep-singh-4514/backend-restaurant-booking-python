#!/usr/bin/env bash
set -e

echo "Running Alembic migrations..."

poetry run alembic upgrade head

echo "Migrations completed successfully!"

echo "Starting server..."
exec uvicorn src.app:app --host 0.0.0.0 --port 8001