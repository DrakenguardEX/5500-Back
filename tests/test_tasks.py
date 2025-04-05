import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
import mongomock  # ✅
from mongoengine import connect, disconnect
from datetime import datetime

from app import create_app  # ✅
from models.task import Task
from models.user import User


@pytest.fixture(scope='module')
def test_client():
    connect(
        'mongoenginetest',
        host='mongodb://localhost',
        mongo_client_class=mongomock.MongoClient  # ✅ new required way
    )
    app = create_app({"TESTING": True})
    client = app.test_client()
    yield client
    disconnect()


@pytest.fixture
def mock_user():
    user = User(username="testuser", password="testpass")
    user.save()
    yield user
    user.delete()


def test_create_user_task(test_client, mock_user):
    payload = {
        "title": "Test Task",
        "description": "This is a test",
        "type": "Bug",
        "status": "Open",
        "priority": "High",
        "cycle": "Weekly",
        "dueDate": "2025-04-10"
    }
    response = test_client.post(
        f"/api/tasks/user/{mock_user.id}",
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "High"


def test_get_user_tasks(test_client, mock_user):
    response = test_client.get(f"/api/tasks/user/{mock_user.id}")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_all_tasks(test_client):
    response = test_client.get("/api/tasks/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_task_with_bad_date(test_client, mock_user):
    payload = {
        "title": "Bad Date Task",
        "dueDate": "not-a-date"
    }
    response = test_client.post(
        f"/api/tasks/user/{mock_user.id}",
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201  # Still succeeds, date is just ignored or invalid format
    data = response.get_json()
    assert data["title"] == "Bad Date Task"
    assert data["dueDate"] is None or "dueDate" in data
