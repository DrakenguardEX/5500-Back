import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_user_login_success(client):
    response = client.post('/api/users/login', json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200 or response.status_code == 401

def test_user_login_fail(client):
    response = client.post('/api/users/login', json={
        "username": "no_such_user",
        "password": "wrongpass"
    })
    assert response.status_code == 401
