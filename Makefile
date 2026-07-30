.PHONY: help dev-api dev-web db-up db-down test lint api-deps web-deps

help:
	@echo "Commands:"
	@echo "  make dev-api     Start API dev server (hot-reload)"
	@echo "  make dev-web     Start web dev server (hot-reload)"
	@echo "  make db-up       Start Postgres + Redis containers"
	@echo "  make db-down     Stop database containers"
	@echo "  make api-deps    Install Python dependencies"
	@echo "  make web-deps    Install Node dependencies"
	@echo "  make test        Run all tests"
	@echo "  make lint        Run linters"

db-up:
	docker compose up -d postgres redis

db-down:
	docker compose down

api-deps:
	cd apps/api && python -m pip install -r requirements.txt

dev-api:
	cd apps/api && uvicorn src.main:app --reload --port 8000

web-deps:
	cd apps/web && npm install

dev-web:
	cd apps/web && npm run dev

test:
	cd apps/api && python -m pytest tests/ -v

lint:
	cd apps/api && ruff check src/ tests/
	cd apps/web && npx tsc --noEmit

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/web/dist apps/web/node_modules .venv
