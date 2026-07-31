#!/bin/bash
set -e
echo "=== Lint ==="
cd apps/api && ruff check . && cd ../..
echo "=== TypeScript Check ==="
cd apps/web && npx tsc --noEmit && cd ../..
echo "=== Tests ==="
cd apps/api && python -m pytest -v --tb=short && cd ../..
echo "=== All checks passed ==="
