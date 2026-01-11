# VPS Environment Configuration

This directory contains environment configuration files for VPS deployment.

## Required Configuration Files

### 1. `.env.app` - Application Configuration

Must include Ollama configuration:

```env
# LLM Configuration for Ollama on VPS
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"

# Ollama endpoint (use container name for internal Docker networking)
OPENAI_API_URL="http://ollama:11434/v1"
OPENAI_API_KEY="ollama"  # Placeholder, not used by Ollama

# Model Selection
GENERATION_MODEL_ID="qwen2.5-coder:1.5b"
EMBEDDING_MODEL_ID="nomic-embed-text"
EMBEDDING_MODEL_SIZE=768
```

### 2. Ollama Resource Configuration (Optional)

You can configure Ollama resource limits in two ways:

#### Option A: Environment Variables (Recommended)

Set these before running `docker compose`:

```bash
export OLLAMA_NUM_THREADS=4
export OLLAMA_CPU_LIMIT=2.0
export OLLAMA_MEMORY_LIMIT=4G
export OLLAMA_CPU_RESERVATION=1.0
export OLLAMA_MEMORY_RESERVATION=2G
export OLLAMA_DEBUG=false

docker compose up -d
```

#### Option B: Create `.env.ollama` file

Create `docker/env/.env.ollama`:

```env
OLLAMA_NUM_THREADS=4
OLLAMA_CPU_LIMIT=2.0
OLLAMA_MEMORY_LIMIT=4G
OLLAMA_CPU_RESERVATION=1.0
OLLAMA_MEMORY_RESERVATION=2G
OLLAMA_DEBUG=false
```

Then load it before docker compose:

```bash
source .env.ollama
docker compose up -d
```

## Resource Recommendations by VPS Size

### Small VPS (2 cores, 4GB RAM)

```env
OLLAMA_NUM_THREADS=2
OLLAMA_CPU_LIMIT=1.5
OLLAMA_MEMORY_LIMIT=2G
OLLAMA_CPU_RESERVATION=0.5
OLLAMA_MEMORY_RESERVATION=1G
```

### Medium VPS (4 cores, 8GB RAM)

```env
OLLAMA_NUM_THREADS=4
OLLAMA_CPU_LIMIT=2.0
OLLAMA_MEMORY_LIMIT=4G
OLLAMA_CPU_RESERVATION=1.0
OLLAMA_MEMORY_RESERVATION=2G
```

### Large VPS (8+ cores, 16GB+ RAM)

```env
OLLAMA_NUM_THREADS=8
OLLAMA_CPU_LIMIT=4.0
OLLAMA_MEMORY_LIMIT=8G
OLLAMA_CPU_RESERVATION=2.0
OLLAMA_MEMORY_RESERVATION=4G
```

## Quick Setup

1. **Create `.env.app`** with Ollama configuration (see above)
2. **Set resource limits** (optional, but recommended):
   ```bash
   export OLLAMA_CPU_LIMIT=2.0
   export OLLAMA_MEMORY_LIMIT=4G
   ```
3. **Start services**:
   ```bash
   cd docker
   docker compose up -d ollama
   ./init-ollama.sh
   docker compose up -d
   ```

## Verification

After deployment, verify Ollama is working:

```bash
# Check Ollama is running
docker compose ps ollama

# List models
docker exec ollama ollama list

# Test API
curl http://localhost:11434/api/tags
```

## Troubleshooting

If Ollama fails to start or crashes:

1. **Check logs**: `docker compose logs ollama`
2. **Reduce memory limit** if VPS has limited RAM
3. **Check disk space**: `df -h` (models need ~2GB)
4. **Verify network**: Ensure `OPENAI_API_URL` in `.env.app` is `http://ollama:11434/v1`

For more details, see `../VPS-DEPLOYMENT.md`
