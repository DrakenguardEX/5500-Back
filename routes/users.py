from flask import Blueprint, request, jsonify
from models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400

    if User.objects(username=username).first():
        return jsonify({"success": False, "message": "Username already exists."}), 409

    user = User(username=username, password=password)
    user.save()

    return jsonify({
        "success": True,
        "message": "User registered successfully.",
        "user_id": str(user.id)
    }), 201

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.objects(username=username).first()
    if user and user.password == password:
        return jsonify({
            "success": True,
            "token": f"fake-token-for-{username}",
            "user_id": str(user.id),
            "message": "Login successful"
        }), 200

    return jsonify({"success": False, "message": "Invalid username or password"}), 401


@users_bp.route('/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "_id": str(user.id),
        "username": user.username,
        "teams": [str(t.id) for t in user.teams],
        "personal_tasks": [str(t.id) for t in user.personal_tasks]
    })