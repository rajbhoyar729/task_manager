def validate_task_data(title: str, status: str) -> bool:
    """
    Validates task title and status against application rules.
    
    Args:
        title (str): Task title to validate.
        status (str): Task status (must be 'pending', 'in-progress', or 'completed').
    
    Returns:
        bool: True if valid, else False.
    
    Rules:
        - Title must be at least 3 non-whitespace characters [[3]][[6]].
        - Status must be one of the allowed values [[9]].
    """
    # Title validation
    if not title or len(title.strip()) < 3:
        return False
    
    # Status validation
    allowed_statuses = {'pending', 'in-progress', 'completed'}
    return status in allowed_statuses

def validate_username(username: str) -> bool:
    """
    Ensures username meets minimum length requirements.
    
    Args:
        username (str): Username to validate.
    
    Returns:
        bool: True if valid (>=3 characters), else False [[5]][[9]].
    """
    return username and len(username.strip()) >= 3

def validate_password(password: str) -> bool:
    """
    Enforces password complexity requirements.
    
    Args:
        password (str): Password to validate.
    
    Returns:
        bool: True if valid (>=8 characters), else False [[5]][[7]].
    """
    return password and len(password.strip()) >= 8