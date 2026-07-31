.PHONY: dev-api dev-web lint test clean migrate

# apps/api imports the top-level `orchestration` package; it isn't pip-installed,
# so every target that runs Python there needs the repo root on PYTHONPATH.
ROOT := $(shell pwd)

dev-api:
	cd apps/api && PYTHONPATH=$(ROOT) uvicorn src.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

lint:
	cd apps/api && PYTHONPATH=$(ROOT) ruff check .
	cd apps/web && npx tsc --noEmit

test:
	cd apps/api && PYTHONPATH=$(ROOT) pytest -v

test-coverage:
	cd apps/api && PYTHONPATH=$(ROOT) pytest --cov=src --cov-report=term-missing

migrate:
	cd apps/api && alembic upgrade head

migrate-create:
	cd apps/api && alembic revision --autogenerate -m "$(name)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
