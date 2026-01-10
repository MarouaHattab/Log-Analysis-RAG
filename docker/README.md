# Docker Deployment Guide

This directory contains all Docker-related configuration for the mini-RAG application, including **Ollama integration** for self-hosted LLM inference.

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

Use the interactive deployment script from the project root:

```bash
cd ..
bash deploy.sh
```

Select option 1 for local Docker Compose deployment. The script will:
- Set up all environment files
- Start all services
- Initialize Ollama with required models
- Display service URLs

### Option 2: Manual Deployment

```bash
# 1. Set up environment files
cd env
for file in .env.example.*; do cp "$file" "${file//.example/}"; done
cd ..

# 2. Start all services
docker compose up -d --build

# 3. Initialize Ollama models
bash init-ollama.sh
```

## 📦 Services Overview

The docker-compose.yml orchestrates the following services:

### Core Application
- **fastapi** (port 8000) - Main API server
- **celery-worker** - Background task processor
- **celery-beat** - Task scheduler
- **flower** (port 5555) - Celery monitoring dashboard
- **nginx** (port 80) - Reverse proxy

### AI/LLM Services
- **ollama** (port 11434) - Self-hosted LLM inference
  - Models: `qwen2.5-coder:1.5b`, `nomic-embed-text:latest`
  - Volume: `ollama_data` (persists downloaded models)
  - GPU support available (see configuration below)

### Databases
- **pgvector** (port 5400) - PostgreSQL with vector extension
- **qdrant** (ports 6333, 6334) - Vector database
- **redis** (port 6379) - Cache and Celery backend
- **rabbitmq** (ports 5672, 15672) - Message broker

### Monitoring
- **prometheus** (port 9090) - Metrics collection
- **grafana** (port 3000) - Metrics visualization
- **node-exporter** (port 9100) - System metrics
- **postgres-exporter** (port 9187) - Database metrics

## 🤖 Ollama Configuration

### Model Initialization

The `init-ollama.sh` script automatically pulls required models:

```bash
bash init-ollama.sh
```

This downloads:
- **nomic-embed-text:latest** (~274MB) - Text embeddings
- **qwen2.5-coder:1.5b** (~1.0GB) - Code generation

### GPU Support

To enable NVIDIA GPU acceleration, uncomment these lines in `docker-compose.yml`:

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

**Prerequisites:**
- NVIDIA GPU with CUDA support
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed

### Manual Model Management

```bash
# List installed models
docker exec ollama ollama list

# Pull a specific model
docker exec ollama ollama pull qwen2.5-coder:1.5b

# Remove a model
docker exec ollama ollama rm qwen2.5-coder:7b

# Test model inference
docker exec ollama ollama run qwen2.5-coder:1.5b "Hello, world!"
```

### Switching Models

To use different models, update these files:

**docker/env/.env.app:**
```env
GENERATION_MODEL_ID="qwen2.5-coder:1.5b"
EMBEDDING_MODEL_ID="nomic-embed-text:latest"
```

**src/.env** (for local development):
```env
GENERATION_MODEL_ID="qwen2.5-coder:1.5b"
EMBEDDING_MODEL_ID="nomic-embed-text:latest"
```

Then pull the new models:
```bash
docker exec ollama ollama pull <model-name>
```

## 🔧 Environment Configuration

### Required Environment Files

Located in `env/` directory:

- **.env.app** - Application configuration (LLM, database, Celery)
- **.env.postgres** - PostgreSQL credentials
- **.env.rabbitmq** - RabbitMQ configuration
- **.env.redis** - Redis password
- **.env.grafana** - Grafana admin credentials
- **.env.postgres-exporter** - Database metrics exporter

### Key Configuration Variables

**LLM Configuration (.env.app):**
```env
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"
OPENAI_API_URL="http://ollama:11434/v1/"
OPENAI_API_KEY="not-needed"

GENERATION_MODEL_ID="qwen2.5-coder:1.5b"
EMBEDDING_MODEL_ID="nomic-embed-text:latest"
EMBEDDING_MODEL_SIZE=768
```

**Database Configuration:**
```env
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="admin"
```

## 🏗️ Architecture

```
┌─────────────┐
│   Nginx     │ ← Reverse Proxy
└──────┬──────┘
       │
┌──────▼──────┐     ┌──────────────┐
│   FastAPI   │────▶│   Ollama     │ ← LLM Inference
└──────┬──────┘     │ - qwen2.5    │
       │            │ - nomic-embed│
       │            └──────────────┘
       │
┌──────▼──────┐     ┌──────────────┐
│  RabbitMQ   │────▶│Celery Worker │
└─────────────┘     └──────┬───────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐   ┌────────▼────────┐  ┌──────▼──────┐
│  PostgreSQL │   │     Qdrant      │  │    Redis    │
│  (pgvector) │   │  (Vector DB)    │  │   (Cache)   │
└─────────────┘   └─────────────────┘  └─────────────┘
```

## 📊 Service URLs

After deployment, access services at:

| Service | URL | Credentials |
|---------|-----|-------------|
| FastAPI API | http://localhost:8000 | - |
| API Documentation | http://localhost:8000/docs | - |
| Nginx | http://localhost:80 | - |
| Flower (Celery) | http://localhost:5555 | Set in .env.app |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| RabbitMQ | http://localhost:15672 | Set in .env.rabbitmq |
| Qdrant | http://localhost:6333 | - |
| Ollama API | http://localhost:11434 | - |

## 🛠️ Common Operations

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f fastapi
docker compose logs -f ollama
docker compose logs -f celery-worker
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart fastapi
docker compose restart ollama
```

### Stop Services

```bash
docker compose down
```

### Clean Everything (including volumes)

```bash
docker compose down -v
```

### Database Migrations

```bash
# Run migrations
docker exec fastapi alembic -c /app/models/db_schemes/minirag/alembic.ini upgrade head

# Create new migration
docker exec fastapi alembic -c /app/models/db_schemes/minirag/alembic.ini revision --autogenerate -m "description"
```

## 🐛 Troubleshooting

### Ollama Service Not Starting

**Check logs:**
```bash
docker compose logs ollama
```

**Verify health:**
```bash
curl http://localhost:11434/api/tags
```

**Restart service:**
```bash
docker compose restart ollama
```

### Models Not Loading

**Check available disk space:**
```bash
docker system df
```

**Manually pull models:**
```bash
docker exec ollama ollama pull nomic-embed-text:latest
docker exec ollama ollama pull qwen2.5-coder:1.5b
```

### FastAPI Can't Connect to Ollama

**Verify network connectivity:**
```bash
docker exec fastapi curl http://ollama:11434/api/tags
```

**Check environment variables:**
```bash
docker exec fastapi env | grep OPENAI_API_URL
```

### Out of Memory Errors

**Reduce model size** - Use smaller models:
- `qwen2.5-coder:0.5b` instead of `1.5b`
- `all-minilm:latest` instead of `nomic-embed-text`

**Increase Docker memory limit** in Docker Desktop settings

### Database Connection Issues

**Check PostgreSQL health:**
```bash
docker compose ps pgvector
docker compose logs pgvector
```

**Verify connection from FastAPI:**
```bash
docker exec fastapi pg_isready -h pgvector -p 5432 -U postgres
```

## 🔒 Production Considerations

### Security

1. **Change default passwords** in all .env files
2. **Enable HTTPS** with proper SSL certificates in Nginx
3. **Restrict network access** using Docker networks
4. **Use secrets management** for sensitive data

### Performance

1. **Enable GPU** for Ollama if available
2. **Scale Celery workers** based on workload:
   ```bash
   docker compose up -d --scale celery-worker=3
   ```
3. **Tune PostgreSQL** connection pool settings
4. **Configure Redis** persistence and eviction policies

### Monitoring

1. **Set up Grafana dashboards** for all services
2. **Configure Prometheus alerts** for critical metrics
3. **Enable log aggregation** (e.g., ELK stack)
4. **Monitor Ollama** model performance and response times

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

## 🆘 Support

For issues or questions:
1. Check the [main README](../README.md)
2. Review service logs: `docker compose logs -f`
3. Open an issue on GitHub