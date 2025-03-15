from flask import Blueprint, request, jsonify

tasks_bp = Blueprint('tasks', __name__)

# Mock database (临时数据)
tasks_db = [
    {"id": 1, "title": "Task 1", "description": "Description 1"},
    {"id": 2, "title": "Task 2", "description": "Description 2"}
]

# 获取所有任务
@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    return jsonify(tasks_db)

# 获取单个任务详情
@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if task:
        return jsonify(task), 200
    else:
        return jsonify({"message": "Task not found"}), 404

# 更新任务（标题和描述）
@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if task:
        task["title"] = data.get("title", task["title"])  # 如果有 title 就更新
        task["description"] = data.get("description", task["description"])  # 如果有 description 就更新
        return jsonify({"message": "Task updated", "task": task}), 200
    else:
        return jsonify({"message": "Task not found"}), 404

# 删除任务
@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks_db
    tasks_db = [task for task in tasks_db if task["id"] != task_id]
    return jsonify({"message": "Task deleted"}), 200
