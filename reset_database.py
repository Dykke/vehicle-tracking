"""
Database Reset Script

This script completely resets the database by:
1. Dropping all existing tables
2. Creating new tables from the complete_schema.sql file
3. Adding default users

Use this script for local development and testing only.
"""

import os
import time
import sqlite3
from werkzeug.security import generate_password_hash

# Force SQLite for local development
print("Forcing SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def reset_database():
    """Reset the database using the complete schema SQL file."""
    try:
        print("WARNING: This will delete all data in the database!")
        print("You have 5 seconds to cancel (Ctrl+C)...")
        
        # Countdown
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("Resetting database...")
        
        # Extract the SQLite database path
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        print(f"Using SQLite database at: {db_path}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read the SQL file
        with open('migrations/complete_schema.sql', 'r') as f:
            sql_script = f.read()
        
        # Split the SQL script into individual statements
        sql_statements = sql_script.split(';')
        
        # Execute each statement
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"Executed SQL: {statement[:50]}...")
                except sqlite3.Error as e:
                    print(f"Error executing SQL statement: {e}")
                    print(f"Statement: {statement}")
        
        # Create admin user with direct SQL
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'admin123'
        admin_password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256', salt_length=8)
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
                (admin_username, admin_email, admin_password_hash, 'admin', 1)
            )
        
        # Create operator user with direct SQL
        operator_username = 'operator'
        operator_email = 'operator@example.com'
        operator_password = 'operator123'
        operator_password_hash = generate_password_hash(operator_password, method='pbkdf2:sha256', salt_length=8)
        
        # Check if operator user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (operator_username,))
        operator_exists = cursor.fetchone()
        
        if not operator_exists:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
                (operator_username, operator_email, operator_password_hash, 'operator', 1)
            )
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Database reset complete!")
        print(f"Admin user created: {admin_username} / {admin_password}")
        print(f"Operator user created: {operator_username} / {operator_password}")
    
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    reset_database()