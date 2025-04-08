from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from app.utils.exceptions import CustomException
from bson import ObjectId

class User:
    """
    User model representing a user in the system.
    
    Attributes:
        username (str): Unique identifier for the user.
        password_hash (str): Hashed password (plain text passwords are never stored).
        id (ObjectId, optional): MongoDB document ID (automatically generated).
    """
    
    def __init__(self, username: str, password_hash: str, id: ObjectId = None):
        self.username = username
        self.password_hash = password_hash
        self.id = id

    @classmethod
    def create(cls, username: str, password: str) -> 'User':
        """
        Creates a new user with secure password hashing.
        
        Args:
            username (str): Desired username (must be unique).
            password (str): Plain text password.
        
        Returns:
            User: The created user instance.
        
        Raises:
            CustomException: If username already exists or validation fails.
        """
        # Validate input
        if len(username) < 3:
            raise CustomException("Username must be at least 3 characters", 400)
        if len(password) < 8:
            raise CustomException("Password must be at least 8 characters", 400)
        
        # Check for existing user [[1]][[4]]
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            raise CustomException("Username already exists", 409)
        
        # Hash password and insert into MongoDB [[6]][[7]]
        password_hash = generate_password_hash(password)
        result = mongo.db.users.insert_one({
            'username': username,
            'password_hash': password_hash
        })
        return cls(username, password_hash, id=result.inserted_id)

    @classmethod
    def get_by_username(cls, username: str) -> 'User':
        """
        Retrieves a user by their username.
        
        Args:
            username (str): The username to search for.
        
        Returns:
            User: The user instance if found, else None.
        """
        user_data = mongo.db.users.find_one({'username': username})
        return cls(**user_data) if user_data else None

    @classmethod
    def get_by_id(cls, user_id: ObjectId) -> 'User':
        """
        Retrieves a user by their MongoDB ObjectId.
        
        Args:
            user_id (ObjectId): The user's unique database ID.
        
        Returns:
            User: The user instance if found, else None.
        """
        user_data = mongo.db.users.find_one({'_id': user_id})
        return cls(**user_data) if user_data else None

    def check_password(self, password: str) -> bool:
        """
        Verifies a plain text password against the stored hash.
        
        Args:
            password (str): The password to check.
        
        Returns:
            bool: True if password matches, else False.
        """
        return check_password_hash(self.password_hash, password)

    def update_password(self, new_password: str) -> None:
        """
        Updates the user's password with a new secure hash.
        
        Args:
            new_password (str): New plain text password.
        
        Raises:
            CustomException: If password validation fails.
        """
        if len(new_password) < 8:
            raise CustomException("Password must be at least 8 characters", 400)
        new_hash = generate_password_hash(new_password)
        mongo.db.users.update_one(
            {'_id': self.id},
            {'$set': {'password_hash': new_hash}}
        )
        self.password_hash = new_hash