#!/bin/bash

echo "=========================================="
echo "  Stopping MQTT Industrial IoT Demo"
echo "=========================================="

# Stop all containers
echo "🛑 Stopping all containers..."
docker-compose down

# Optional: Remove volumes (uncomment if you want to clean up data)
# echo "🗑️  Removing volumes..."
# docker-compose down -v

# Optional: Remove images (uncomment if you want to clean up completely)
# echo "🗑️  Removing images..."
# docker-compose down --rmi all

echo ""
echo "✅ MQTT Demo stopped successfully!"
echo ""
echo "📋 Cleanup Options:"
echo "  Remove volumes:    docker-compose down -v"
echo "  Remove images:     docker-compose down --rmi all"
echo "  Remove everything: docker system prune -a"
echo ""
echo "=========================================="
