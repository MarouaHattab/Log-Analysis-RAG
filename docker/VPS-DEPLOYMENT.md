# VPS Deployment Guide for Ollama

This guide provides step-by-step instructions for deploying the mini-RAG application with Ollama on a VPS (Virtual Private Server).

## Prerequisites

### VPS Requirements

**Minimum Specifications:**

- **CPU**: 2 cores (4+ recommended)
- **RAM**: 4GB (8GB+ recommended for better performance)
- **Storage**: 20GB+ free space (models require ~2GB)
- **OS**: Ubuntu 20.04+ or Debian 11+ (recommended)

**Recommended Specifications:**

- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: Stable internet connection (for model downloads)

### Software Requirements

1. **Docker** (version 20.10+)
2. **Docker Compose** (version 2.0+)
3. **Git**

## Step 1: VPS Setup

### 1.1 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### 1.3 Configure Docker (Optional but Recommended)

Create or edit `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

## Step 2: Clone and Configure Application

### 2.1 Clone Repository

```bash
cd ~
git clone <your-repo-url> mini-rag-app
cd mini-rag-app/docker
```

### 2.2 Create Environment Files

```bash
cd env

# Copy example files (if they exist)
# For .env.app, you'll need to create it manually with Ollama configuration
```

### 2.3 Configure Ollama Environment Variables

Create or edit `docker/env/.env.app` with the following Ollama configuration:

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

# Embedding model size
EMBEDDING_MODEL_SIZE=768
```

### 2.4 Configure Ollama Resource Limits (Optional)

Create `docker/env/.env.ollama` to customize resource limits:

```env
# CPU Configuration
# Set based on your VPS CPU cores
OLLAMA_NUM_THREADS=4

# Resource Limits
OLLAMA_CPU_LIMIT=2.0          # Maximum CPU cores
OLLAMA_MEMORY_LIMIT=4G         # Maximum RAM (adjust based on VPS)
OLLAMA_CPU_RESERVATION=1.0     # Minimum CPU cores
OLLAMA_MEMORY_RESERVATION=2G   # Minimum RAM

# Debug mode
OLLAMA_DEBUG=false
```

**Resource Recommendations:**

- **2-core VPS, 4GB RAM**: `OLLAMA_NUM_THREADS=2`, `OLLAMA_MEMORY_LIMIT=2G`
- **4-core VPS, 8GB RAM**: `OLLAMA_NUM_THREADS=4`, `OLLAMA_MEMORY_LIMIT=4G`
- **8+ core VPS, 16GB+ RAM**: `OLLAMA_NUM_THREADS=8`, `OLLAMA_MEMORY_LIMIT=8G`

## Step 3: Deploy Services

### 3.1 Start Core Services First

```bash
cd ~/mini-rag-app/docker

# Start databases and dependencies
docker compose up -d pgvector rabbitmq redis qdrant

# Wait for services to be healthy
docker compose ps
```

### 3.2 Start Ollama

```bash
# Start Ollama service
docker compose up -d ollama

# Check Ollama logs
docker compose logs -f ollama
```

Wait until you see Ollama is ready (usually takes 30-60 seconds).

### 3.3 Initialize Ollama Models

```bash
# Make script executable
chmod +x init-ollama.sh

# Run initialization script
./init-ollama.sh
```

This will download:

- `nomic-embed-text:latest` (~274MB) - for embeddings
- `qwen2.5-coder:1.5b` (~1.0GB) - for text generation

**Note**: Model download may take 10-30 minutes depending on your VPS internet speed.

### 3.4 Start Application Services

```bash
# Start all remaining services
docker compose up -d --build

# Check all services are running
docker compose ps
```

## Step 4: Verify Deployment

### 4.1 Check Ollama Status

```bash
# List installed models
docker exec ollama ollama list

# Test Ollama API
curl http://localhost:11434/api/tags

# Test model inference
docker exec ollama ollama run qwen2.5-coder:1.5b "Hello, world!"
```

### 4.2 Check Application Health

```bash
# Check FastAPI health
curl http://localhost:8000/health

# Check service logs
docker compose logs fastapi
docker compose logs celery-worker
```

### 4.3 Access Services

- **FastAPI**: `http://your-vps-ip:8000`
- **Nginx**: `http://your-vps-ip:80`
- **Flower (Celery)**: `http://your-vps-ip:5555`
- **Grafana**: `http://your-vps-ip:3000`
- **Ollama API**: `http://your-vps-ip:11434`

## Step 5: Firewall Configuration

### 5.1 Configure UFW (Ubuntu Firewall)

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application ports (optional, for direct access)
sudo ufw allow 8000/tcp
sudo ufw allow 11434/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 5.2 Configure Cloud Provider Firewall

If using a cloud provider (AWS, DigitalOcean, etc.), configure their firewall/security groups to allow:

- Port 22 (SSH)
- Port 80 (HTTP)
- Port 443 (HTTPS, if using SSL)
- Port 8000 (FastAPI, optional)
- Port 11434 (Ollama, optional - only if needed externally)

## Step 6: Production Optimizations

### 6.1 Set Up SSL/HTTPS (Recommended)

Use Nginx with Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 6.2 Configure Nginx for Production

Update `docker/nginx/default.conf` to include SSL and security headers.

### 6.3 Set Up Auto-restart

Docker Compose already includes `restart: always`, but ensure Docker starts on boot:

```bash
sudo systemctl enable docker
```

### 6.4 Monitor Resources

```bash
# Check resource usage
docker stats

# Check disk space
df -h

# Check memory
free -h
```

## Troubleshooting

### Ollama Container Keeps Restarting

1. **Check logs**: `docker compose logs ollama`
2. **Check resources**: `docker stats ollama`
3. **Reduce memory limit** in `.env.ollama` if VPS has limited RAM
4. **Check disk space**: `df -h` (models need space)

### Models Not Loading

1. **Verify models are downloaded**: `docker exec ollama ollama list`
2. **Re-run initialization**: `./init-ollama.sh`
3. **Check network connectivity**: `docker exec ollama ping -c 3 ollama.com`

### Slow Inference

1. **Increase CPU allocation** in `.env.ollama`
2. **Use smaller models** (already using 1.5b, which is small)
3. **Check VPS CPU/RAM usage**: `htop` or `docker stats`
4. **Consider GPU-enabled VPS** (uncomment GPU config in docker-compose.yml)

### Connection Issues

1. **Verify OPENAI_API_URL** in `.env.app` is `http://ollama:11434/v1`
2. **Check network**: `docker network inspect docker_backend`
3. **Test from FastAPI container**: `docker exec fastapi curl http://ollama:11434/api/tags`

### Out of Memory Errors

1. **Reduce OLLAMA_MEMORY_LIMIT** in `.env.ollama`
2. **Reduce OLLAMA_MAX_LOADED_MODELS** (already set to 2)
3. **Add swap space** to VPS:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## Maintenance

### Update Models

```bash
# Pull latest model versions
docker exec ollama ollama pull nomic-embed-text:latest
docker exec ollama ollama pull qwen2.5-coder:1.5b
```

### Backup Models

```bash
# Backup Ollama volume
docker run --rm -v docker_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz /data
```

### Restore Models

```bash
# Restore Ollama volume
docker run --rm -v docker_ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama-backup.tar.gz -C /
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ollama
docker compose logs -f fastapi
```

## Performance Tuning

### For Low-End VPS (2 cores, 4GB RAM)

```env
# .env.ollama
OLLAMA_NUM_THREADS=2
OLLAMA_CPU_LIMIT=1.5
OLLAMA_MEMORY_LIMIT=2G
OLLAMA_CPU_RESERVATION=0.5
OLLAMA_MEMORY_RESERVATION=1G
```

### For Mid-Range VPS (4 cores, 8GB RAM)

```env
# .env.ollama
OLLAMA_NUM_THREADS=4
OLLAMA_CPU_LIMIT=3.0
OLLAMA_MEMORY_LIMIT=4G
OLLAMA_CPU_RESERVATION=1.0
OLLAMA_MEMORY_RESERVATION=2G
```

### For High-End VPS (8+ cores, 16GB+ RAM)

```env
# .env.ollama
OLLAMA_NUM_THREADS=8
OLLAMA_CPU_LIMIT=6.0
OLLAMA_MEMORY_LIMIT=8G
OLLAMA_CPU_RESERVATION=2.0
OLLAMA_MEMORY_RESERVATION=4G
```

## Support

For issues specific to:

- **Ollama**: Check [Ollama documentation](https://github.com/ollama/ollama)
- **Docker**: Check [Docker documentation](https://docs.docker.com/)
- **Application**: Check main README.md

## Security Notes

1. **Never expose Ollama port (11434) publicly** unless necessary
2. **Use firewall rules** to restrict access
3. **Keep Docker and system updated**
4. **Use strong passwords** for all services
5. **Enable SSL/HTTPS** for production deployments
6. **Regularly backup** your data and models
