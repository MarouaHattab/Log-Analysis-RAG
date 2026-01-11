#!/bin/bash
set -euo pipefail

#################################
# Ollama Model Initialization Script (VPS Optimized)
# This script pulls the required models inside the Ollama Docker container
# NO LOCAL OLLAMA INSTALLATION REQUIRED
# Optimized for VPS deployment with better error handling and retries
#################################

echo "=========================================="
echo "Ollama Model Initialization (Docker - VPS)"
echo "=========================================="

# Check if Ollama container is running
echo "Checking if Ollama container is running..."
if ! docker ps --format '{{.Names}}' | grep -q '^ollama$'; then
    echo "❌ ERROR: Ollama container is not running!"
    echo "Please start the services first with:"
    echo "  docker compose up -d ollama"
    exit 1
fi

echo "✅ Ollama container is running"

# Check container health
echo ""
echo "Checking Ollama container health..."
if ! docker inspect ollama --format='{{.State.Health.Status}}' | grep -q 'healthy\|starting'; then
    echo "⚠️  Warning: Ollama container may not be healthy"
    echo "Container status: $(docker inspect ollama --format='{{.State.Status}}')"
    echo "Waiting 30 seconds for container to stabilize..."
    sleep 30
fi

# Wait for Ollama service to be ready inside the container
echo ""
echo "Waiting for Ollama service to be ready..."
max_attempts=90  # Increased for VPS (slower startup)
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # Test if we can list models (this means Ollama is ready)
    if docker exec ollama ollama list > /dev/null 2>&1; then
        echo "✅ Ollama service is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "Attempt $attempt/$max_attempts: Still waiting for Ollama service..."
        # Check if container is still running
        if ! docker ps --format '{{.Names}}' | grep -q '^ollama$'; then
            echo "❌ ERROR: Ollama container stopped unexpectedly!"
            echo "Check logs with: docker compose logs ollama"
            exit 1
        fi
    fi
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ ERROR: Ollama service failed to start after $max_attempts attempts"
    echo "Check logs with: docker compose logs ollama"
    echo "Check container status: docker ps -a | grep ollama"
    exit 1
fi

# Pull embedding model with retry logic (VPS may have network issues)
echo ""
echo "📥 Pulling embedding model: nomic-embed-text:latest"
echo "This may take a few minutes (~274MB download)..."
MAX_RETRIES=3
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec ollama ollama pull nomic-embed-text:latest; then
        echo "✅ Successfully pulled nomic-embed-text:latest"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⚠️  Pull failed, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
            sleep 5
        else
            echo "❌ ERROR: Failed to pull nomic-embed-text:latest after $MAX_RETRIES attempts"
            exit 1
        fi
    fi
done

# Pull generation model with retry logic
echo ""
echo "📥 Pulling generation model: qwen2.5-coder:1.5b"
echo "This may take a few minutes (~1.0GB download)..."
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec ollama ollama pull qwen2.5-coder:1.5b; then
        echo "✅ Successfully pulled qwen2.5-coder:1.5b"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⚠️  Pull failed, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
            sleep 5
        else
            echo "❌ ERROR: Failed to pull qwen2.5-coder:1.5b after $MAX_RETRIES attempts"
            exit 1
        fi
    fi
done

# Verify models are installed
echo ""
echo "Verifying installed models..."
docker exec ollama ollama list

# Test model inference (optional, but recommended for VPS)
echo ""
echo "Testing model inference..."
if docker exec ollama ollama run nomic-embed-text "test" > /dev/null 2>&1; then
    echo "✅ Embedding model test successful"
else
    echo "⚠️  Warning: Embedding model test failed, but model is installed"
fi

echo ""
echo "=========================================="
echo "✅ Ollama models successfully initialized"
echo "=========================================="
echo ""
echo "Available models inside Docker container:"
echo "  - nomic-embed-text:latest (embeddings, ~274MB)"
echo "  - qwen2.5-coder:1.5b (generation, ~1.0GB)"
echo ""
echo "Models are stored in Docker volume: ollama_data"
echo "Ollama is accessible at: http://localhost:11434"
echo "For VPS: Update OPENAI_API_URL in .env.app to: http://ollama:11434/v1"
echo ""
