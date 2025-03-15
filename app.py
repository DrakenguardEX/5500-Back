from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from routes.users import users_bp
from routes.teams import teams_bp

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://User1:User1@taskmanagement.vhuou.mongodb.net/")
db = client['team_task_manager']

app.config['DB'] = db

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(teams_bp, url_prefix='/api/teams')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
