#!/bin/bash
set -e
echo "Setting up development environment..."
cd apps/api
python -m venv .venv 2>/dev/null || true
.\.venv\Scripts\pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]"
cd ../..
cd apps/web
npm install
cd ../..
echo "Setup complete!"
