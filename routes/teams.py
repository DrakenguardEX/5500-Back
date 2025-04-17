from flask import Blueprint, request, jsonify
from models.team import Team
from models.task import Task
from models.user import User
from datetime import datetime

teams_bp = Blueprint('teams', __name__)

# Get all teams for the current user
@teams_bp.route('/', methods=['GET'])
def get_teams():
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify({"message": "Missing user ID"}), 400

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    teams = Team.objects(members=user)
    result = []
    for team in teams:
        result.append({
            "_id": str(team.id),
            "name": team.name,
            "tasks": [{
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "dueDate": str(task.dueDate) if task.dueDate else None
            } for task in team.tasks]
        })
    return jsonify(result), 200

# Create new team and add current user as member
@teams_bp.route('/', methods=['POST'])
def create_team():
    data = request.json
    name = data.get("name")
    user_id = request.headers.get("X-User-Id")

    if not name or not user_id:
        return jsonify({"message": "Team name and User ID required"}), 400

    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    team = Team(name=name, members=[user], tasks=[])
    team.save()

    return jsonify({
        "message": "Team created",
        "team": {
            "_id": str(team.id),
            "name": team.name,
            "members": [{"_id": str(user.id), "username": user.username}],
            "tasks": []
        }
    }), 201

# Add task to a team
@teams_bp.route('/<string:team_id>/tasks', methods=['POST'])
def add_task_to_team(team_id):
    data = request.json
    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "")
    due_date = data.get("dueDate")

    team = Team.objects(id=team_id).first()
    if not team:
        return jsonify({"message": "Team not found"}), 404
    
    # Check for duplicate title in the team's tasks
    for task in team.tasks:
        if task.title.strip().lower() == title.strip().lower():
            return jsonify({"message": "Task with this title already exists"}), 409


    task = Task(title=title, description=description, status=status, dueDate=due_date, team=team)
    task.save()
    team.tasks.append(task)
    team.save()

    return jsonify({
        "message": "Task added",
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "dueDate": str(task.dueDate) if task.dueDate else None
        }
    }), 201

@teams_bp.route('/<string:team_id>/tasks/<string:task_id>', methods=['PUT'])
def update_team_task(team_id, task_id):
    data = request.json

    team = Team.objects(id=team_id).first()
    if not team:
        return jsonify({"message": "Team not found"}), 404

    task = Task.objects(id=task_id, team=team).first()
    if not task:
        return jsonify({"message": "Task not found in this team"}), 404

    # Update fields directly like in tasks.py
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    task.priority = data.get("priority", task.priority)
    task.type = data.get("type", task.type)
    task.cycle = data.get("cycle", task.cycle)
    
    # Handle dueDate separately for proper date formatting
    due_date_str = data.get("dueDate")
    if due_date_str:
        try:
            task.dueDate = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            print("⚠️ Invalid dueDate format:", due_date_str)

    task.save()

    return jsonify({
        "message": "Task updated",
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "type": task.type,
            "cycle": task.cycle,
            "dueDate": str(task.dueDate) if task.dueDate else None
        }
    }), 200

@teams_bp.route('/<string:team_id>/tasks/<string:task_id>', methods=['DELETE'])
def delete_team_task(team_id, task_id):
    team = Team.objects(id=team_id).first()
    if not team:
        return jsonify({"message": "Team not found"}), 404

    task = Task.objects(id=task_id, team=team).first()
    if not task:
        return jsonify({"message": "Task not found in this team"}), 404

    # Remove task from team's task list and delete it
    team.tasks = [t for t in team.tasks if t.id != task.id]
    team.save()
    task.delete()

    return jsonify({"message": "Task deleted"}), 200


@teams_bp.route('/<string:team_id>/members', methods=['POST'])
def add_member_to_team(team_id):
    data = request.json
    username_to_add = data.get("username")

    if not username_to_add:
        return jsonify({"message": "Username is required"}), 400

    user = User.objects(username=username_to_add).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    team = Team.objects(id=team_id).first()
    if not team:
        return jsonify({"message": "Team not found"}), 404

    if user in team.members:
        return jsonify({"message": "User already a member"}), 409

    team.members.append(user)
    team.save()

    user.teams.append(team)
    user.save()

    return jsonify({
        "message": "User added to team",
        "user": {
            "_id": str(user.id),
            "username": user.username
        }
    }), 200
