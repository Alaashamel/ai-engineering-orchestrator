from fastapi.testclient import TestClient

def _register(client):
    client.post('/auth/register', json={'username': 'alice', 'password': 'secret123'})

def _token(client) -> str:
    r = client.post('/auth/login', json={'username': 'alice', 'password': 'secret123'})
    assert r.status_code == 200, r.text
    return r.json()['access_token']

def _headers(token):
    return {'Authorization': 'Bearer ' + token}

def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}

def test_register_and_login(client):
    _register(client)
    token = _token(client)
    assert token

def test_login_rejects_bad_password(client):
    _register(client)
    r = client.post('/auth/login', json={'username': 'alice', 'password': 'wrong'})
    assert r.status_code == 401

def test_crud_requires_token(client):
    r = client.get('/todos')
    assert r.status_code == 401

def test_crud_roundtrip(client):
    _register(client)
    headers = _headers(_token(client))
    created = client.post('/todos', json={'title': 'buy milk'}, headers=headers)
    assert created.status_code == 201
    item_id = created.json()['id']
    listed = client.get('/todos', headers=headers)
    assert listed.status_code == 200
    assert any(i['id'] == item_id for i in listed.json())
    updated = client.patch(f'/todos/{item_id}', json={'completed': True}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()['completed'] is True
    deleted = client.delete(f'/todos/{item_id}', headers=headers)
    assert deleted.status_code == 204

def test_crud_404_for_missing(client):
    _register(client)
    headers = _headers(_token(client))
    assert client.get('/todos/9999', headers=headers).status_code == 404
