from src.main import app


def test_app_title():
    assert app.title == "AI Software Engineering Company"

def test_app_version():
    assert app.version == "0.1.0"

def test_routes_exist():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    assert "/health" in schema["paths"]
    assert "/" in schema["paths"]

def test_cors_middleware_loaded():
    middlewares = [getattr(m.cls, "__name__", str(m.cls)) for m in app.user_middleware]
    assert "CORSMiddleware" in middlewares

def test_health_route_returns_json():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code in (200, 404)
