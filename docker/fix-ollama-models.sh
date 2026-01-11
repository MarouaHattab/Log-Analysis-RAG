#!/bin/bash
# Quick fix script to manually install Ollama models

echo "🔧 Installing Ollama Models Manually..."

# Check if Ollama is running
if ! docker exec ollama ollama list > /dev/null 2>&1; then
    echo "❌ Ollama container is not running or not accessible"
    echo "Start it with: docker compose up -d ollama"
    exit 1
fi

# Models to install
GENERATION_MODEL="${GENERATION_MODEL:-qwen2.5-coder:7b}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text:latest}"

echo ""
echo "Installing models:"
echo "  - Generation: $GENERATION_MODEL"
echo "  - Embedding: $EMBEDDING_MODEL"
echo ""

# Install generation model
echo "📥 Pulling generation model: $GENERATION_MODEL"
if docker exec ollama ollama pull "$GENERATION_MODEL"; then
    echo "✅ Generation model installed"
else
    echo "❌ Failed to install generation model"
    exit 1
fi

echo ""

# Install embedding model
echo "📥 Pulling embedding model: $EMBEDDING_MODEL"
if docker exec ollama ollama pull "$EMBEDDING_MODEL"; then
    echo "✅ Embedding model installed"
else
    echo "❌ Failed to install embedding model"
    exit 1
fi

echo ""
echo "✅ All models installed successfully!"
echo ""
echo "Installed models:"
docker exec ollama ollama list
