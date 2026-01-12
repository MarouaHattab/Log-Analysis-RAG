#!/bin/bash
# Script to clean Docker images and rebuild everything

set -e

echo "🧹 Cleaning Docker environment..."
echo "=================================="

# Stop and remove all containers
echo "Stopping containers..."
docker compose down

# Remove all containers (including stopped ones)
echo "Removing containers..."
docker compose rm -f

# Remove images (optional - uncomment if you want to remove images too)
echo "Removing images..."
docker compose down --rmi all

# Remove volumes (optional - uncomment if you want to remove data too)
# WARNING: This will delete all data including models and databases!
# echo "Removing volumes..."
# docker compose down -v

# Clean up dangling images
echo "Cleaning up dangling images..."
docker image prune -f

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Rebuilding and starting services..."
echo "=================================="

# Rebuild and start everything
docker compose up -d --build
docker compose up --build
echo ""
echo "✅ Services are starting!"
echo ""
echo "Monitor the logs with:"
echo "  docker compose logs -f ollama-init"
echo ""
echo "Check service status with:"
echo "  docker compose ps"
