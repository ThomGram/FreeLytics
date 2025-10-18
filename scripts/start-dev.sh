#!/bin/bash
set -e

echo "Starting FreeLytics in development mode..."
cp .env.dev .env
docker compose -f docker-compose.dev.yml up -d

echo "Services starting..."
echo "Airflow will be available at: http://localhost:8080"
echo "Username: airflow"
echo "Password: airflow"
