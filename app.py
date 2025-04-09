import logging
import argparse
import os  # Import os to set environment variables
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the Flask application.
    
    Initializes the app, configures logging, and runs the server.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Task Manager API')
    parser.add_argument('--env', default='development', choices=['development', 'production', 'testing'],
                        help='Environment to run the application in (default: development)')
    args = parser.parse_args()

    # Synchronize FLASK_ENV with the --env argument
    os.environ['FLASK_ENV'] = args.env

    # Create the Flask app with the specified environment
    app = create_app()

    # Log startup event
    logger.info(f"Starting Task Manager API in {args.env} environment")

    try:
        # Run the Flask app
        if args.env == 'development':
            app.run(debug=True)
        else:
            app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}", exc_info=True)
        raise
    finally:
        # Log shutdown event
        logger.info("Task Manager API shutting down")

if __name__ == "__main__":
    main()