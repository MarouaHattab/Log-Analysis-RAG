# --- Stage 1: Builder ---
FROM ghcr.io/astral-sh/uv:0.6.14-python3.11-bookworm AS builder

WORKDIR /app

# Only install build-time dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies to system
COPY src/requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt --system

# --- Stage 2: Runtime ---
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install ONLY runtime shared libraries (no compilers)
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (site-packages AND bin)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ .

# Create directory structure for Alembic
RUN mkdir -p /app/models/db_schemes/minirag/

COPY docker/minirag/alembic.ini /app/models/db_schemes/minirag/alembic.ini
COPY docker/minirag/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]