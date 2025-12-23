#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/models/db_schemes/minirag

# Try to upgrade. If it fails due to existing tables, stamp to head.
# The || handles the failure case
alembic upgrade head || {
    echo "Migration failed, tables may already exist. Stamping to head..."
    alembic stamp head
    echo "Stamped successfully."
}

cd /app

# Execute the CMD passed from Dockerfile (uvicorn)
exec "$@"
