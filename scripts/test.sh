#!/bin/bash
set -e
echo "Running tests..."
cd apps/api
python -m pytest -v --tb=short "$@"
