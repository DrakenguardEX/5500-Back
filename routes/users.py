from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId

users_bp = Blueprint('users', __name__)

# User registration route
@users_bp.route('/register', methods=['POST'])
def register():
    db = current_app.config['DB']
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400

    # Check if username already exists
    existing_user = db['users'].find_one({"username": username})
    if existing_user:
        return jsonify({"success": False, "message": "Username already exists."}), 409

    # Insert new user into MongoDB
    user = {
        "username": username,
        "password": password  # Plaintext password
    }
    result = db['users'].insert_one(user)

    return jsonify({"success": True, "message": "User registered successfully.", "user_id": str(result.inserted_id)}), 201

# User login route
@users_bp.route('/login', methods=['POST'])
def login():
    db = current_app.config['DB']  # Access MongoDB database from app config
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400

    # Find user in MongoDB
    user = db['users'].find_one({"username": username})

    if user and user.get('password') == password:
        # If user exists and password matches, return success
        return jsonify({
            "success": True,
            "token": f"fake-token-for-{username}",  # Optional: implement real JWT token later
            "message": "Login successful"
        }), 200
    else:
        # If user not found or password doesn't match
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401
