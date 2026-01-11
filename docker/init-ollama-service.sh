#!/bin/bash
set -e

# This script runs inside the docker-compose init container
# It waits for Ollama to be ready and installs models

echo "🚀 Initializing Ollama Models (Service Mode)..."

# Default models (can be overridden via environment variables)
GENERATION_MODEL="${GENERATION_MODEL:-qwen2.5-coder:7b}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text:latest}"

# Set OLLAMA_HOST to point to the ollama service
export OLLAMA_HOST=http://ollama:11434

# Wait for Ollama service to be ready
echo "Waiting for Ollama service to be ready..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if OLLAMA_HOST=http://ollama:11434 ollama list > /dev/null 2>&1; then
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
    echo "❌ ERROR: Ollama service not ready after $max_attempts attempts"
    exit 1
fi

# Function to check if model exists
check_model_exists() {
    local model=$1
    # Use ollama CLI to check if model exists
    if OLLAMA_HOST=http://ollama:11434 ollama list 2>/dev/null | grep -q "$model"; then
        return 0
    fi
    # Also check without tag
    local model_base="${model%%:*}"
    if [ "$model_base" != "$model" ] && OLLAMA_HOST=http://ollama:11434 ollama list 2>/dev/null | grep -q "$model_base"; then
        return 0
    fi
    return 1
}

# Function to pull model using Ollama CLI (more reliable than API)
pull_model() {
    local model=$1
    local model_type=$2
    
    echo "📥 Pulling $model_type model: $model"
    echo "This may take several minutes depending on your internet connection..."
    
    # Use ollama CLI to pull the model (more reliable than API)
    # Set OLLAMA_HOST to point to the ollama service
    export OLLAMA_HOST=http://ollama:11434
    
    # Pull the model using ollama CLI
    if OLLAMA_HOST=http://ollama:11434 ollama pull "$model"; then
        echo "✅ Successfully pulled $model"
        
        # Verify the model exists (sometimes takes a moment to register)
        echo "Verifying model installation..."
        sleep 3
        
        if check_model_exists "$model"; then
            echo "✅ Model verified and ready"
            return 0
        else
            # Wait a bit more for model to be registered
            max_wait=60
            waited=0
            while [ $waited -lt $max_wait ]; do
                if check_model_exists "$model"; then
                    echo "✅ Model verified and ready"
                    return 0
                fi
                sleep 2
                waited=$((waited + 2))
            done
            
            # Final check
            if check_model_exists "$model"; then
                echo "✅ Model verified"
                return 0
            else
                echo "⚠️  Warning: Model pulled but not yet visible in list"
                echo "   This is usually fine - the model should be available shortly"
                return 0  # Don't fail, model was pulled successfully
            fi
        fi
    else
        echo "❌ Failed to pull $model"
        return 1
    fi
}

# Check and install generation model
echo ""
echo "Checking generation model: $GENERATION_MODEL"
if check_model_exists "$GENERATION_MODEL"; then
    echo "✅ Generation model $GENERATION_MODEL already installed"
else
    pull_model "$GENERATION_MODEL" "Generation" || exit 1
fi

# Check and install embedding model
echo ""
echo "Checking embedding model: $EMBEDDING_MODEL"
if check_model_exists "$EMBEDDING_MODEL"; then
    echo "✅ Embedding model $EMBEDDING_MODEL already installed"
else
    pull_model "$EMBEDDING_MODEL" "Embedding" || exit 1
fi

echo ""
echo "✅ Ollama Models Initialization Complete!"
echo ""
echo "Installed models:"
OLLAMA_HOST=http://ollama:11434 ollama list
