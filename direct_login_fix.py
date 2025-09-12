"""
Direct Login Fix Script

This script directly inserts properly hashed admin and operator passwords into the database.
It bypasses the ORM to ensure the passwords are correctly stored.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Force SQLite for local development
print("Using SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def fix_passwords():
    """Reset the admin and operator passwords with direct SQL."""
    try:
        # Extract the SQLite database path
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        print(f"Using SQLite database at: {db_path}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Admin credentials
        admin_username = 'admin'
        admin_password = 'admin123'
        
        # Generate password hash manually
        admin_password_hash = generate_password_hash(admin_password)
        print(f"Generated admin hash: {admin_password_hash}")
        
        # Delete existing admin user if it exists
        cursor.execute("DELETE FROM users WHERE username = ?", (admin_username,))
        print(f"Deleted existing admin user")
        
        # Create a new admin user with the correct hash
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
            (admin_username, 'admin@example.com', admin_password_hash, 'admin', 1)
        )
        print(f"Created new admin user with username: {admin_username} and password: {admin_password}")
        
        # Verify the hash works
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (admin_username,))
        stored_hash = cursor.fetchone()[0]
        print(f"Stored admin hash: {stored_hash}")
        
        is_valid = check_password_hash(stored_hash, admin_password)
        print(f"Admin password verification test: {'SUCCESS' if is_valid else 'FAILED'}")
        
        # Operator credentials
        operator_username = 'operator'
        operator_password = 'operator123'
        
        # Generate password hash manually
        operator_password_hash = generate_password_hash(operator_password)
        print(f"Generated operator hash: {operator_password_hash}")
        
        # Delete existing operator user if it exists
        cursor.execute("DELETE FROM users WHERE username = ?", (operator_username,))
        print(f"Deleted existing operator user")
        
        # Create a new operator user with the correct hash
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
            (operator_username, 'operator@example.com', operator_password_hash, 'operator', 1)
        )
        print(f"Created new operator user with username: {operator_username} and password: {operator_password}")
        
        # Verify the hash works
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (operator_username,))
        stored_hash = cursor.fetchone()[0]
        print(f"Stored operator hash: {stored_hash}")
        
        is_valid = check_password_hash(stored_hash, operator_password)
        print(f"Operator password verification test: {'SUCCESS' if is_valid else 'FAILED'}")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Password updates complete!")
    
    except Exception as e:
        print(f"Error fixing passwords: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    fix_passwords()