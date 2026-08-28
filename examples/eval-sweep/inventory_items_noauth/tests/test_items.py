def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}

def test_crud_roundtrip(client):
    created = client.post('/items', json={'title': 'buy milk'})
    assert created.status_code == 201
    item_id = created.json()['id']
    assert client.get('/items').status_code == 200
    listed = client.get('/items').json()
    assert any(i['id'] == item_id for i in listed)
    updated = client.patch('/items/' + str(item_id), json={'completed': True})
    assert updated.status_code == 200
    assert updated.json()['completed'] is True
    assert client.delete('/items/' + str(item_id)).status_code == 204

def test_crud_404_for_missing(client):
    assert client.get('/items/9999').status_code == 404
