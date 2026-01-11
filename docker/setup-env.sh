#!/bin/bash
set -e

# Script to set up environment files from examples

echo "🔧 Setting up environment files..."

cd "$(dirname "$0")/env"

# Check if .env files already exist
if [ -f ".env.app" ] || [ -f ".env.postgres" ] || [ -f ".env.rabbitmq" ] || [ -f ".env.redis" ]; then
    echo "⚠️  Warning: Some .env files already exist."
    read -p "Do you want to overwrite them? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping environment file setup."
        exit 0
    fi
fi

# Create .env.app
if [ ! -f ".env.app" ]; then
    cat > .env.app << 'EOF'
# Application Configuration
APP_NAME=mini-rag-app
APP_VERSION=1.0.0

# File Upload Configuration
FILE_ALLOWED_TYPES=["txt","log","csv","json","pdf"]
FILE_MAX_SIZE=10485760
FILE_DEFAULT_CHUNK_SIZE=1000

# LLM Configuration for local Ollama
GENERATION_BACKEND=OPENAI
EMBEDDING_BACKEND=OPENAI

# Use local Ollama endpoint (OpenAI compatible)
OPENAI_API_URL=http://ollama:11434/v1
OPENAI_API_KEY=ollama

# Model Selection
GENERATION_MODEL_ID=qwen2.5-coder:7b
EMBEDDING_MODEL_ID=nomic-embed-text:latest
EMBEDDING_MODEL_SIZE=768

# Generation Settings
INPUT_DEFAULT_MAX_CHARACTERS=4000
GENERATION_DEFAULT_MAX_TOKENS=1000
GENERATION_DEFAULT_TEMPERATURE=0.1

# PostgreSQL Configuration
POSTGRES_HOST=pgvector
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=change_me_secure_password
POSTGRES_MAIN_DATABASE=minirag

# Vector Database Configuration
VECTOR_DB_BACKEND=QDRANT
VECTOR_DB_PATH=http://qdrant:6333
VECTOR_DB_DISTANCE_METHOD=Cosine
VECTOR_DB_PGVEC_INDEX_THRESHOLD=1000

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://:change_me_redis_password@redis:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_TASK_TIME_LIMIT=600
CELERY_TASK_ACKS_LATE=true
CELERY_WORKER_CONCURRENCY=2
CELERY_FLOWER_PASSWORD=change_me_flower_password

# Language Configuration
PRIMARY_LANG=en
DEFAULT_LANG=en
EOF
    echo "✅ Created .env.app"
else
    echo "⏭️  .env.app already exists"
fi

# Create .env.postgres
if [ ! -f ".env.postgres" ]; then
    cat > .env.postgres << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me_secure_password
POSTGRES_DB=minirag
EOF
    echo "✅ Created .env.postgres"
else
    echo "⏭️  .env.postgres already exists"
fi

# Create .env.rabbitmq
if [ ! -f ".env.rabbitmq" ]; then
    cat > .env.rabbitmq << 'EOF'
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
EOF
    echo "✅ Created .env.rabbitmq"
else
    echo "⏭️  .env.rabbitmq already exists"
fi

# Create .env.redis
if [ ! -f ".env.redis" ]; then
    cat > .env.redis << 'EOF'
REDIS_PASSWORD=change_me_redis_password
EOF
    echo "✅ Created .env.redis"
else
    echo "⏭️  .env.redis already exists"
fi

# Create .env.grafana
if [ ! -f ".env.grafana" ]; then
    cat > .env.grafana << 'EOF'
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin_password
GF_USERS_ALLOW_SIGN_UP=false
EOF
    echo "✅ Created .env.grafana"
else
    echo "⏭️  .env.grafana already exists"
fi

# Create .env.postgres-exporter
if [ ! -f ".env.postgres-exporter" ]; then
    cat > .env.postgres-exporter << 'EOF'
DATA_SOURCE_NAME=postgresql://postgres:change_me_secure_password@pgvector:5432/minirag?sslmode=disable
EOF
    echo "✅ Created .env.postgres-exporter"
else
    echo "⏭️  .env.postgres-exporter already exists"
fi

echo ""
echo "✅ Environment files setup complete!"
echo ""
echo "⚠️  IMPORTANT: Please update the passwords in the .env files before deploying!"
echo "   - .env.app (POSTGRES_PASSWORD, CELERY_RESULT_BACKEND, CELERY_FLOWER_PASSWORD)"
echo "   - .env.postgres (POSTGRES_PASSWORD)"
echo "   - .env.redis (REDIS_PASSWORD)"
echo "   - .env.postgres-exporter (DATA_SOURCE_NAME)"
