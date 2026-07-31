#!/bin/bash
set -e
echo "Deploying to production..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
echo "Running migrations..."
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
echo "Deployment complete!"
