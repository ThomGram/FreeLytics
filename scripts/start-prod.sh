#!/bin/bash
set -e

echo "Starting FreeLytics in production mode..."
cp .env.prod .env
docker compose -f docker-compose.prod.yml up -d

echo "Services starting..."
echo "Airflow will be available at: http://localhost:8080"
echo "Keycloak admin will be available at: http://localhost:8081"
echo "Keycloak admin username: admin"
echo "Keycloak admin password: admin"
echo ""
echo "Configure Keycloak realm 'freelytics' and client 'airflow' before using Airflow"
