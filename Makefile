.PHONY: api-deps web-deps db-up db-down dev-api dev-web lint test test-coverage clean migrate

api-deps:
	python -m venv .venv
	.venv/Scripts/python -m pip install --upgrade pip
	.venv/Scripts/python -m pip install -r apps/api/requirements.txt

web-deps:
	cd apps/web && npm install

db-up:
	docker compose up -d postgres redis

db-down:
	docker compose down

dev-api:
	cd apps/api && uvicorn src.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

lint:
	cd apps/api && ruff check .
	cd apps/web && npx tsc --noEmit

test:
	pytest -v apps/api/tests orchestration/tests

test-coverage:
	pytest --cov=apps/api/src --cov=orchestration --cov-report=term-missing apps/api/tests orchestration/tests

migrate:
	cd apps/api && alembic upgrade head

migrate-create:
	cd apps/api && alembic revision --autogenerate -m "$(name)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
