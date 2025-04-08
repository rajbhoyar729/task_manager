from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.task_service import TaskService
from app.utils.exceptions import CustomException
from app.utils.validators import validate_task_data

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task for the authenticated user.
    
    Request Body:
        - title (str): Task title (required, min 3 characters).
        - description (str, optional): Task details.
        - status (str, optional): Must be 'pending', 'in-progress', or 'completed'.
    
    Responses:
        201: Task created successfully.
        400: Invalid input data.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    status = data.get('status', 'pending')

    # Validate input [[3]][[6]]
    if not validate_task_data(title, status):
        raise CustomException("Invalid task data", 400)

    # Create task via service layer [[8]]
    task_id, error = TaskService.create_task(
        user_id=user_id,
        title=title,
        description=description,
        status=status
    )
    if error:
        raise CustomException(error, 400)

    return jsonify({'id': task_id, 'message': 'Task created'}), 201

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Retrieve all tasks for the authenticated user.
    
    Responses:
        200: List of tasks.
    """
    user_id = get_jwt_identity()
    tasks = TaskService.get_user_tasks(user_id)
    return jsonify(tasks), 200

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Retrieve a specific task by ID.
    
    Responses:
        200: Task details.
        404: Task not found or access denied.
    """
    user_id = get_jwt_identity()
    task = TaskService.get_task_by_id(user_id, task_id)
    if not task:
        raise CustomException("Task not found", 404)
    return jsonify(task), 200

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task_put(task_id):
    """Fully replace a task's data (all fields required).
    
    Request Body:
        - title (str): New title.
        - description (str): New description.
        - status (str): New status.
    
    Responses:
        200: Updated task details.
        400: Invalid data.
        404: Task not found.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    required_fields = ['title', 'description', 'status']
    if not all(field in data for field in required_fields):
        raise CustomException("Missing required fields", 400)
    task, error = TaskService.update_task(user_id, task_id, data)
    if error:
        raise CustomException(error, 400)
    return jsonify(task), 200

@tasks_bp.route('/tasks/<task_id>', methods=['PATCH'])
@jwt_required()
def update_task_patch(task_id):
    """Partially update a task's data.
    
    Request Body:
        - title (str, optional)
        - description (str, optional)
        - status (str, optional)
    
    Responses:
        200: Updated task details.
        400: Invalid status.
        404: Task not found.
    """
    user_id = get_jwt_identity()
    updates = request.get_json()
    task, error = TaskService.update_task(user_id, task_id, updates)
    if error:
        raise CustomException(error, 400)
    return jsonify(task), 200

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task by ID.
    
    Responses:
        200: Task deleted.
        404: Task not found.
    """
    user_id = get_jwt_identity()
    success = TaskService.delete_task(user_id, task_id)
    if not success:
        raise CustomException("Task not found", 404)
    return jsonify({'message': 'Task deleted'}), 200