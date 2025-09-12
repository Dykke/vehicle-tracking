"""
Production configuration for Render hosting
"""
import os

class ProductionConfig:
    """Production configuration class"""
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-change-in-production')
    FLASK_ENV = 'production'
    DEBUG = False
    
    # SocketIO
    SOCKETIO_PING_TIMEOUT = int(os.environ.get('SOCKETIO_PING_TIMEOUT', 60))
    SOCKETIO_PING_INTERVAL = int(os.environ.get('SOCKETIO_PING_INTERVAL', 25))
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*')
    
    # Gunicorn
    GUNICORN_TIMEOUT = int(os.environ.get('GUNICORN_TIMEOUT', 120))
    GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', 1))
    GUNICORN_WORKER_CLASS = os.environ.get('GUNICORN_WORKER_CLASS', 'gunicorn.workers.sync.SyncWorker')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def get_database_config():
        """Get database configuration for production"""
        if ProductionConfig.DATABASE_URL:
            # Handle Render's postgres:// URLs
            if ProductionConfig.DATABASE_URL.startswith('postgres://'):
                ProductionConfig.DATABASE_URL = ProductionConfig.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            
            # Use pg8000 dialect for PostgreSQL
            if ProductionConfig.DATABASE_URL.startswith('postgresql://'):
                ProductionConfig.DATABASE_URL = ProductionConfig.DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)
            
            # SSL configuration for production with pg8000 driver
            connect_args = {}
            
            # Always require SSL in production - use ssl_context for pg8000
            import ssl
            ssl_context = ssl.create_default_context()
            connect_args['ssl_context'] = ssl_context
            
            return {
                'SQLALCHEMY_DATABASE_URI': ProductionConfig.DATABASE_URL,
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SQLALCHEMY_ENGINE_OPTIONS': {
                    'pool_size': 10,
                    'pool_recycle': 60,
                    'pool_pre_ping': True,
                    'connect_args': connect_args
                }
            }
        else:
            raise ValueError("DATABASE_URL environment variable is required for production")
