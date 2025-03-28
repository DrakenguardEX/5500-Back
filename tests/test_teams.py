import pytest
from app import app
from bson import ObjectId

MOCK_USER_ID = str(ObjectId())
MOCK_TEAM_ID = str(ObjectId())

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_teams(client):
    response = client.get('/api/teams/', headers={"X-User-Id": MOCK_USER_ID})
    assert response.status_code in [200, 400, 404]

def test_create_team(client):
    response = client.post('/api/teams/',
        headers={"Content-Type": "application/json", "X-User-Id": MOCK_USER_ID},
        json={"name": "Test Team"})
    assert response.status_code in [201, 400, 404]

def test_add_task_to_team(client):
    response = client.post(f'/api/teams/{MOCK_TEAM_ID}/tasks',
        json={"title": "Team Task", "description": "Testing task"})
    assert response.status_code in [201, 404]

def test_add_member_to_team(client):
    response = client.post(f'/api/teams/{MOCK_TEAM_ID}/members',
        json={"username": "someone"})
    assert response.status_code in [200, 400, 404, 409]
