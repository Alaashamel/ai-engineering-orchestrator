.PHONY: dev-api dev-web lint test clean migrate

dev-api:
	cd apps/api && uvicorn src.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

lint:
	cd apps/api && ruff check .
	cd apps/web && npx tsc --noEmit

test:
	cd apps/api && pytest -v

test-coverage:
	cd apps/api && pytest --cov=src --cov-report=term-missing

migrate:
	cd apps/api && alembic upgrade head

migrate-create:
	cd apps/api && alembic revision --autogenerate -m "$(name)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
