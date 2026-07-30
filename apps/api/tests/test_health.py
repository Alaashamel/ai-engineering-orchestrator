from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-software-engineering-api"
    assert data["version"] == "0.1.0"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AI Software Engineering Company API" in data["message"]
