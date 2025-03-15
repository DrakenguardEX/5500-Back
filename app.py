from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# template
users_db = {
    "testuser": "123456",
    "alice": "password"
}

@app.route('/api/login', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
