from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env [[2]][[3]]

class Config:
    # Base configuration [[6]]
    DEBUG = False
    TESTING = False
    MONGO_URI = os.getenv("DATABASE_URI", "mongodb://localhost:27017/taskmanager")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"  # Rate limiting [[7]][[9]]
    RATELIMIT_HEADERS_ENABLED = True

class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.getenv("DATABASE_URI", "mongodb://localhost:27017/taskmanager_dev")  # Separate DB for dev [[1]]
    RATELIMIT_ENABLED = False  # Disable rate limiting in development [[9]]

class ProductionConfig(Config):
    MONGO_URI = os.getenv("DATABASE_URI")  # Require explicit production URI [[2]]
    RATELIMIT_ENABLED = True  # Enable rate limiting in production [[7]]

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv("TEST_DATABASE_URI", "mongodb://localhost:27017/taskmanager_test")  # Isolated test DB [[5]]

def get_config():
    """Return the appropriate config class based on FLASK_ENV"""
    env = os.getenv("FLASK_ENV", "development")
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    return config_map.get(env, DevelopmentConfig)