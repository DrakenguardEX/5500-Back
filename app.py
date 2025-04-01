from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from routes.users import users_bp
from routes.teams import teams_bp
from routes.tasks import tasks_bp
from routes.ai_assistant import ai_assistant_bp

from dotenv import load_dotenv
import os

load_dotenv()  # 👈 This loads variables from .env

openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

connect(
    db="team_task_manager",
    host="mongodb+srv://User1:User1@taskmanagement.vhuou.mongodb.net/team_task_manager"
)

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(teams_bp, url_prefix='/api/teams')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai') 

if __name__ == '__main__':
    app.run(debug=True, port=5000)
