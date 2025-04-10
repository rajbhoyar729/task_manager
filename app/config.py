import os
from decouple import Config, RepositoryEnv, RepositoryEmpty, UndefinedValueError
from typing import Optional, Type, TypeVar, Union, Dict, Any
from app.utils.exceptions import CustomException

# Define type variables for configuration classes
T = TypeVar('T', bound='BaseConfig')

class BaseConfig:
    
    def __init__(self, config: Config):
        self._config = config

    @classmethod
    def from_env(cls: Type[T], env_file: Optional[str] = None) -> T:
        """
        Create a config instance from an environment file or system environment variables.
        
        Args:
            env_file (Optional[str]): Path to the .env file. If None, use system env vars.
        
        Returns:
            T: An instance of the configuration class.
        """
        if env_file and os.path.exists(env_file):
            config = Config(RepositoryEnv(env_file))
        else:
            config = Config(RepositoryEmpty())  # Fallback to system environment variables
        return cls(config)

    def _get(self, key: str, cast: type = str, default: Any = None) -> Any:
        """
        Get a configuration value with type casting and fallback default.
        
        Args:
            key (str): The environment variable key.
            cast (type): Type to cast the value to.
            default (Any): Default value if the key is missing.
        
        Returns:
            Any: The cast value or default.
        
        Raises:
            CustomException: If the key is missing and no default is provided.
        """
        try:
            return self._config(key, cast=cast)
        except UndefinedValueError:
            if default is not None:
                return default
            raise CustomException(f"Missing required environment variable: {key}", 500)

    @property
    def DEBUG(self) -> bool:
        """Enable debug mode."""
        return self._get('DEBUG', cast=bool, default=False)

    @property
    def TESTING(self) -> bool:
        """Enable testing mode."""
        return self._get('TESTING', cast=bool, default=False)

    @property
    def MONGO_URI(self) -> str:
        """MongoDB connection URI."""
        return self._get('DATABASE_URI', cast=str)

    @property
    def JWT_SECRET_KEY(self) -> str:
        """Secret key for JWT encoding/decoding."""
        return self._get('JWT_SECRET_KEY', cast=str)

    @property
    def RATELIMIT_ENABLED(self) -> bool:
        """Enable rate limiting."""
        return self._get('RATELIMIT_ENABLED', cast=bool, default=True)

    @property
    def RATELIMIT_DEFAULT(self) -> str:
        """Default rate limit string."""
        return self._get('RATELIMIT_DEFAULT', cast=str, default="200 per day;50 per hour")

    @property
    def RATELIMIT_HEADERS_ENABLED(self) -> bool:
        """Enable rate limit headers."""
        return self._get('RATELIMIT_HEADERS_ENABLED', cast=bool, default=True)

class DevelopmentConfig(BaseConfig):
    """Configuration for development environment."""
    @property
    def DEBUG(self) -> bool:
        return True

    @property
    def RATELIMIT_ENABLED(self) -> bool:
        return False

class ProductionConfig(BaseConfig):
    """Configuration for production environment."""
    @property
    def RATELIMIT_ENABLED(self) -> bool:
        return True

class TestingConfig(BaseConfig):
    """Configuration for testing environment."""
    @property
    def TESTING(self) -> bool:
        return True

def get_config(env_file: Optional[str] = None) -> BaseConfig:
    """
    Get the appropriate configuration based on the FLASK_ENV environment variable.
    
    Args:
        env_file (Optional[str]): Path to an optional .env file.
    
    Returns:
        BaseConfig: The configuration instance.
    """
    env = os.getenv('FLASK_ENV', 'development')
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class.from_env(env_file)

# Global configuration instance
config = get_config()