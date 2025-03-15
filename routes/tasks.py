from flask import Blueprint, jsonify, request

tasks_bp = Blueprint('tasks', __name__)

# Mock database
tasks_db = [
    {"id": 1, "title": "Task 1"},
    {"id": 2, "title": "Task 2"}
]

@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    return jsonify(tasks_db)

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks_db
    tasks_db = [task for task in tasks_db if task["id"] != task_id]
    return jsonify({"message": "Task deleted"}), 200

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    for task in tasks_db:
        if task["id"] == task_id:
            task["title"] = data.get("title", task["title"])
            return jsonify({"message": "Task updated", "task": task}), 200
    return jsonify({"message": "Task not found"}), 404
