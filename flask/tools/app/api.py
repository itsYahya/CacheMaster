from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flasgger import Swagger
import jwt
import datetime
import os
import redis
import json

# App setup
app = Flask(__name__)
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Taux de Change Auth API",
        "description": "User auth with JWT and Redis sync",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    }
})
app.config['SECRET_KEY'] = 'your-very-secure-secret-key'  # Replace with env var in prod
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:%40dmin1234@postgres:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Redis configuration.
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Create DB tables (only first time)
with app.app_context():
    db.create_all()

# 🧾 Signup route
@app.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Username or email already exists
    """
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully ✅'}), 201

# 🔐 Login route
@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return a JWT
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: JWT token returned
        schema:
          type: object
          properties:
            token:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cached_user = redis_client.get(f"user:{username}")
    user = None

    if cached_user:
        user_data = json.loads(cached_user)
        if bcrypt.check_password_hash(user_data['password_hash'], password):
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                created_at=datetime.datetime.fromisoformat(user_data['created_at'])
            )
        else:
            return jsonify({'error': 'Invalid credentials (Redis)'}), 401
    else:
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401

        redis_client.set(f"user:{username}", json.dumps({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password_hash': user.password_hash,
            'created_at': user.created_at.isoformat()
        }), ex=3600)  # Optional: TTL 1 hour

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token})


@app.route('/me', methods=['GET'])
def get_user():
    """
    Get current user's info (requires JWT)
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT token in format "Bearer <token>"
    responses:
      200:
        description: User info
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            email:
              type: string
            created_at:
              type: string
              format: date-time
      401:
        description: Unauthorized or invalid token
    """
    auth = request.headers.get('Authorization')
    if not auth:
        return jsonify({'error': 'Missing token'}), 401

    try:
        token = auth.split()[1]
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(decoded['user_id'])
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

# 🚀 Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
