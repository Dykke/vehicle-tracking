import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import inspect, text
from models import db
from db_config import get_sqlalchemy_config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure database using our helper module
    app.config.update(get_sqlalchemy_config())
    
    db.init_app(app)
    return app

def check_db_schema(app):
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Database tables: {tables}")
        
        if 'vehicles' not in tables:
            logger.error("CRITICAL ERROR: 'vehicles' table does not exist!")
            return False
        
        # Check columns in vehicles table
        columns = {col['name']: col for col in inspector.get_columns('vehicles')}
        logger.info(f"Columns in vehicles table: {list(columns.keys())}")
        
        # Check for required columns
        required_columns = {
            'accuracy': 'FLOAT',
            'route': 'VARCHAR(255)',
            'route_info': 'JSON'
        }
        
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
            
            # Add missing columns
            conn = db.engine.connect()
            for col_name, col_type in missing_columns:
                logger.info(f"Adding column {col_name} ({col_type}) to vehicles table...")
                try:
                    conn.execute(text(f"ALTER TABLE vehicles ADD COLUMN {col_name} {col_type}"))
                    logger.info(f"Successfully added {col_name} column")
                except Exception as e:
                    logger.error(f"Error adding {col_name} column: {str(e)}")
                    try:
                        # Try alternative syntax
                        conn.execute(text(f"ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                        logger.info(f"Successfully added {col_name} column using IF NOT EXISTS")
                    except Exception as e2:
                        logger.error(f"All attempts to add {col_name} column failed: {str(e2)}")
                        return False
            conn.close()
            
            # Verify columns were added
            inspector = inspect(db.engine)
            updated_columns = {col['name'] for col in inspector.get_columns('vehicles')}
            logger.info(f"Updated columns in vehicles table: {updated_columns}")
            
            for col_name, _ in missing_columns:
                if col_name not in updated_columns:
                    logger.error(f"Failed to add column {col_name}")
                    return False
        
        return True

def main():
    app = create_app()
    success = check_db_schema(app)
    
    if success:
        logger.info("Database schema check completed successfully!")
        return 0
    else:
        logger.error("Database schema check failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 