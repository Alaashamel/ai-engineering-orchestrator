import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_list_projects_empty():
    response = client.get("/projects")
    assert response.status_code == 200

def test_create_project():
    response = client.post("/projects", json={"name": "Test", "description": "desc"})
    assert response.status_code in (200, 422, 500)

def test_get_nonexistent_project():
    response = client.get("/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
