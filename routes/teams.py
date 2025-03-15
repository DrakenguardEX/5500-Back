from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
import uuid  # for generating unique task IDs

teams_bp = Blueprint('teams', __name__)

# Get all teams with their tasks
@teams_bp.route('/', methods=['GET'])
def get_teams():
    db = current_app.config['DB']
    teams = []
    for team in db['teams'].find():
        team['_id'] = str(team['_id'])
        for task in team.get('tasks', []):
            task['id'] = str(task['id'])
        teams.append(team)
    return jsonify(teams), 200

# Create a new team
@teams_bp.route('/', methods=['POST'])
def create_team():
    db = current_app.config['DB']
    data = request.json
    if 'name' not in data:
        return jsonify({"message": "Team name is required"}), 400
    team = {
        "name": data['name'],
        "tasks": []
    }
    result = db['teams'].insert_one(team)
    team['_id'] = str(result.inserted_id)
    return jsonify({"message": "Team created", "team": team}), 201

# Add a new task to a team
@teams_bp.route('/<string:team_id>/tasks', methods=['POST'])
def add_task_to_team(team_id):
    db = current_app.config['DB']
    data = request.json
    if 'title' not in data:
        return jsonify({"message": "Task title is required"}), 400

    task = {
        "id": str(ObjectId()),  # generate a unique id
        "title": data['title'],
        "description": data.get('description', '')
    }

    result = db['teams'].update_one(
        {'_id': ObjectId(team_id)},
        {'$push': {'tasks': task}}
    )

    if result.matched_count == 0:
        return jsonify({"message": "Team not found"}), 404

    return jsonify({"message": "Task added", "task": task}), 201

# Update a task inside a team
@teams_bp.route('/<string:team_id>/tasks/<string:task_id>', methods=['PUT'])
def update_task_in_team(team_id, task_id):
    db = current_app.config['DB']
    data = request.json

    result = db['teams'].update_one(
        {'_id': ObjectId(team_id), 'tasks.id': task_id},
        {'$set': {
            'tasks.$.title': data.get('title'),
            'tasks.$.description': data.get('description')
        }}
    )

    if result.matched_count == 0:
        return jsonify({"message": "Task or Team not found"}), 404

    return jsonify({"message": "Task updated"}), 200

# Delete a task from a team
@teams_bp.route('/<string:team_id>/tasks/<string:task_id>', methods=['DELETE'])
def delete_task_from_team(team_id, task_id):
    db = current_app.config['DB']
    result = db['teams'].update_one(
        {'_id': ObjectId(team_id)},
        {'$pull': {'tasks': {'id': task_id}}}
    )

    if result.matched_count == 0:
        return jsonify({"message": "Team not found"}), 404

    return jsonify({"message": "Task deleted"}), 200
