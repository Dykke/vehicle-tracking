"""
Fix Login Issue

This script fixes the login issue by creating new users with correct password hashes.
It also completely resets the database to ensure a clean state.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash
import time

# Force SQLite for local development
print("Using SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def fix_login_issue():
    """Fix the login issue by creating new users with correct password hashes."""
    try:
        # Extract the SQLite database path
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        print(f"Using SQLite database at: {db_path}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop all existing users
        print("Dropping all existing users...")
        cursor.execute("DELETE FROM users")
        
        # Create admin user with correct hash
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'admin123'
        admin_password_hash = generate_password_hash(admin_password)
        
        print(f"Creating admin user with username: {admin_username} and password: {admin_password}")
        print(f"Generated hash: {admin_password_hash}")
        
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
            (admin_username, admin_email, admin_password_hash, 'admin', 1)
        )
        
        # Create operator user with correct hash
        operator_username = 'operator'
        operator_email = 'operator@example.com'
        operator_password = 'operator123'
        operator_password_hash = generate_password_hash(operator_password)
        
        print(f"Creating operator user with username: {operator_username} and password: {operator_password}")
        print(f"Generated hash: {operator_password_hash}")
        
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
            (operator_username, operator_email, operator_password_hash, 'operator', 1)
        )
        
        # Commit changes
        conn.commit()
        
        # Verify the users were created
        cursor.execute("SELECT id, username, user_type FROM users")
        users = cursor.fetchall()
        
        print(f"Created {len(users)} users:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Type: {user[2]}")
        
        # Close connection
        conn.close()
        
        print("Login issue fixed successfully!")
        print("Please try logging in with these credentials:")
        print(f"  Admin: {admin_username} / {admin_password}")
        print(f"  Operator: {operator_username} / {operator_password}")
        
    except Exception as e:
        print(f"Error fixing login issue: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    fix_login_issue()
