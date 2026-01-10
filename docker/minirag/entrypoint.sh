#!/bin/bash
set -e

echo "Waiting for Ollama service to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama service is ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Waiting for Ollama..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️ WARNING: Ollama service not ready, continuing anyway..."
fi

echo "Running database migrations..."
cd /app/models/db_schemes/minirag/
alembic upgrade head
 cd /app

# Execute the CMD passed from Dockerfile (uvicorn)
exec "$@"
