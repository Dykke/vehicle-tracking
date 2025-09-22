from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from flask_cors import CORS
from models import db
from models.user import User
import os
import logging
from logging.handlers import RotatingFileHandler
import sys
import time
from werkzeug.serving import run_simple
from secure_config import get_secret_key, create_env_example
from datetime import timedelta

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create file handler
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Import blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.driver import driver_bp
from routes.public import public_bp
from routes.operator import operator_bp
from routes.api import api_bp
from routes.notifications import notifications_bp
from routes.commuter import commuter_bp

# Import event handlers
import events_optimized

# Create Flask app
app = Flask(__name__)
app.config.from_object('db_config')

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Set secret key from environment or generate a secure one
app.config['SECRET_KEY'] = get_secret_key()

# Configure Flask session settings for better persistence
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # 24 hour session lifetime
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request
app.config['SESSION_COOKIE_NAME'] = 'drive_monitoring_session'  # Custom session cookie name

# CRITICAL FIX: Load database configuration BEFORE initializing database
from db_config import get_sqlalchemy_config
db_config = get_sqlalchemy_config()
app.config.update(db_config)

# Initialize database with proper configuration
db.init_app(app)

# Verify database path for debugging and ensure consistency
from db_config import verify_database_path, get_database_url
with app.app_context():
    verify_database_path()
    db_url = get_database_url()
    logger.info(f"Flask app using database: {db_url}")
    
    # Ensure the database directory exists (only for SQLite)
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        # Handle both absolute and relative paths
        if os.path.isabs(db_path):
            db_dir = os.path.dirname(db_path)
        else:
            # For relative paths, resolve against current working directory
            db_dir = os.path.dirname(os.path.abspath(db_path))
        
        # Only create directory if it's not empty and doesn't exist
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.warning(f"Could not create database directory {db_dir}: {e}")
                logger.info("Database will be created in current working directory if possible")
        elif db_dir:
            logger.info(f"Database directory exists: {db_dir}")
        else:
            logger.warning("Database directory path is empty - using current working directory")

# Create .env.example file if it doesn't exist
with app.app_context():
    create_env_example()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Disable automatic context processor to avoid database queries on public pages
login_manager._context_processor = None

# Custom context processor that only loads user data when needed
@app.context_processor
def inject_user():
    from flask import request
    from flask_login import current_user
    # Only load user data for non-public routes
    if request.endpoint == 'index':
        return {}  # Return empty context for public page
    return dict(current_user=current_user)

# Initialize Socket.IO with threading mode for Python 3.13 compatibility
import os
async_mode = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)

# Register Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    events_optimized.handle_connect()

@socketio.on('disconnect')
def handle_disconnect():
    events_optimized.handle_disconnect()

@socketio.on('location_update')
def handle_location_event(data):
    events_optimized.handle_location_update(data)

@socketio.on('request_vehicle_positions')
def handle_request_vehicle_positions():
    events_optimized.handle_request_vehicle_positions()

@socketio.on('join_vehicle_room')
def handle_join_vehicle_room(data):
    events_optimized.handle_join_vehicle_room(data)

@socketio.on('driver_vehicle_update')
def handle_driver_vehicle_update(data):
    events_optimized.handle_driver_vehicle_update(data)

@socketio.on('driver_status_update')
def handle_driver_status_update(data):
    events_optimized.handle_driver_status_update(data)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(driver_bp, url_prefix='/driver')
app.register_blueprint(commuter_bp, url_prefix='/commuter')  # Register commuter blueprint
app.register_blueprint(public_bp, url_prefix='/public')
app.register_blueprint(operator_bp, url_prefix='/operator')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(notifications_bp)

# Add diagnostic endpoints for performance testing
@app.route('/ping')
def ping():
    return 'pong', 200

@app.route('/health')
def health():
    """Simple health check without database access"""
    return {'status': 'healthy', 'timestamp': time.time()}, 200

@app.route('/db-ping')
def db_ping():
    import time
    t0 = time.time()
    try:
        # Test database connection with timeout
        db.session.execute('SELECT 1')
        db.session.commit()
        took_ms = int((time.time() - t0) * 1000)
        return {'ok': True, 'took_ms': took_ms}, 200
    except Exception as e:
        took_ms = int((time.time() - t0) * 1000)
        # Return 200 with error info instead of 500 to avoid breaking the app
        return {'ok': False, 'error': str(e), 'took_ms': took_ms, 'status': 'database_unavailable'}, 200

# Root route - PUBLIC PAGE (no authentication required)
@app.route('/')
def index():
    # Skip user loading for public page to avoid database queries
    return render_template('public/map.html')

# Check if running in development mode
def is_development_mode():
    return os.environ.get('FLASK_ENV') == 'development' or app.debug

# Create database tables if they don't exist
with app.app_context():
    try:
        # Check if we need to bypass migrations
        bypass_migrations = True
        
        if bypass_migrations:
            logger.info("BYPASSING migrations and using safe table creation...")
            try:
                # Import all models to ensure they're registered with SQLAlchemy
                from models.user import User
                # Check if vehicle model exists
                try:
                    from models.vehicle import Vehicle
                except ImportError:
                    logger.warning("models.vehicle not found, skipping import")
                
                # Check if location_log model exists
                try:
                    from models.location_log import LocationLog
                except ImportError:
                    logger.warning("models.location_log not found, skipping import")
                
                # Check if notification model exists
                try:
                    from models.notification import Notification, NotificationSetting
                except ImportError:
                    logger.warning("models.notification not found, skipping import")
                
                logger.info("Models imported successfully")
                
                # CRITICAL FIX: Check if database file actually exists before checking tables
                db_url = get_database_url()
                if db_url.startswith('sqlite:///'):
                    db_file_path = db_url.replace('sqlite:///', '')
                    # Handle relative paths
                    if not os.path.isabs(db_file_path):
                        db_file_path = os.path.abspath(db_file_path)
                    
                    db_exists = os.path.exists(db_file_path)
                    db_size = os.path.getsize(db_file_path) if db_exists else 0
                    
                    logger.info(f"Database file path: {db_file_path}")
                    logger.info(f"Database file exists: {db_exists}")
                    logger.info(f"Database file size: {db_size} bytes")
                    
                    # If database file is very small (< 100 bytes), it's likely newly created
                    if db_exists and db_size < 100:
                        logger.info("Database file exists but is very small - likely newly created")
                        db_exists = False  # Treat as new database
                else:
                    db_exists = True  # For non-SQLite databases, assume they exist
                
                # SAFE TABLE CREATION: Check if tables exist before creating
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                logger.info(f"Existing tables: {existing_tables}")
                
                # Only create tables if database is truly new (no file or very small file)
                if not db_exists or not existing_tables:
                    logger.info("Database is new or empty, creating all tables...")
                    db.create_all()
                    logger.info("Tables created successfully using create_all()")
                else:
                    logger.info("Database exists with data, skipping table creation to preserve data")
                    
                    # Verify all required tables exist
                    required_tables = ['users', 'vehicles', 'location_logs', 'notifications', 'notification_settings']
                    missing_tables = [table for table in required_tables if table not in existing_tables]
                    
                    if missing_tables:
                        logger.warning(f"Missing tables: {missing_tables}")
                        logger.info("Creating missing tables only...")
                        db.create_all()
                        logger.info("Missing tables created successfully")
                    else:
                        logger.info("All required tables exist ✓")
                
                # List all tables to verify
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                logger.info(f"Final tables: {table_names}")
                
                # Check if vehicles table exists
                if 'vehicles' in table_names:
                    # Ensure required columns exist in vehicles table
                    logger.info("Ensuring required columns exist in vehicles table...")
                    vehicle_columns = [column['name'] for column in inspector.get_columns('vehicles')]
                    logger.info(f"Existing columns in vehicles table: {vehicle_columns}")
                    
                    # Check for specific columns that must exist
                    required_columns = ['accuracy', 'route', 'route_info']
                    for col in required_columns:
                        if col in vehicle_columns:
                            logger.info(f"Column {col} already exists")
                        else:
                            logger.warning(f"Column {col} is missing!")
                    
                    logger.info("Column check completed")
                    
                    # Verify all columns are present
                    vehicle_columns = [column['name'] for column in inspector.get_columns('vehicles')]
                    logger.info(f"VERIFICATION - Vehicle columns after setup: {vehicle_columns}")
                    logger.info("ALL REQUIRED COLUMNS VERIFIED ✓")
                else:
                    logger.warning("Vehicles table not found, skipping column verification")
            except Exception as inner_e:
                logger.error(f"Error during model import or table creation: {str(inner_e)}")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    try:
        # Run the app
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        logger.info(f"Starting server on {host}:{port} with debug={debug}")
        logger.info("Using threading mode for Socket.IO")
        
        # Check Flask version to determine if allow_unsafe_werkzeug is supported
        import flask
        flask_version = flask.__version__
        logger.info(f"Flask version: {flask_version}")
        
        if debug:
            # For newer Flask versions
            try:
                socketio.run(app, host=host, port=port, debug=debug)
            except TypeError:
                # For older Flask versions that might support allow_unsafe_werkzeug
                try:
                    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
                except TypeError:
                    logger.warning("Neither socketio.run() signature worked, falling back to app.run()")
                    app.run(host=host, port=port, debug=debug)
        else:
            # Production mode
            run_simple(host, port, app, use_reloader=False, use_debugger=False)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        print("Server startup failed!")
        sys.exit(1)