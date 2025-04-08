from bson import ObjectId
from app import mongo
from app.utils.exceptions import CustomException
from app.utils.validators import validate_task_data
from typing import List, Dict, Optional

class TaskService:
    """
    Service layer for task-related operations.
    
    Ensures all operations are scoped to the authenticated user and validates input data.
    """
    
    @classmethod
    def create_task(cls, user_id: str, title: str, description: str, status: str) -> str:
        """
        Creates a new task for a user.
        
        Args:
            user_id (str): ID of the task owner.
            title (str): Task title (min 3 characters).
            description (str): Task details (optional).
            status (str): Must be 'pending', 'in-progress', or 'completed'.
        
        Returns:
            str: The ID of the created task.
        
        Raises:
            CustomException: For invalid data or database errors.
        """
        if not validate_task_data(title, status):
            raise CustomException("Invalid task data", 400)
        
        result = mongo.db.tasks.insert_one({
            'title': title,
            'description': description,
            'status': status,
            'user_id': user_id
        })
        return str(result.inserted_id)

    @classmethod
    def get_user_tasks(cls, user_id: str) -> List[Dict]:
        """
        Retrieves all tasks for a user.
        
        Args:
            user_id (str): ID of the task owner.
        
        Returns:
            List[Dict]: Serialized tasks (id, title, status).
        """
        tasks = mongo.db.tasks.find({'user_id': user_id})
        return [{'id': str(t['_id']), 'title': t['title'], 'status': t['status']} for t in tasks]

    @classmethod
    def get_task_by_id(cls, user_id: str, task_id: str) -> Optional[Dict]:
        """
        Retrieves a specific task by ID, verifying ownership.
        
        Args:
            user_id (str): ID of the task owner.
            task_id (str): MongoDB ObjectId as a string.
        
        Returns:
            Dict: Task details if found and owned by user.
        
        Raises:
            CustomException: If task not found or access denied.
        """
        try:
            task = mongo.db.tasks.find_one({
                '_id': ObjectId(task_id),
                'user_id': user_id
            })
        except Exception as e:
            raise CustomException(f"Invalid task ID format: {str(e)}", 400)
        
        if not task:
            raise CustomException("Task not found or access denied", 404)
        return {
            'id': str(task['_id']),
            'title': task['title'],
            'description': task.get('description'),
            'status': task['status']
        }

    @classmethod
    def update_task(cls, user_id: str, task_id: str, updates: Dict) -> Dict:
        """
        Updates a task, enforcing ownership and valid status transitions.
        
        Args:
            user_id (str): ID of the task owner.
            task_id (str): MongoDB ObjectId as a string.
            updates (Dict): Fields to update (title, description, status).
        
        Returns:
            Dict: Updated task details.
        
        Raises:
            CustomException: For invalid data or access violations.
        """
        # Validate status enum [[6]][[9]]
        allowed_statuses = ['pending', 'in-progress', 'completed']
        if 'status' in updates and updates['status'] not in allowed_statuses:
            raise CustomException("Invalid status value", 400)
        
        # Enforce ownership and existence [[8]]
        existing_task = cls.get_task_by_id(user_id, task_id)
        if not existing_task:
            raise CustomException("Task not found", 404)
        
        # Perform atomic update [[6]]
        mongo.db.tasks.update_one(
            {'_id': ObjectId(task_id), 'user_id': user_id},
            {'$set': updates}
        )
        return cls.get_task_by_id(user_id, task_id)  # Return updated state

    @classmethod
    def delete_task(cls, user_id: str, task_id: str) -> bool:
        """
        Deletes a task, verifying ownership.
        
        Args:
            user_id (str): ID of the task owner.
            task_id (str): MongoDB ObjectId as a string.
        
        Returns:
            bool: True if deleted, False otherwise.
        """
        result = mongo.db.tasks.delete_one({
            '_id': ObjectId(task_id),
            'user_id': user_id
        })
        return result.deleted_count > 0