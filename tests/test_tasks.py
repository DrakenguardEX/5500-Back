import pytest
from app import app
from bson import ObjectId

MOCK_TASK_ID = str(ObjectId())
MOCK_USER_ID = str(ObjectId())

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_all_tasks(client):
    response = client.get('/api/tasks/')
    assert response.status_code in [200]

def test_get_task_by_id(client):
    response = client.get(f'/api/tasks/{MOCK_TASK_ID}')
    assert response.status_code in [200, 404]

def test_update_task(client):
    response = client.put(f'/api/tasks/{MOCK_TASK_ID}', json={
        "title": "Updated",
        "description": "New desc"
    })
    assert response.status_code in [200, 404]

def test_delete_task(client):
    response = client.delete(f'/api/tasks/{MOCK_TASK_ID}')
    assert response.status_code in [200, 404]

def test_get_user_tasks(client):
    response = client.get(f'/api/tasks/user/{MOCK_USER_ID}')
    assert response.status_code in [200, 404]

def test_add_user_task(client):
    response = client.post(f'/api/tasks/user/{MOCK_USER_ID}', json={
        "title": "Personal Task",
        "description": "Some desc"
    })
    assert response.status_code in [201, 404]
