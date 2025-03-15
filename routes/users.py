from flask import Blueprint, request, jsonify

users_bp = Blueprint('users', __name__)

users_db = {
    "testuser": "123456",
    "alice": "password"
}

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.json  # Get JSON
    username = data.get('username')
    password = data.get('password')

    if username in users_db and users_db[username] == password:
        # Success Return Token
        return jsonify({
            "success": True,
            "token": f"fake-token-for-{username}",
            "message": "Login successful"
        })
    else:
        # Fail
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401