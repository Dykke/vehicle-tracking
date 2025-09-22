import os
import time
import logging
import sys
from dotenv import load_dotenv
from flask import Flask
from models import db
from models.user import User, Vehicle
# import pymysql - removed for PostgreSQL

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# No longer needed for PostgreSQL
# pymysql.install_as_MySQLdb()

load_dotenv()

def create_app():
    logger.info("Creating Flask application")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

    # Configure database URL for PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set!")
        raise ValueError("DATABASE_URL environment variable is required")
        
    logger.info(f"Database URL format: {database_url[:8]}...")  # Log just the beginning for security
    
    # Handle Render's postgres:// URLs (convert to postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info("Converted postgres:// URL to postgresql://")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # SSL configuration for PostgreSQL with pg8000 driver
    connect_args = {'connect_timeout': 30}
    
    # Check if we're in production (Render.com or similar)
    if 'render.com' in database_url or os.getenv('RENDER'):
        import ssl
        ssl_context = ssl.create_default_context()
        connect_args['ssl_context'] = ssl_context
        logger.info("Production environment detected - enabling SSL context for pg8000 driver")
    elif database_url.startswith('postgresql'):
        import ssl
        ssl_context = ssl.create_default_context()
        connect_args['ssl_context'] = ssl_context
        logger.info("PostgreSQL detected - enabling SSL context for pg8000 driver")
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 1,  # Minimal for free tier
        'pool_recycle': 300,  # 5 minutes
        'pool_pre_ping': False,  # Disable pre-ping to avoid connection issues
        'pool_timeout': 5,  # 5 seconds timeout
        'max_overflow': 0,  # No additional connections
        'pool_reset_on_return': 'commit',  # Reset connections on return
        'connect_args': connect_args
    }

    logger.info("Initializing SQLAlchemy with Flask app")
    db.init_app(app)
    return app

def initialize_database(max_retries=5, retry_delay=5):
    logger.info("==== Starting database initialization ====")
    app = create_app()
    retries = 0
    while retries < max_retries:
        try:
            with app.app_context():
                logger.info("Checking database connection...")
                # Test the connection
                conn = db.engine.connect()
                conn.close()
                logger.info("Database connection successful")
                
                logger.info("Creating all database tables directly (bypassing migrations)...")
                # Explicitly import all models to ensure they're registered
                try:
                    from models.user import User, Vehicle, LocationLog
                    from models.notification import Notification, NotificationSetting
                    logger.info("Models imported successfully")
                except ImportError as e:
                    logger.error(f"Error importing models: {e}")
                
                # Force-create all tables
                db.create_all()
                logger.info("Tables created successfully")
                
                # List tables for verification
                try:
                    inspector = db.inspect(db.engine)
                    tables = inspector.get_table_names()
                    logger.info(f"Database tables: {tables}")
                except Exception as e:
                    logger.error(f"Could not list tables: {e}")
                
                # Check if admin user exists
                admin = User.query.filter_by(email='admin@example.com').first()
                if not admin:
                    # Create admin user
                    logger.info("Admin user not found, creating...")
                    admin = User(
                        username='admin',
                        email='admin@example.com',
                        user_type='operator'
                    )
                    admin.set_password('admin123')  # Change this password!
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("Admin user created successfully")
                else:
                    logger.info("Admin user already exists")
                
                logger.info("==== Database initialization completed successfully ====")
                return True
        except Exception as e:
            retries += 1
            logger.error(f"Database initialization failed (attempt {retries}/{max_retries}): {str(e)}")
            if retries < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Maximum retries reached. Database initialization failed.")
                logger.error("==== Database initialization FAILED ====")
                return False

if __name__ == '__main__':
    success = initialize_database()
    if not success:
        logger.error("Exiting with error due to database initialization failure")
        sys.exit(1)
    logger.info("Database initialization script completed successfully") 