from flask import Flask
from models import db
import traceback
import os
from sqlalchemy import create_engine, inspect, text

def add_route_column():
    """Add the route column to the vehicles table"""
    try:
        print("Starting migration: Adding 'route' column to vehicles table...")
        
        # Get database URL from environment or use default
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        
        # Handle SQLite vs PostgreSQL
        if database_url.startswith('sqlite'):
            engine = create_engine(database_url)
            sql = "ALTER TABLE vehicles ADD COLUMN route VARCHAR(50);"
        else:
            # Render.com PostgreSQL URL fix
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            engine = create_engine(database_url)
            sql = "ALTER TABLE vehicles ADD COLUMN route VARCHAR(50);"
        
        # Check if the column already exists to avoid error
        inspector = inspect(engine)
        columns = inspector.get_columns('vehicles')
        column_names = [c['name'] for c in columns]
        
        if 'route' not in column_names:
            # Execute the SQL to add the column
            with engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
            print("Successfully added 'route' column to vehicles table")
        else:
            print("'route' column already exists in vehicles table")
            
        return True
        
    except Exception as e:
        print(f"Error adding 'route' column to vehicles table: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    add_route_column() 