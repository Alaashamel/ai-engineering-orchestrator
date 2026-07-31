# syntax=docker/dockerfile:1
# Build context is the repo root (see docker-compose.yml) because this
# image needs both apps/api and the sibling top-level `orchestration`
# package, which apps/api imports at runtime.
FROM python:3.13-slim AS builder
WORKDIR /app
COPY apps/api/requirements.txt .
RUN pip install --user --no-cache-dirs -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY apps/api/ .
COPY orchestration/ ./orchestration/
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
