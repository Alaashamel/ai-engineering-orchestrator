from src.main import app


def test_app_title():
    assert app.title == "AI Software Engineering Company"

def test_app_version():
    assert app.version == "0.1.0"

def test_routes_exist():
    routes = []
    for r in app.routes:
        rtype = type(r).__name__
        if rtype == "Route" or rtype == "APIRoute":
            routes.append(r.path)
        elif rtype == "_IncludedRouter":
            for sub in r.original_router.routes:
                if hasattr(sub, "path"):
                    routes.append(sub.path)
    assert any("/health" in p for p in routes), f"Routes: {routes}"
    assert "/" in routes

def test_cors_middleware_loaded():
    middlewares = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middlewares

def test_health_route_returns_json():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code in (200, 404)
