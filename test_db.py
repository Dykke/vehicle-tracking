import os
import logging
import pg8000
from db_config import get_database_url

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pg8000_connection():
    """Test direct connection to PostgreSQL using pg8000."""
    try:
        # Get database URL from our helper module
        database_url = get_database_url()
        
        # Parse the database URL
        if '@' in database_url and '/' in database_url:
            # Extract components from URL
            auth_part = database_url.split('@')[0].split('://')[1]
            host_part = database_url.split('@')[1].split('/')[0]
            db_name = database_url.split('/')[-1].split('?')[0]
            
            # Extract username and password
            username = auth_part.split(':')[0]
            password = auth_part.split(':')[1] if ':' in auth_part else None
            
            # Extract host and port
            host = host_part.split(':')[0]
            port = int(host_part.split(':')[1]) if ':' in host_part else 5432
            
            logger.info(f"Connecting to PostgreSQL at {host}:{port} as {username}")
            
            # Connect using pg8000
            conn = pg8000.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=db_name
            )
            
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"Connected successfully to PostgreSQL: {version}")
            
            # Close the connection
            cursor.close()
            conn.close()
            
            return True
        else:
            logger.error("Invalid database URL format")
            return False
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_pg8000_connection()
    if success:
        print("Database connection test successful!")
    else:
        print("Database connection test failed!")
        exit(1) 