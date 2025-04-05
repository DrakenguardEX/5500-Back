import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pytest
import mongomock
from unittest.mock import patch, MagicMock
from mongoengine import connect, disconnect

from app import create_app
from models.user import User
from models.task import Task


@pytest.fixture(scope="module")
def test_client():
    disconnect()
    connect("mongoenginetest", host="mongodb://localhost", mongo_client_class=mongomock.MongoClient)
    app = create_app({"TESTING": True})
    client = app.test_client()

    # Set up mock user and tasks
    user = User(username="aiuser", password="testpass").save()
    Task(
        title="Write report",
        description="Write the monthly financial report",
        priority="High",
        cycle="Weekly",
        owner=user
    ).save()
    Task(
        title="Team meeting",
        description="Schedule and lead the weekly sync",
        priority="Medium",
        cycle="Weekly",
        owner=user
    ).save()

    yield client

    # Clean up
    User.objects.delete()
    Task.objects.delete()
    disconnect()


@patch("routes.ai_assistant.client.chat.completions.create")
def test_generate_task_plan(mock_openai_call, test_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="📝 Here is your task plan."))]
    mock_openai_call.return_value = mock_response

    user = User.objects.first()
    response = test_client.post("/api/ai-assistant/plan", json={"user_id": str(user.id)})

    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data
    assert "task plan" in data["plan"]


@patch("routes.ai_assistant.client.chat.completions.create")
def test_generate_task_guidance(mock_openai_call, test_client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="🧭 Step-by-step guide..."))]
    mock_openai_call.return_value = mock_response

    response = test_client.get("/api/ai-assistant/guidance/Write report")
    assert response.status_code == 200
    data = response.get_json()
    assert "guidance" in data
    assert "Step-by-step" in data["guidance"]


def test_generate_guidance_task_not_found(test_client):
    response = test_client.get("/api/ai-assistant/guidance/Nonexistent Task")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["message"] == "Task not found."
