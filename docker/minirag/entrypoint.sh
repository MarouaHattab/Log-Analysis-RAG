#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/models/db_schemes/minirag/
alembic upgrade head
 cd /app

# Execute the CMD passed from Dockerfile (uvicorn)
exec "$@"
