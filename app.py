from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.users import users_bp
from routes.tasks import tasks_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
