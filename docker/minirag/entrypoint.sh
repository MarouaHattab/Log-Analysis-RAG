#!/bin/bash
set -e

echo "🚀 Starting FastAPI application..."
echo "=================================="

# Wait for Ollama service to be ready
echo "Waiting for Ollama service to be ready..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama service is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "Attempt $attempt/$max_attempts: Waiting for Ollama..."
    fi
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️ WARNING: Ollama service not ready after $max_attempts attempts, continuing anyway..."
    echo "⚠️ Models may not be installed yet. Check ollama-init service logs."
fi

# Wait for models to be available (optional check)
echo "Checking if Ollama models are available..."
model_check_attempts=30
model_attempt=0

while [ $model_attempt -lt $model_check_attempts ]; do
    models=$(curl -s http://ollama:11434/api/tags 2>/dev/null || echo "")
    if [ -n "$models" ] && echo "$models" | grep -q "qwen2.5-coder\|nomic-embed-text"; then
        echo "✅ Ollama models are available"
        break
    fi
    model_attempt=$((model_attempt + 1))
    if [ $((model_attempt % 10)) -eq 0 ]; then
        echo "Waiting for models... ($model_attempt/$model_check_attempts)"
    fi
    sleep 2
done

if [ $model_attempt -eq $model_check_attempts ]; then
    echo "⚠️ WARNING: Models may not be installed yet. The ollama-init service may still be running."
    echo "⚠️ The application will start, but LLM features may not work until models are installed."
fi

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to be ready..."
pg_attempts=30
pg_attempt=0

while [ $pg_attempt -lt $pg_attempts ]; do
    if pg_isready -h pgvector -p 5432 -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    pg_attempt=$((pg_attempt + 1))
    sleep 2
done

# Run database migrations
echo ""
echo "Running database migrations..."
cd /app/models/db_schemes/minirag/
alembic upgrade head || {
    echo "⚠️ WARNING: Database migration failed. Continuing anyway..."
}
cd /app

echo ""
echo "✅ All checks complete. Starting application..."
echo "=================================="
echo ""

# Execute the CMD passed from Dockerfile (uvicorn)
exec "$@"
