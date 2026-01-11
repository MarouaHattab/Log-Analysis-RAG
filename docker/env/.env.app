APP_NAME="mini-RAG"
APP_VERSION="0.1"

FILE_ALLOWED_TYPES=["text/plain","application/pdf","text/x-log","application/octet-stream"]
FILE_MAX_SIZE=1024
FILE_DEFAULT_CHUNK_SIZE=512000 # 512KB

POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="admin"
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="minirag"

# ========================= LLM Config =========================
GENERATION_BACKEND = "OPENAI"
EMBEDDING_BACKEND = "OPENAI"

OPENAI_API_KEY="not-needed"
OPENAI_API_URL="http://ollama:11434/v1/"
COHERE_API_KEY="not-needed"

GENERATION_MODEL_ID_LITERAL = ["gpt-4o-mini", "qwen2.5-coder:7b"]
GENERATION_MODEL_ID="qwen2.5-coder:7b"
EMBEDDING_MODEL_ID="nomic-embed-text:latest"
EMBEDDING_MODEL_SIZE=768

INPUT_DAFAULT_MAX_CHARACTERS=1024
GENERATION_DAFAULT_MAX_TOKENS=200
GENERATION_DAFAULT_TEMPERATURE=0.1

# ========================= Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND = "PGVECTOR"
VECTOR_DB_PATH = "qdrant_db"
VECTOR_DB_DISTANCE_METHOD = "cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD = 100

# ========================= Template Config =========================
PRIMARY_LANG = "en"
DEFAULT_LANG = "en"

#===Celery task queue config===
CELERY_BROKER_URL="amqp://minirag_user:minirag_rabbitmq_2222@rabbitmq:5672/minirag_vhost"
CELERY_RESULT_BACKEND="redis://:minirag_redis_2222@redis:6379/0"
CELERY_TASK_SERIALIZER="json"
CELERY_TASK_TIME_LIMIT=600
CELERY_TASK_ACKS_LATE=false
CELERY_WORKER_CONCURRENCY=2
CELERY_FLOWER_PASSWORD="minirag_flower_2222"