from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.user import User
from app.utils.exceptions import CustomException

# Initialize blueprint and rate limiter [[3]][[7]]
auth_bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent registration abuse [[7]]
def register():
    """User registration endpoint.
    
    Request Body:
        - username (str): Unique username (min 3 characters).
        - password (str): Plain text password (min 8 characters).
    
    Responses:
        201: User created successfully.
        400: Invalid input data.
        409: Username already exists.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Input validation [[5]][[6]]
    if not username or len(username) < 3:
        raise CustomException("Username must be at least 3 characters", 400)
    if not password or len(password) < 8:
        raise CustomException("Password must be at least 8 characters", 400)

    # Create user [[6]][[8]]
    try:
        User.create(username, password)
    except CustomException as e:
        raise e  # Re-raise for global handler to process

    return jsonify({'message': 'User created'}), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")  # Protect against brute-force attacks [[7]]
def login():
    """User login endpoint with JWT token generation.
    
    Request Body:
        - username (str): Registered username.
        - password (str): Correct password.
    
    Responses:
        200: JWT access token.
        401: Invalid credentials.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Validate input [[5]]
    if not username or not password:
        raise CustomException("Username and password are required", 400)

    # Authenticate user [[6]][[8]]
    user = User.get_by_username(username)
    if not user or not user.check_password(password):
        raise CustomException("Invalid credentials", 401)

    # Generate JWT [[5]][[7]]
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token), 200