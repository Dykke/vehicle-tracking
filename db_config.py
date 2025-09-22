"""
Helper module to configure database connections consistently across scripts
"""
import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """
    Get and process the database URL from environment variables
    """
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        logger.info("DATABASE_URL environment variable found - using production database")
        
        # Handle different database types
        if database_url.startswith('mysql://'):
            logger.info("MySQL database detected")
            # For local development, ensure we're using the right database name
            if 'localhost' in database_url and 'transport_monitoring' not in database_url:
                # Add the database name for local development
                if database_url.endswith('/'):
                    database_url = database_url + 'transport_monitoring'
                else:
                    database_url = database_url + '/transport_monitoring'
                logger.info(f"Updated local MySQL URL to include database: {database_url}")
            return database_url
        elif database_url.startswith('postgres://'):
            # Handle Render's postgres:// URLs (convert to postgresql://)
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            logger.info("Converted postgres:// URL to postgresql://")
        elif database_url.startswith('postgresql://'):
            logger.info("PostgreSQL database detected")
        
        # Use pg8000 dialect explicitly for PostgreSQL
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
            logger.info("Using pg8000 dialect for PostgreSQL")
        
        return database_url
    
    # No DATABASE_URL - use SQLite for local development
    logger.info("DATABASE_URL environment variable is not set! Using SQLite for local development.")
    
    # Get the current directory for database path resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # For local development, use transport_monitoring.db in the current directory
    # This matches the .env file expectation
    db_name = 'transport_monitoring.db'
    db_path = os.path.join(current_dir, db_name)
    
    database_url = f'sqlite:///{db_path}'
    logger.info(f"Using SQLite database at: {db_path}")
    
    return database_url

def verify_database_path():
    """
    Verify that the database path is correct and accessible
    """
    database_url = get_database_url()
    
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        logger.info(f"SQLite Database path: {db_path}")
        
        # Handle both absolute and relative paths
        if os.path.isabs(db_path):
            abs_db_path = db_path
        else:
            abs_db_path = os.path.abspath(db_path)
        
        logger.info(f"Absolute database path: {abs_db_path}")
        logger.info(f"Database file exists: {os.path.exists(abs_db_path)}")
        
        if os.path.exists(abs_db_path):
            logger.info(f"Database file size: {os.path.getsize(abs_db_path)} bytes")
        
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Database directory: {os.path.dirname(abs_db_path)}")
        logger.info(f"Database directory exists: {os.path.exists(os.path.dirname(abs_db_path))}")
        
        # Check if we can write to the database directory
        db_dir = os.path.dirname(abs_db_path)
        if os.path.exists(db_dir):
            logger.info(f"Database directory writable: {os.access(db_dir, os.W_OK)}")
        else:
            logger.info("Database directory does not exist yet - will be created if needed")
    
    elif database_url.startswith('mysql'):
        logger.info(f"MySQL database detected: {database_url[:50]}...")
        logger.info("Skipping local file verification for MySQL database")
        logger.info("MySQL database will be accessed remotely")
    
    elif database_url.startswith('postgresql'):
        logger.info(f"PostgreSQL database detected: {database_url[:50]}...")
        logger.info("Skipping local file verification for PostgreSQL database")
        logger.info("PostgreSQL database will be accessed remotely")
    
    else:
        logger.info(f"Unknown database type: {database_url[:50]}...")
        logger.info("Skipping verification for unknown database type")

def get_sqlalchemy_config():
    """
    Get SQLAlchemy configuration dictionary
    """
    database_url = get_database_url()
    config = {
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    
    # Add engine options for production databases
    if database_url.startswith('postgresql'):
        # SSL configuration for PostgreSQL with pg8000 driver
        connect_args = {}
        
        # Check if we're in production (Render.com or similar)
        if 'render.com' in database_url or os.getenv('RENDER'):
            # For pg8000 driver, we need to use ssl_context
            import ssl
            ssl_context = ssl.create_default_context()
            connect_args['ssl_context'] = ssl_context
            logger.info("Production environment detected - enabling SSL context for pg8000 driver")
        else:
            # For other PostgreSQL instances, try to use SSL if available
            import ssl
            ssl_context = ssl.create_default_context()
            connect_args['ssl_context'] = ssl_context
            logger.info("PostgreSQL detected - enabling SSL context for pg8000 driver")
        
        config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 1,  # Minimal for free tier
            'pool_recycle': 300,  # 5 minutes
            'pool_pre_ping': False,  # Disable pre-ping to avoid connection issues
            'pool_timeout': 10,  # 10 seconds timeout
            'max_overflow': 1,  # Allow only 1 additional connection
            'pool_reset_on_return': 'commit',  # Reset connections on return
            'connect_args': connect_args
        }
    elif database_url.startswith('mysql'):
        config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 1,  # Minimal for free tier
            'pool_recycle': 300,  # 5 minutes
            'pool_pre_ping': False,  # Disable pre-ping to avoid connection issues
            'pool_timeout': 10,  # 10 seconds timeout
            'max_overflow': 1,  # Allow only 1 additional connection
            'pool_reset_on_return': 'commit',  # Reset connections on return
            'connect_args': {
                'charset': 'utf8mb4'
            }
        }
    
    return config 