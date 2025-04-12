from flask import Blueprint, request, jsonify
from models.task import Task
from models.team import Team
from models.user import User
from bson.errors import InvalidId
from datetime import datetime

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
    try:
        task = Task.objects(id=task_id).first()
    except InvalidId as e:
        print("🔥 Invalid Task ID:", e)
        return jsonify({"message": "Invalid task ID"}), 400

    if not task:
        return jsonify({"message": "Task not found"}), 404

    return jsonify({
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "type": task.type,
        "priority": task.priority,
        "cycle": task.cycle,
        "dueDate": str(task.dueDate) if task.dueDate else None
    }), 200


@tasks_bp.route('/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.objects(id=task_id).first()
    except InvalidId as e:
        return jsonify({"message": "Invalid task ID"}), 400

    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.json
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.type = data.get("type", task.type)
    task.status = data.get("status", task.status)
    task.priority = data.get("priority", task.priority)
    task.cycle = data.get("cycle", task.cycle)

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
            "type": task.type,
            "status": task.status,
            "priority": task.priority,
            "cycle": task.cycle,
            "dueDate": str(task.dueDate) if task.dueDate else None
        }
    }), 200


@tasks_bp.route('/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.objects(id=task_id).first()
    except InvalidId as e:
        return jsonify({"message": "Invalid task ID"}), 400

    if not task:
        return jsonify({"message": "Task not found"}), 404

    task.delete()
    return jsonify({"message": "Task deleted"}), 200


@tasks_bp.route('/user/<string:user_id>', methods=['POST'])
def add_user_task(user_id):
    try:
        user = User.objects(id=user_id).first()
    except InvalidId as e:
        print("🔥 Invalid User ID:", e)
        return jsonify({"message": "Invalid user ID"}), 400

    if not user:
        print("❌ User not found:", user_id)
        return jsonify({"message": "User not found"}), 404

    data = request.json
    title = data.get("title")
    description = data.get("description", "")
    task_type = data.get("type", "TBD")
    status = data.get("status", "TBD")
    priority = data.get("priority", "TBD")
    cycle = data.get("cycle", "TBD")

    due_date_str = data.get("dueDate")
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            print("⚠️ Invalid dueDate format:", due_date_str)

    task = Task(
        title=title,
        description=description,
        type=task_type,
        status=status,
        priority=priority,
        cycle=cycle,
        dueDate=due_date,
        owner=user
    )
    task.save()
    user.personal_tasks.append(task)
    user.save()

    return jsonify({
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "type": task.type,
        "status": task.status,
        "priority": task.priority,
        "cycle": task.cycle,
        "dueDate": str(task.dueDate) if task.dueDate else None
    }), 201


@tasks_bp.route('/user/<string:user_id>', methods=['GET'])
def get_user_tasks(user_id):
    try:
        user = User.objects(id=user_id).first()
    except InvalidId as e:
        return jsonify({"message": "Invalid user ID"}), 400

    if not user:
        return jsonify({"message": "User not found"}), 404

    result = []
    for task_ref in user.personal_tasks:
        task = Task.objects(id=task_ref.id).first()
        if task:
            result.append({
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "type": task.type,
                "status": task.status,
                "priority": task.priority,
                "cycle": task.cycle,
                "dueDate": task.dueDate
            })

    return jsonify(result), 200
