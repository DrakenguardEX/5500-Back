from flask import Blueprint, request, jsonify
from models.team import Team
from models.task import Task
from models.user import User

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
                "description": task.description
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

    team = Team.objects(id=team_id).first()
    if not team:
        return jsonify({"message": "Team not found"}), 404

    task = Task(title=title, description=description, team=team)
    task.save()
    team.tasks.append(task)
    team.save()

    return jsonify({
        "message": "Task added",
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description
        }
    }), 201

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

