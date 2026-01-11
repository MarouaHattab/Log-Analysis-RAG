#!/bin/bash
set -e

echo "🚀 Initializing Ollama Models..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default models (can be overridden via environment variables)
GENERATION_MODEL="${GENERATION_MODEL:-qwen2.5-coder:1.5b}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text:latest}"

# Wait for Ollama service to be ready
echo -e "${YELLOW}Waiting for Ollama service to be ready...${NC}"
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama service is ready${NC}"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "Attempt $attempt/$max_attempts: Waiting for Ollama..."
    fi
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ ERROR: Ollama service not ready after $max_attempts attempts${NC}"
    exit 1
fi

# Function to check if model exists
check_model_exists() {
    local model=$1
    docker exec ollama ollama list 2>/dev/null | grep -q "$model" || return 1
}

# Function to pull model
pull_model() {
    local model=$1
    local model_type=$2
    
    echo -e "\n${YELLOW}📥 Pulling $model_type model: $model${NC}"
    echo "This may take several minutes depending on your internet connection..."
    
    if docker exec ollama ollama pull "$model"; then
        echo -e "${GREEN}✅ Successfully pulled $model${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to pull $model${NC}"
        return 1
    fi
}

# Check and install generation model
echo -e "\n${YELLOW}Checking generation model: $GENERATION_MODEL${NC}"
if check_model_exists "$GENERATION_MODEL"; then
    echo -e "${GREEN}✅ Generation model $GENERATION_MODEL already installed${NC}"
else
    pull_model "$GENERATION_MODEL" "Generation" || exit 1
fi

# Check and install embedding model
echo -e "\n${YELLOW}Checking embedding model: $EMBEDDING_MODEL${NC}"
if check_model_exists "$EMBEDDING_MODEL"; then
    echo -e "${GREEN}✅ Embedding model $EMBEDDING_MODEL already installed${NC}"
else
    pull_model "$EMBEDDING_MODEL" "Embedding" || exit 1
fi

# Verify models are working
echo -e "\n${YELLOW}🧪 Testing models...${NC}"

echo "Testing generation model..."
if docker exec ollama ollama run "$GENERATION_MODEL" "Hello" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Generation model is working${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Could not test generation model${NC}"
fi

echo -e "\n${GREEN}=================================="
echo -e "✅ Ollama Models Initialization Complete!"
echo -e "==================================${NC}"
echo ""
echo "Installed models:"
docker exec ollama ollama list
echo ""
echo "You can now use the application with Ollama models!"
