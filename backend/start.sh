#!/bin/sh
set -e

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting server..."
exec uvicorn api_server:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
