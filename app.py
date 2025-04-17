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


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    if test_config:
        app.config.update(test_config)
        # connect(
        #     db="test_team_task_manager",  # Use a separate test DB if needed
        #     host="mongodb://localhost:27017/test_team_task_manager"  # Example local MongoDB
        # )
    else:
        try:
            get_connection()
        except:
            connect(
                db="team_task_manager",
                host="mongodb+srv://User1:User1@taskmanagement.vhuou.mongodb.net/team_task_manager"
            )

    # Register blueprints
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai')

    return app

# Only run the server if it's not imported (e.g., by test code)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)