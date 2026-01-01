<div align="center">

# 🤖 Mini RAG App

🐍 Python • ⚡ FastAPI • 🐳 Docker • 🥬 Celery • 🐰 RabbitMQ • 🐘 PostgreSQL • 📊 Prometheus • 📈 Grafana

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-table-of-contents) • [🏗️ Architecture](#-system-architecture) • [📊 Monitoring](#-monitoring--observability)

---

**Mini RAG App** is a production-ready, horizontally scalable implementation of a Retrieval Augmented Generation system. It combines the power of vector databases, distributed task queues, and large language models to deliver accurate, context-aware answers from your documents.

</div>

---

## 📖 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Technology Stack](#-technology-stack)
5. [Services Deep Dive](#-services-deep-dive)
   - [FastAPI Application Server](#1-fastapi-application-server)
   - [Celery Distributed Task Queue](#2-celery-distributed-task-queue)
   - [RabbitMQ Message Broker](#3-rabbitmq-message-broker)
   - [Redis Cache & Results Backend](#4-redis-cache--results-backend)
   - [PostgreSQL with pgvector](#5-postgresql-with-pgvector)
   - [Qdrant Vector Database](#6-qdrant-vector-database)
6. [Monitoring & Observability](#-monitoring--observability)
7. [Quick Start](#-quick-start)
8. [Configuration Reference](#-configuration-reference)
9. [API Documentation](#-api-documentation)
10. [Development Guide](#-development-guide)
11. [Troubleshooting](#-troubleshooting)
12. [Contributing](#-contributing)

---

## 🎯 Overview

### What is RAG?

**Retrieval Augmented Generation (RAG)** is an AI architecture that enhances Large Language Model (LLM) responses by grounding them in factual, retrieved information. Instead of relying solely on the model's training data, RAG systems:

1. **Retrieve** relevant documents from a knowledge base using semantic search
2. **Augment** the LLM prompt with this contextual information
3. **Generate** accurate, source-backed responses

### Why Mini RAG App?

| Challenge | Solution |
| --------- | -------- |
| LLMs hallucinate facts | Responses grounded in your actual documents |
| Static training data | Dynamic knowledge base you can update anytime |
| No source attribution | Full traceability to source documents |
| Generic responses | Domain-specific answers from your content |
| Scalability concerns | Distributed architecture with Celery workers |

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 📤 Document Management
- **Multi-format support**: PDF and TXT files
- **Automatic chunking**: Configurable size with overlap
- **Project isolation**: Separate knowledge bases per project
- **Metadata extraction**: Preserve document context

</td>
<td width="50%">

### 🧠 Intelligent Search
- **Semantic search**: Beyond keyword matching
- **Vector embeddings**: State-of-the-art models
- **Dual vector DB**: pgvector and Qdrant support
- **Similarity scoring**: Ranked results by relevance

</td>
</tr>
<tr>
<td width="50%">

### 💬 Conversational AI
- **Multi-turn chat**: Context-aware conversations
- **Query refinement**: Automatic follow-up handling
- **Markdown responses**: Rich formatted answers
- **Source citations**: Know where answers come from

</td>
<td width="50%">

### ⚡ Enterprise Ready
- **Async processing**: Non-blocking operations
- **Task queuing**: Celery with RabbitMQ
- **Full observability**: Prometheus + Grafana
- **Containerized**: Docker Compose deployment

</td>
</tr>
</table>

---

## 🏗️ System Architecture

### High-Level Overview

```mermaid
graph TB
    subgraph Client["🌐 Client Layer"]
        Browser["Web Browser"]
        API_Client["API Client"]
    end

    subgraph Gateway["🚪 Gateway Layer"]
        Nginx["Nginx Reverse Proxy<br/>Port 80"]
    end

    subgraph Application["⚡ Application Layer"]
        FastAPI["FastAPI Server<br/>Port 8000"]
        CeleryWorker["Celery Workers<br/>(2 concurrent)"]
        CeleryBeat["Celery Beat<br/>(Scheduler)"]
    end

    subgraph Messaging["📨 Message Queue Layer"]
        RabbitMQ["RabbitMQ<br/>Port 5672 | 15672"]
        Redis["Redis<br/>Port 6379"]
    end

    subgraph Storage["💾 Storage Layer"]
        PostgreSQL["PostgreSQL + pgvector<br/>Port 5400"]
        Qdrant["Qdrant Vector DB<br/>Port 6333"]
        FileStorage["File Storage<br/>(Docker Volume)"]
    end

    subgraph AI["🤖 AI Layer"]
        Ollama["Ollama<br/>Local LLM"]
        OpenAI["OpenAI API<br/>Cloud LLM"]
    end

    subgraph Monitoring["📊 Monitoring Layer"]
        Prometheus["Prometheus<br/>Port 9090"]
        Grafana["Grafana<br/>Port 3000"]
        Flower["Flower<br/>Port 5555"]
        NodeExporter["Node Exporter<br/>Port 9100"]
        PGExporter["PG Exporter<br/>Port 9187"]
    end

    Browser --> Nginx
    API_Client --> Nginx
    Nginx --> FastAPI

    FastAPI --> RabbitMQ
    FastAPI --> PostgreSQL
    FastAPI --> Qdrant
    FastAPI --> Ollama
    FastAPI --> OpenAI
    FastAPI --> FileStorage

    RabbitMQ --> CeleryWorker
    CeleryBeat --> RabbitMQ
    CeleryWorker --> Redis
    CeleryWorker --> PostgreSQL
    CeleryWorker --> Qdrant
    CeleryWorker --> Ollama
    CeleryWorker --> FileStorage

    FastAPI --> Prometheus
    NodeExporter --> Prometheus
    PGExporter --> Prometheus
    Prometheus --> Grafana
    CeleryWorker --> Flower
    RabbitMQ --> Flower

    style FastAPI fill:#009688,color:#fff
    style CeleryWorker fill:#37814A,color:#fff
    style RabbitMQ fill:#FF6600,color:#fff
    style Redis fill:#DC382D,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style Prometheus fill:#E6522C,color:#fff
```

### Request Flow: Document Processing Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant N as 🚪 Nginx
    participant F as 🚀 FastAPI
    participant R as 🐰 RabbitMQ
    participant C as ⚡ Celery Worker
    participant D as 🐘 PostgreSQL
    participant V as 🔮 pgvector
    participant L as 🤖 LLM

    rect rgb(240, 248, 255)
        Note over U,F: Phase 1: Document Upload
        U->>N: POST /upload (multipart/form-data)
        N->>F: Forward request
        F->>F: Validate file (type, size)
        F->>D: Store asset metadata
        F-->>U: ✅ file_id returned
    end

    rect rgb(255, 248, 240)
        Note over U,L: Phase 2: Processing & Indexing
        U->>F: POST /process-and-push
        F->>R: Enqueue task
        F-->>U: ✅ task_id returned

        R->>C: Deliver task
        C->>C: Read file from storage
        C->>C: Split into chunks
        C->>D: Store chunks
        C->>L: Generate embeddings
        L-->>C: Vector arrays
        C->>V: Store vectors
        C->>R: Task complete
    end

    rect rgb(240, 255, 240)
        Note over U,L: Phase 3: Query & Answer
        U->>F: POST /answer {"text": "..."}
        F->>L: Embed query
        L-->>F: Query vector
        F->>V: Similarity search
        V-->>F: Top-K chunks
        F->>L: Generate with context
        L-->>F: AI response
        F-->>U: ✅ Answer + sources
    end
```

### Database Schema

```mermaid
erDiagram
    PROJECTS {
        int project_id PK
        string project_name
        timestamp created_at
        timestamp updated_at
    }

    ASSETS {
        int asset_id PK
        int asset_project_id FK
        string asset_name
        string asset_type
        bigint asset_size
        timestamp created_at
    }

    DATA_CHUNKS {
        int data_chunk_id PK
        int chunk_project_id FK
        int chunk_asset_id FK
        text chunk_text
        jsonb chunk_metadata
        int chunk_order
        timestamp created_at
    }

    VECTOR_COLLECTION {
        bigint id PK
        text text
        vector_768 vector
        jsonb metadata
        int chunk_id FK
    }

    CELERY_TASK_EXECUTIONS {
        int execution_id PK
        string task_name
        jsonb task_args
        string celery_task_id
        string status
        jsonb result
        timestamp created_at
        timestamp updated_at
    }

    PROJECTS ||--o{ ASSETS : "contains"
    PROJECTS ||--o{ DATA_CHUNKS : "contains"
    ASSETS ||--o{ DATA_CHUNKS : "source"
    DATA_CHUNKS ||--|| VECTOR_COLLECTION : "embedded"
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| ----- | ---------- | ------- |
| **Web Framework** | FastAPI | Async REST API with automatic OpenAPI docs |
| **Task Queue** | Celery 5.3+ | Distributed task processing |
| **Message Broker** | RabbitMQ 4.1 | Reliable message delivery with AMQP |
| **Cache/Backend** | Redis 8.0 | Task results storage and caching |
| **Database** | PostgreSQL 17 | Relational data with pgvector extension |
| **Vector DB** | Qdrant / pgvector | Semantic similarity search |
| **Reverse Proxy** | Nginx | Load balancing and SSL termination |
| **LLM Provider** | Ollama / OpenAI | Text generation and embeddings |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Containerization** | Docker Compose | Multi-container orchestration |

---

## 📦 Services Deep Dive

### 1. FastAPI Application Server

The core REST API handling all client requests with async/await patterns.

```mermaid
graph LR
    subgraph FastAPI["FastAPI Application"]
        Routes["Routes Layer"]
        Controllers["Controllers"]
        Models["Data Models"]
        Stores["Provider Stores"]
    end

    Routes --> Controllers
    Controllers --> Models
    Controllers --> Stores

    Stores --> LLM["LLM Providers"]
    Stores --> VectorDB["Vector Stores"]
    Models --> PostgreSQL["PostgreSQL"]

    style FastAPI fill:#009688,color:#fff
```

| Property | Details |
| -------- | ------- |
| **Container** | `fastapi` |
| **Internal Port** | `8000` |
| **External Port** | `80` (via Nginx) |
| **Health Check** | `GET /api/v1/` |
| **API Docs** | `http://localhost:8000/docs` |
| **Metrics** | `GET /TrhBVe_m5gg2002_E5VVqS` |

**Key Endpoints:**

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/api/v1/data/upload/{project_id}` | Upload document to project |
| `POST` | `/api/v1/data/process-and-push/{project_id}` | Chunk, embed, and index |
| `GET` | `/api/v1/nlp/index/info/{project_id}` | Get collection statistics |
| `POST` | `/api/v1/nlp/index/search/{project_id}` | Semantic similarity search |
| `POST` | `/api/v1/nlp/index/answer/{project_id}` | RAG question answering |

---

### 2. Celery Distributed Task Queue

Handles CPU-intensive and long-running operations asynchronously.

```mermaid
graph TB
    subgraph Celery["Celery Ecosystem"]
        direction TB
        Beat["🕐 Celery Beat<br/>(Scheduler)"]
        Worker1["⚡ Worker 1"]
        Worker2["⚡ Worker 2"]
        Flower["🌸 Flower<br/>(Monitor)"]
    end

    subgraph Queues["Task Queues"]
        Q1["default"]
        Q2["file_processing"]
        Q3["data_indexing"]
    end

    subgraph Tasks["Registered Tasks"]
        T1["process_project_files"]
        T2["index_data_content"]
        T3["push_after_process_task"]
        T4["process_and_push_workflow"]
        T5["clean_old_tasks"]
    end

    Beat -->|"Schedule"| Q1
    Q1 --> Worker1
    Q2 --> Worker1
    Q3 --> Worker2

    Worker1 --> T1
    Worker1 --> T5
    Worker2 --> T2
    Worker2 --> T3

    Worker1 -.-> Flower
    Worker2 -.-> Flower

    style Beat fill:#9C27B0,color:#fff
    style Worker1 fill:#37814A,color:#fff
    style Worker2 fill:#37814A,color:#fff
    style Flower fill:#E91E63,color:#fff
```

#### Celery Components

| Component | Container | Command | Purpose |
| --------- | --------- | ------- | ------- |
| **Worker** | `celery-worker` | `celery -A celery_app worker` | Execute background tasks |
| **Beat** | `celery-beat` | `celery -A celery_app beat` | Schedule periodic tasks |
| **Flower** | `flower` | `celery -A celery_app flower` | Web-based monitoring |

#### Task Configuration

```python
# Task with automatic retry on failure
@celery_app.task(
    bind=True,
    name="tasks.file_processing.process_project_files",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def process_project_files(self, project_id, file_id, chunk_size, overlap_size, do_reset):
    # Task implementation
    ...
```

#### Task Workflow Chain

```mermaid
graph LR
    A["process_and_push_workflow"] --> B["process_project_files"]
    B -->|"on success"| C["push_after_process_task"]
    C --> D["index_data_content"]

    style A fill:#9C27B0,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#4CAF50,color:#fff
    style D fill:#FF9800,color:#fff
```

---

### 3. RabbitMQ Message Broker

Enterprise-grade message broker ensuring reliable task delivery.

```mermaid
graph LR
    subgraph Producers
        FastAPI["FastAPI"]
        Beat["Celery Beat"]
    end

    subgraph RabbitMQ["RabbitMQ Broker"]
        Exchange["celery Exchange<br/>(direct)"]
        Q1["Queue: default"]
        Q2["Queue: file_processing"]
        Q3["Queue: data_indexing"]
    end

    subgraph Consumers
        W1["Worker 1"]
        W2["Worker 2"]
    end

    FastAPI -->|"publish"| Exchange
    Beat -->|"publish"| Exchange

    Exchange -->|"route"| Q1
    Exchange -->|"route"| Q2
    Exchange -->|"route"| Q3

    Q1 -->|"consume"| W1
    Q2 -->|"consume"| W1
    Q3 -->|"consume"| W2

    style Exchange fill:#FF6600,color:#fff
```

| Property | Value |
| -------- | ----- |
| **Container** | `rabbitmq` |
| **AMQP Port** | `5672` |
| **Management UI** | `http://localhost:15672` |
| **Virtual Host** | `minirag_vhost` |
| **Default User** | Configured in `.env.rabbitmq` |

**Why RabbitMQ?**

- ✅ **Reliability**: Message persistence survives broker restarts
- ✅ **Acknowledgments**: Tasks confirmed only after completion
- ✅ **Routing**: Flexible message routing with exchanges
- ✅ **Management**: Built-in web UI for monitoring
- ✅ **Clustering**: Horizontal scaling support

---

### 4. Redis Cache & Results Backend

High-performance in-memory store for task results and caching.

| Property | Value |
| -------- | ----- |
| **Container** | `redis` |
| **Port** | `6379` |
| **Persistence** | AOF (Append Only File) |
| **Authentication** | Password required |
| **Max Memory** | Configured via Redis settings |

**Use Cases in Mini RAG:**

| Use Case | Description |
| -------- | ----------- |
| **Task Results** | Store Celery task outcomes for retrieval |
| **Task State** | Track PENDING, STARTED, SUCCESS, FAILURE |
| **Rate Limiting** | Prevent API abuse (optional) |
| **Session Cache** | Store temporary user sessions |

---

### 5. PostgreSQL with pgvector

Relational database extended with vector similarity search capabilities.

| Property | Value |
| -------- | ----- |
| **Container** | `pgvector` |
| **Image** | `pgvector/pgvector:0.8.0-pg17` |
| **External Port** | `5400` |
| **Internal Port** | `5432` |
| **Database** | `minirag` |
| **Extension** | pgvector for vector operations |

**Vector Operations Supported:**

```sql
-- Create vector column
ALTER TABLE collection ADD COLUMN vector vector(768);

-- Cosine similarity search
SELECT * FROM collection
ORDER BY vector <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- Create HNSW index for fast search
CREATE INDEX ON collection
USING hnsw (vector vector_cosine_ops);
```

---

### 6. Qdrant Vector Database

Alternative dedicated vector database for high-performance similarity search.

| Property | Value |
| -------- | ----- |
| **Container** | `qdrant` |
| **HTTP Port** | `6333` |
| **gRPC Port** | `6334` |
| **Dashboard** | `http://localhost:6333/dashboard` |
| **Storage** | Persistent volume |

---

## 📊 Monitoring & Observability

### Monitoring Architecture

```mermaid
graph TB
    subgraph Targets["📡 Metric Sources"]
        FastAPI["FastAPI<br/>/metrics"]
        Node["Node Exporter<br/>:9100"]
        PG["PostgreSQL Exporter<br/>:9187"]
        RMQ["RabbitMQ<br/>:15692"]
    end

    subgraph Collection["📥 Collection"]
        Prometheus["Prometheus<br/>:9090"]
    end

    subgraph Visualization["📊 Visualization"]
        Grafana["Grafana<br/>:3000"]
    end

    subgraph Alerting["🚨 Alerting"]
        AlertManager["Alert Manager"]
    end

    subgraph TaskMon["⚡ Task Monitoring"]
        Flower["Flower<br/>:5555"]
        CeleryWorker["Celery Workers"]
    end

    FastAPI -->|"scrape /15s"| Prometheus
    Node -->|"scrape /15s"| Prometheus
    PG -->|"scrape /15s"| Prometheus
    RMQ -->|"scrape /15s"| Prometheus

    Prometheus --> Grafana
    Prometheus --> AlertManager
    CeleryWorker --> Flower

    style Prometheus fill:#E6522C,color:#fff
    style Grafana fill:#F46800,color:#fff
    style Flower fill:#37814A,color:#fff
```

### Prometheus

Metrics collection and storage with PromQL query language.

| Property | Value |
| -------- | ----- |
| **Container** | `prometheus` |
| **Port** | `9090` |
| **Config** | `docker/prometheus/prometheus.yml` |
| **Retention** | 15 days (default) |
| **Storage** | Persistent volume |

**Access:** `http://localhost:9090`

### Grafana

Beautiful dashboards for metrics visualization.

| Property | Value |
| -------- | ----- |
| **Container** | `grafana` |
| **Port** | `3000` |
| **Default Credentials** | Set in `.env.grafana` |

**Access:** `http://localhost:3000`

**Recommended Dashboards:**

1. Node Exporter Full (ID: 1860)
2. PostgreSQL Database (ID: 9628)
3. RabbitMQ Overview (ID: 10991)

### Flower

Real-time Celery task monitoring.

| Property | Value |
| -------- | ----- |
| **Container** | `flower` |
| **Port** | `5555` |
| **Authentication** | Password protected |

**Access:** `http://localhost:5555`

**Features:**

- Real-time task progress
- Worker status and statistics
- Task history and details
- Broker connection monitoring

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Purpose |
| ----------- | ------- | ------- |
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Ollama | Latest | Local LLM (optional) |
| Git | Any | Clone repository |

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/mini-rag-app.git
cd mini-rag-app
```

### Step 2: Configure Environment

```bash
cd docker/env

# Copy all example files
cp .env.app.example .env.app
cp .env.postgres.example .env.postgres
cp .env.redis.example .env.redis
cp .env.rabbitmq.example .env.rabbitmq
cp .env.grafana.example .env.grafana
```

**Edit `.env.app` for LLM configuration:**

```env
# For Ollama (local, free)
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"
OPENAI_API_KEY="not-needed"
OPENAI_API_URL="http://host.docker.internal:11434/v1/"
GENERATION_MODEL_ID="qwen2.5-coder:7b"
EMBEDDING_MODEL_ID="nomic-embed-text"
EMBEDDING_MODEL_SIZE=768
```

### Step 3: Start Ollama (Optional - for local LLM)

```bash
# Install Ollama from https://ollama.ai

# Pull required models
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

# Start server
ollama serve
```

### Step 4: Launch Services

```bash
cd docker
docker-compose up -d
```

**Services Started:**

| Service | Port | URL |
| ------- | ---- | --- |
| Web UI | 80 | http://localhost |
| FastAPI | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Flower | 5555 | http://localhost:5555 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |
| RabbitMQ | 15672 | http://localhost:15672 |
| Qdrant | 6333 | http://localhost:6333/dashboard |

### Step 5: Verify Deployment

```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs -f fastapi celery-worker

# Test API
curl http://localhost:8000/api/v1/
```

---

## ⚙️ Configuration Reference

### Environment Files

| File | Description |
| ---- | ----------- |
| `.env.app` | Main application configuration |
| `.env.postgres` | PostgreSQL database credentials |
| `.env.redis` | Redis authentication |
| `.env.rabbitmq` | RabbitMQ user and vhost |
| `.env.grafana` | Grafana admin credentials |
| `.env.postgres-exporter` | PostgreSQL exporter connection |

### Application Settings (`.env.app`)

```env
# ==================== Application ====================
APP_NAME="mini-rag"
APP_VERSION="0.1"

# ==================== File Processing ====================
FILE_ALLOWED_TYPES=["text/plain","application/pdf"]
FILE_MAX_SIZE=10                    # Maximum file size in MB
FILE_DEFAULT_CHUNK_SIZE=512000      # Chunk size in bytes

# ==================== Database ====================
POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="admin"
POSTGRES_HOST="pgvector"            # Docker service name
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="minirag"

# ==================== LLM Configuration ====================
GENERATION_BACKEND="OPENAI"         # OPENAI or COHERE
EMBEDDING_BACKEND="OPENAI"          # OPENAI or COHERE
OPENAI_API_KEY="your-key"
OPENAI_API_URL="http://host.docker.internal:11434/v1/"

# Model settings
GENERATION_MODEL_ID="qwen2.5-coder:7b"
EMBEDDING_MODEL_ID="nomic-embed-text"
EMBEDDING_MODEL_SIZE=768

# Generation limits
INPUT_DEFAULT_MAX_CHARACTERS=4096
GENERATION_DEFAULT_MAX_TOKENS=4096
GENERATION_DEFAULT_TEMPERATURE=0.1

# ==================== Vector Database ====================
VECTOR_DB_BACKEND="PGVECTOR"        # PGVECTOR or QDRANT
VECTOR_DB_DISTANCE_METHOD="cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD=500

# ==================== Celery ====================
CELERY_BROKER_URL="amqp://user:pass@rabbitmq:5672/vhost"
CELERY_RESULT_BACKEND="redis://:pass@redis:6379/0"
CELERY_TASK_SERIALIZER="json"
CELERY_TASK_TIME_LIMIT=600          # 10 minutes
CELERY_TASK_ACKS_LATE=false
CELERY_WORKER_CONCURRENCY=2

# ==================== Templates ====================
PRIMARY_LANG="en"
DEFAULT_LANG="en"
```

---

## 📚 API Documentation

### Interactive Documentation

Once running, access the auto-generated API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoint Reference

#### Data Management

| Method | Endpoint | Description | Request Body |
| ------ | -------- | ----------- | ------------ |
| `POST` | `/api/v1/data/upload/{project_id}` | Upload document | `multipart/form-data` |
| `POST` | `/api/v1/data/process/{project_id}` | Process documents | `ProcessRequest` |
| `POST` | `/api/v1/data/process-and-push/{project_id}` | Process + Index | `ProcessRequest` |

#### NLP Operations

| Method | Endpoint | Description | Request Body |
| ------ | -------- | ----------- | ------------ |
| `GET` | `/api/v1/nlp/index/info/{project_id}` | Get index info | - |
| `POST` | `/api/v1/nlp/index/push/{project_id}` | Index to vector DB | `PushRequest` |
| `POST` | `/api/v1/nlp/index/search/{project_id}` | Semantic search | `SearchRequest` |
| `POST` | `/api/v1/nlp/index/answer/{project_id}` | RAG Q&A | `SearchRequest` |

### Example: Complete Workflow

```bash
# 1. Upload a document
curl -X POST "http://localhost/api/v1/data/upload/1" \
  -F "file=@document.pdf"

# Response: {"signal": "file_upload_success", "file_id": "abc123_document.pdf"}

# 2. Process and index
curl -X POST "http://localhost/api/v1/data/process-and-push/1" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 500,
    "overlap_size": 50,
    "do_reset": 1,
    "file_id": "abc123_document.pdf"
  }'

# Response: {"signal": "process_and_push_workflow_ready", "workflow_task_id": "..."}

# 3. Check index status
curl "http://localhost/api/v1/nlp/index/info/1"

# Response: {"collection_info": {"record_count": 42, ...}}

# 4. Ask a question
curl -X POST "http://localhost/api/v1/nlp/index/answer/1" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the main topic of this document?",
    "limit": 5
  }'

# Response: {"answer": "Based on the provided documents...", ...}
```

---

## 💻 Development Guide

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
cd src
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Start services (PostgreSQL, Redis, RabbitMQ)
# ... (install locally or use Docker)

# Run migrations
alembic upgrade head

# Start FastAPI
uvicorn main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A celery_app worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A celery_app beat --loglevel=info
```

### Project Structure

```
mini-rag-app/
├── 📂 docker/
│   ├── docker-compose.yml          # All service definitions
│   ├── 📂 env/                      # Environment files
│   │   ├── .env.app
│   │   ├── .env.postgres
│   │   ├── .env.redis
│   │   ├── .env.rabbitmq
│   │   └── .env.grafana
│   ├── 📂 minirag/                  # FastAPI Dockerfile
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── 📂 nginx/                    # Nginx configuration
│   ├── 📂 prometheus/               # Prometheus config
│   └── 📂 rabbitmq/                 # RabbitMQ config
│
├── 📂 src/
│   ├── main.py                      # FastAPI entry point
│   ├── celery_app.py                # Celery configuration
│   │
│   ├── 📂 routes/                   # API endpoints
│   │   ├── base.py
│   │   ├── data.py
│   │   ├── nlp.py
│   │   └── 📂 schemes/              # Pydantic models
│   │
│   ├── 📂 controllers/              # Business logic
│   │   ├── DataController.py
│   │   ├── ProcessController.py
│   │   ├── NLPController.py
│   │   └── ProjectController.py
│   │
│   ├── 📂 models/                   # Database models
│   │   ├── db_schemes.py            # SQLAlchemy models
│   │   ├── ProjectModel.py
│   │   ├── AssetModel.py
│   │   └── ChunkModel.py
│   │
│   ├── 📂 stores/                   # External integrations
│   │   ├── 📂 llm/                  # LLM providers
│   │   │   ├── LLMProviderFactory.py
│   │   │   └── 📂 providers/
│   │   │       ├── OpenAIProvider.py
│   │   │       └── CoHereProvider.py
│   │   │
│   │   └── 📂 vectordb/             # Vector DB providers
│   │       ├── VectorDBProviderFactory.py
│   │       └── 📂 providers/
│   │           ├── PGVectorProvider.py
│   │           └── QdrantDBProvider.py
│   │
│   ├── 📂 tasks/                    # Celery tasks
│   │   ├── file_processing.py
│   │   ├── data_indexing.py
│   │   ├── process_workflow.py
│   │   └── maintenance.py
│   │
│   ├── 📂 templates/                # HTML templates
│   │   └── index.html               # Web UI
│   │
│   └── 📂 helpers/                  # Utilities
│       └── config.py
│
└── README.md
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>❌ "Collection not found or project ID invalid"</b></summary>

**Cause:** The vector collection hasn't been created yet.

**Solution:**

1. Upload a file first: `POST /api/v1/data/upload/1`
2. Process and push: `POST /api/v1/data/process-and-push/1`
3. Wait for Celery task to complete (check Flower: http://localhost:5555)
4. Retry the request

</details>

<details>
<summary><b>❌ Celery tasks stuck in PENDING</b></summary>

**Cause:** Worker not consuming from queues properly.

**Solution:**

```bash
# Check worker logs
docker logs celery-worker --tail 100

# Verify RabbitMQ connection
docker logs rabbitmq --tail 50

# Restart worker
docker restart celery-worker
```

</details>

<details>
<summary><b>❌ "Connection refused" to Ollama</b></summary>

**Cause:** Ollama not running or wrong API URL.

**Solution:**

1. Start Ollama: `ollama serve`
2. Check API URL in `.env.app`:
   - Windows/Mac Docker: `http://host.docker.internal:11434/v1/`
   - Linux Docker: `http://172.17.0.1:11434/v1/`
3. Verify models are pulled: `ollama list`

</details>

<details>
<summary><b>❌ Database connection errors</b></summary>

**Cause:** PostgreSQL not ready or wrong credentials.

**Solution:**

```bash
# Check PostgreSQL health
docker-compose ps pgvector

# View PostgreSQL logs
docker logs pgvector --tail 50

# Test connection
docker exec -it pgvector psql -U postgres -d minirag -c "\dt"
```

</details>

### Useful Commands

```bash
# View all logs
docker-compose logs -f

# Restart specific service
docker restart fastapi

# View container resource usage
docker stats

# Execute command in container
docker exec -it fastapi bash

# Full reset (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python
- Write docstrings for all functions
- Add type hints where possible
- Include tests for new features
- Update documentation as needed

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 🌟 Acknowledgments

Built with these amazing technologies:

**[FastAPI](https://fastapi.tiangolo.com/)** • **[Celery](https://docs.celeryq.dev/)** • **[RabbitMQ](https://www.rabbitmq.com/)** • **[PostgreSQL](https://www.postgresql.org/)** • **[pgvector](https://github.com/pgvector/pgvector)** • **[Docker](https://www.docker.com/)**

---

[⬆ Back to Top](#-mini-rag-app)

**⭐ Star this repository if you find it useful! ⭐**

</div>
