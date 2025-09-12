"""
Direct SQL script to add missing columns to vehicles table
This is a backup solution in case migrations don't work
"""
from app import app
from models import db
from sqlalchemy import text

print("Starting direct column additions...")

with app.app_context():
    connection = db.engine.connect()
    
    # Add accuracy column if it doesn't exist
    try:
        print("Adding accuracy column...")
        connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS accuracy FLOAT"))
        db.session.commit()
        print("Added accuracy column")
    except Exception as e:
        print(f"Error adding accuracy column: {str(e)}")
    
    # Add route column if it doesn't exist
    try:
        print("Adding route column...")
        connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route VARCHAR(255)"))
        db.session.commit()
        print("Added route column")
    except Exception as e:
        print(f"Error adding route column: {str(e)}")
    
    # Add route_info column if it doesn't exist
    try:
        print("Adding route_info column...")
        connection.execute(text("ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route_info JSON"))
        db.session.commit()
        print("Added route_info column")
    except Exception as e:
        print(f"Error adding route_info column: {str(e)}")
    
    connection.close()

print("Column additions completed.") 