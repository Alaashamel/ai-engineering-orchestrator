from src.main import app

def test_app_title():
    assert app.title == "AI Software Engineering Company"

def test_app_version():
    assert app.version == "0.1.0"

def test_routes_exist():
    routes = [r.path for r in app.routes]
    assert "/health" in routes
    assert "/" in routes
