"""
Fix Admin Password Script

This script updates the admin password to ensure it matches the expected value.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

# Force SQLite for local development
print("Using SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def fix_admin_password():
    """Reset the admin password to the default."""
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
        admin_password_hash = generate_password_hash(admin_password)
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
        admin = cursor.fetchone()
        
        if admin:
            # Update the admin password
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (admin_password_hash, admin_username)
            )
            print(f"Admin password has been reset to: {admin_password}")
        else:
            print("Admin user not found. Creating new admin user...")
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
                (admin_username, 'admin@example.com', admin_password_hash, 'admin', 1)
            )
            print(f"New admin user created with password: {admin_password}")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Password update complete!")
    
    except Exception as e:
        print(f"Error fixing admin password: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    fix_admin_password()
