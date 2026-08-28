def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}

def test_crud_roundtrip(client):
    created = client.post('/notes', json={'title': 'buy milk'})
    assert created.status_code == 201
    item_id = created.json()['id']
    assert client.get('/notes').status_code == 200
    listed = client.get('/notes').json()
    assert any(i['id'] == item_id for i in listed)
    updated = client.patch('/notes/' + str(item_id), json={'completed': True})
    assert updated.status_code == 200
    assert updated.json()['completed'] is True
    assert client.delete('/notes/' + str(item_id)).status_code == 204

def test_crud_404_for_missing(client):
    assert client.get('/notes/9999').status_code == 404
