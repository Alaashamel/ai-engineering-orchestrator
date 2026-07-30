#!/bin/bash
echo "=== Container Status ==="
docker-compose ps
echo ""
echo "=== Resource Usage ==="
docker stats --no-stream
