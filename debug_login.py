"""
Debug Login System

This script directly inspects the database and tests the login credentials.
It will show exactly what's happening with the authentication process.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import sys

# Force SQLite for local development
print("Using SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def debug_login():
    """Debug the login system by directly inspecting the database."""
    try:
        # Extract the SQLite database path
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        print(f"Using SQLite database at: {db_path}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users in the database:")
        for user in users:
            print(f"ID: {user['id']}, Username: {user['username']}, Type: {user['user_type']}")
            print(f"  Email: {user['email']}")
            print(f"  Password Hash: {user['password_hash']}")
            print(f"  Active: {user['is_active']}")
            print()
        
        # Test login for admin
        admin_username = 'admin'
        admin_password = 'admin123'
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
        admin = cursor.fetchone()
        
        if admin:
            print(f"Testing login for admin user:")
            print(f"  Stored hash: {admin['password_hash']}")
            
            # Test if password matches
            is_valid = check_password_hash(admin['password_hash'], admin_password)
            print(f"  Password 'admin123' verification: {'SUCCESS' if is_valid else 'FAILED'}")
            
            # Create a new hash for comparison
            new_hash = generate_password_hash(admin_password)
            print(f"  Newly generated hash: {new_hash}")
            print(f"  Would this new hash work? {check_password_hash(new_hash, admin_password)}")
            
            # Try some variations
            print(f"  Testing 'Admin123': {check_password_hash(admin['password_hash'], 'Admin123')}")
            print(f"  Testing 'admin1234': {check_password_hash(admin['password_hash'], 'admin1234')}")
        else:
            print("Admin user not found in database!")
        
        # Test login for operator
        operator_username = 'operator'
        operator_password = 'operator123'
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (operator_username,))
        operator = cursor.fetchone()
        
        if operator:
            print(f"\nTesting login for operator user:")
            print(f"  Stored hash: {operator['password_hash']}")
            
            # Test if password matches
            is_valid = check_password_hash(operator['password_hash'], operator_password)
            print(f"  Password 'operator123' verification: {'SUCCESS' if is_valid else 'FAILED'}")
        else:
            print("Operator user not found in database!")
        
        # Create new users with known working hashes
        print("\nCreating new test users with fresh hashes...")
        
        # Delete test users if they exist
        cursor.execute("DELETE FROM users WHERE username IN ('testadmin', 'testoperator')")
        
        # Create test admin
        test_admin_hash = generate_password_hash('testadmin123')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
            ('testadmin', 'testadmin@example.com', test_admin_hash, 'admin', 1)
        )
        
        # Create test operator
        test_operator_hash = generate_password_hash('testoperator123')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
            ('testoperator', 'testoperator@example.com', test_operator_hash, 'operator', 1)
        )
        
        conn.commit()
        
        print("Test users created successfully:")
        print("  testadmin / testadmin123")
        print("  testoperator / testoperator123")
        print("\nPlease try logging in with these test credentials.")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"Error debugging login: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    debug_login()
