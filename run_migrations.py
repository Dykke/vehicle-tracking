"""
Script to run database migrations during deployment
Used by render.yaml to ensure all migrations are applied
"""
import os
import sys
import importlib
from flask_migrate import Migrate
from app import app
from models import db
from sqlalchemy import text
import traceback

print("Starting database migrations...")

# Initialize Flask-Migrate
migrate = Migrate(app, db)

try:
    # Import the migration modules
    sys.path.append(os.path.join(os.path.dirname(__file__), 'migrations'))
    
    try:
        import migrations.versions
    except ImportError:
        print("Note: Could not import migrations.versions module directly")
    
    # Run the migrations
    from flask_migrate import upgrade
    print("Running Alembic migrations...")
    upgrade()
    
    print("Database migrations completed successfully.")
    
    # Fallback: Ensure critical columns exist anyway in case migrations fail
    print("Verifying critical columns exist...")
    with app.app_context():
        connection = db.engine.connect()
        
        # Check if accuracy column exists in vehicles table
        try:
            print("Checking for accuracy column...")
            connection.execute(text("SELECT accuracy FROM vehicles LIMIT 1"))
            print("accuracy column exists.")
        except Exception as e:
            if "column vehicles.accuracy does not exist" in str(e):
                print("Adding missing accuracy column...")
                connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS accuracy FLOAT"))
                db.session.commit()
                print("Added accuracy column.")
            else:
                print(f"Error checking accuracy column: {str(e)}")
        
        # Check if route column exists in vehicles table
        try:
            print("Checking for route column...")
            connection.execute(text("SELECT route FROM vehicles LIMIT 1"))
            print("route column exists.")
        except Exception as e:
            if "column vehicles.route does not exist" in str(e):
                print("Adding missing route column...")
                connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route VARCHAR(255)"))
                db.session.commit()
                print("Added route column.")
            else:
                print(f"Error checking route column: {str(e)}")
        
        # Check if route_info column exists in vehicles table
        try:
            print("Checking for route_info column...")
            connection.execute(text("SELECT route_info FROM vehicles LIMIT 1"))
            print("route_info column exists.")
        except Exception as e:
            if "column vehicles.route_info does not exist" in str(e):
                print("Adding missing route_info column...")
                connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route_info JSON"))
                db.session.commit()
                print("Added route_info column.")
            else:
                print(f"Error checking route_info column: {str(e)}")
        
        connection.close()
        
        print("Column verification completed.")
            
except Exception as e:
    print(f"Error during migrations: {str(e)}")
    traceback.print_exc()
    
    print("Attempting direct schema updates as fallback...")
    
    # Direct fallback with basic SQL
    with app.app_context():
        try:
            connection = db.engine.connect()
            
            # Add columns with IF NOT EXISTS to prevent errors if they already exist
            commands = [
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS accuracy FLOAT",
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route VARCHAR(255)",
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route_info JSON"
            ]
            
            for cmd in commands:
                try:
                    print(f"Executing: {cmd}")
                    connection.execute(text(cmd))
                    db.session.commit()
                    print("Command executed successfully.")
                except Exception as cmd_error:
                    print(f"Error executing command: {str(cmd_error)}")
            
            connection.close()
            print("Fallback schema updates completed.")
        except Exception as inner_e:
            print(f"Error during fallback updates: {str(inner_e)}")
            traceback.print_exc() 