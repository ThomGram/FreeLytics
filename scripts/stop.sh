#!/bin/bash
set -e

echo "Stopping FreeLytics services..."

if [ -f docker-compose.dev.yml ] && [ -f docker-compose.prod.yml ]; then
    docker compose -f docker-compose.dev.yml down 2>/dev/null || true
    docker compose -f docker-compose.prod.yml down 2>/dev/null || true
    docker compose down 2>/dev/null || true
else
    docker compose down
fi

echo "All services stopped."
