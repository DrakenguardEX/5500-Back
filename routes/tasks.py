from flask import Blueprint, request, jsonify
from models.task import Task
from models.team import Team
from models.user import User

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    tasks = Task.objects()
    result = [{
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "team_id": str(task.team.id) if task.team else None
    } for task in tasks]
    return jsonify(result), 200


@tasks_bp.route('/<string:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.objects(id=task_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404
    return jsonify({
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "team_id": str(task.team.id) if task.team else None
    }), 200


@tasks_bp.route('/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.objects(id=task_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.json
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.type = data.get("type", task.type)
    task.status = data.get("status", task.status)
    task.priority = data.get("priority", task.priority)
    
    task.save()

    return jsonify({"message": "Task updated", "task": {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "type": task.type,
        "status": task.status,
        "priority": task.priority
        
    }}), 200


@tasks_bp.route('/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.objects(id=task_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404

    task.delete()
    return jsonify({"message": "Task deleted"}), 200

@tasks_bp.route('/user/<string:user_id>', methods=['POST'])
def add_user_task(user_id):
    try:
        data = request.json
        title = data.get("title")
        description = data.get("description", "")
        
        task_type = "TBD"
        status = "TBD"
        priority = "TBD"

        user = User.objects(id=user_id).first()
        if not user:
            print("❌ User not found:", user_id)
            return jsonify({"message": "User not found"}), 404

        task = Task(
            title=title, 
            description=description,
            type = task_type,
            status = status,
            priority = priority,
            owner=user)
        task.save()

        user.personal_tasks.append(task)
        user.save()

        return jsonify({
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "type": task.type,
            "status": task.status,
            "priority": task.priority
        }), 201

    except Exception as e:
        print("🔥 Error creating personal task:", e)
        return jsonify({"error": str(e)}), 500


@tasks_bp.route('/user/<string:user_id>', methods=['GET'])
def get_user_tasks(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify([
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "type": task.type,
            "status": task.status,
            "priority": task.priority
        } for task in user.personal_tasks
    ])
