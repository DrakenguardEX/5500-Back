import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
import mongomock
from mongoengine import connect, disconnect

from app import create_app
from models.user import User
from models.team import Team
from models.task import Task


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
def mock_user():
    user = User(username="testuser", password="testpass")
    user.save()
    yield user
    user.delete()


def test_create_team(test_client, mock_user):
    payload = {"name": "Alpha Team"}
    response = test_client.post(
        "/api/teams/",
        data=json.dumps(payload),
        content_type='application/json',
        headers={"X-User-Id": str(mock_user.id)}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["team"]["name"] == "Alpha Team"
    assert data["team"]["members"][0]["username"] == "testuser"


def test_get_teams(test_client, mock_user):
    # Create team first
    team = Team(name="Alpha Team", members=[mock_user])
    team.save()

    response = test_client.get(
        "/api/teams/",
        headers={"X-User-Id": str(mock_user.id)}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(team["name"] == "Alpha Team" for team in data)


def test_add_task_to_team(test_client, mock_user):
    team = Team(name="Task Team", members=[mock_user])
    team.save()

    payload = {
        "title": "Team Task",
        "description": "Task for the team"
    }

    response = test_client.post(
        f"/api/teams/{team.id}/tasks",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["task"]["title"] == "Team Task"
    assert Team.objects(id=team.id).first().tasks  # should contain one task


def test_add_member_to_team(test_client, mock_user):
    user2 = User(username="newuser", password="testpass")
    user2.save()
    team = Team(name="Member Team", members=[mock_user])
    team.save()

    payload = {"username": "newuser"}
    response = test_client.post(
        f"/api/teams/{team.id}/members",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["username"] == "newuser"

    user2.reload()
    assert any(str(t.id) == str(team.id) for t in user2.teams)

    # Clean up
    user2.delete()
    team.delete()


def test_add_existing_member_returns_409(test_client, mock_user):
    team = Team(name="Conflict Team", members=[mock_user])
    team.save()

    payload = {"username": "testuser"}
    response = test_client.post(
        f"/api/teams/{team.id}/members",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 409
    data = response.get_json()
    assert "already a member" in data["message"]


def test_get_teams_missing_user_id(test_client):
    response = test_client.get("/api/teams/")
    assert response.status_code == 400
    assert "Missing user ID" in response.get_json()["message"]
