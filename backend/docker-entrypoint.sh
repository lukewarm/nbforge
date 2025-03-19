#!/bin/bash
set -e

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start application based on environment
if [ "$1" = "dev" ]; then
    echo "Starting development server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
elif [ "$1" = "prod" ]; then
    echo "Starting production server..."
    gunicorn app.main:app -w 3 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
else
    echo "Starting server with custom command..."
    exec "$@"
fi
