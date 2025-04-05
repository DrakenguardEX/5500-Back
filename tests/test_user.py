import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
import mongomock
from mongoengine import connect, disconnect

from app import create_app
from models.user import User


@pytest.fixture(scope='module')
def test_client():
    connect(
        'mongoenginetest',
        host='mongodb://localhost',
        mongo_client_class=mongomock.MongoClient
    )
    app = create_app({"TESTING": True})
    client = app.test_client()
    yield client
    disconnect()


@pytest.fixture
def test_user():
    user = User(username="testuser", password="testpass")
    user.save()
    yield user
    user.delete()


def test_register_user(test_client):
    payload = {
        "username": "newuser",
        "password": "newpass"
    }
    response = test_client.post(
        "/api/users/register",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "user_id" in data


def test_register_duplicate_user(test_client, test_user):
    payload = {
        "username": "testuser",
        "password": "testpass"
    }
    response = test_client.post(
        "/api/users/register",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 409
    assert response.get_json()["message"] == "Username already exists."


def test_register_missing_fields(test_client):
    response = test_client.post(
        "/api/users/register",
        data=json.dumps({"username": "incomplete"}),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "Username and password required" in response.get_json()["message"]


def test_login_success(test_client, test_user):
    payload = {
        "username": "testuser",
        "password": "testpass"
    }
    response = test_client.post(
        "/api/users/login",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "fake-token-for-testuser" in data["token"]


def test_login_failure(test_client):
    payload = {
        "username": "wronguser",
        "password": "wrongpass"
    }
    response = test_client.post(
        "/api/users/login",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 401
    assert response.get_json()["message"] == "Invalid username or password"


def test_get_user_by_id(test_client, test_user):
    response = test_client.get(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["_id"] == str(test_user.id)
    assert data["username"] == "testuser"
    assert isinstance(data["teams"], list)
    assert isinstance(data["personal_tasks"], list)


def test_get_user_not_found(test_client):
    response = test_client.get("/api/users/605c3c8657d1ad5e45b3e000")  # fake ID
    assert response.status_code == 404
    assert response.get_json()["message"] == "User not found"
