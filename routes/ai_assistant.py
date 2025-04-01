from flask import Blueprint, request, jsonify
from datetime import datetime
from models.task import Task
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


ai_assistant_bp = Blueprint("ai_assistant", __name__)

@ai_assistant_bp.route("/plan", methods=["POST"])
def generate_task_plan():
    user_id = request.json.get("user_id")
    tasks = Task.objects(owner=user_id)

    if not tasks:
        return jsonify({"message": "No tasks found for this user."}), 404

    def format_due_date(d):
        if not d:
            return "No due date"
        if isinstance(d, str):
            return d
        return d.strftime("%Y-%m-%d")

    formatted_tasks = []
    for t in tasks:
        due = format_due_date(t.dueDate)
        formatted_tasks.append(
            f"- {t.title} (Priority: {t.priority}, Due: {due}, Cycle: {t.cycle})"
        )

    prompt = f"""
You are a smart productivity assistant. A user has the following tasks:

{chr(10).join(formatted_tasks)}

Create an effective plan for them to complete their tasks. Consider priority, due date, and cycle. Organize tasks by urgency and suggest how they can schedule their time.
"""

    response = client.chat.completions.create(
        # model="gpt-4",
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    plan = response.choices[0].message.content
    return jsonify({"plan": plan})



@ai_assistant_bp.route("/guidance/<task_query>", methods=["GET"])
def generate_task_guidance(task_query):
    task = Task.objects(title__iexact=task_query).first()
    if not task:
        return jsonify({"message": "Task not found."}), 404

    prompt = f"""
You are a helpful assistant. Please help the user complete this task:

Title: {task.title}
Description: {task.description or "No detailed description provided."}

Provide a clear step-by-step guide on how to complete it effectively.
"""

    response = client.chat.completions.create(
        # model="gpt-4",
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    guidance = response.choices[0].message.content
    return jsonify({"guidance": guidance})
