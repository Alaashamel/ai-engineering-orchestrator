# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dirs -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
