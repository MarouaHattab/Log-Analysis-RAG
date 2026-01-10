#!/bin/bash
set -euo pipefail

#################################
# Ollama Model Initialization Script
# This script pulls the required models inside the Ollama Docker container
# NO LOCAL OLLAMA INSTALLATION REQUIRED
#################################

echo "=========================================="
echo "Ollama Model Initialization (Docker)"
echo "=========================================="

# Check if Ollama container is running
echo "Checking if Ollama container is running..."
if ! docker ps --format '{{.Names}}' | grep -q '^ollama$'; then
    echo "❌ ERROR: Ollama container is not running!"
    echo "Please start the services first with:"
    echo "  docker compose up -d"
    exit 1
fi

echo "✅ Ollama container is running"

# Wait for Ollama service to be ready inside the container
echo ""
echo "Waiting for Ollama service to be ready..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # Test if we can list models (this means Ollama is ready)
    if docker exec ollama ollama list > /dev/null 2>&1; then
        echo "✅ Ollama service is ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Waiting for Ollama service..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ ERROR: Ollama service failed to start after $max_attempts attempts"
    echo "Check logs with: docker compose logs ollama"
    exit 1
fi

# Pull embedding model
echo ""
echo "📥 Pulling embedding model: nomic-embed-text:latest"
echo "This may take a few minutes (~274MB download)..."
docker exec ollama ollama pull nomic-embed-text:latest

# Pull generation model
echo ""
echo "📥 Pulling generation model: qwen2.5-coder:1.5b"
echo "This may take a few minutes (~1.0GB download)..."
docker exec ollama ollama pull qwen2.5-coder:1.5b

# Verify models are installed
echo ""
echo "Verifying installed models..."
docker exec ollama ollama list

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
echo "No local Ollama installation required!"
echo ""
