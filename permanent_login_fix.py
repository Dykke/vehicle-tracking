"""
Permanent Login Fix

This script creates a permanent solution for the login issue by:
1. Modifying the User model to use a specific hash method
2. Creating users with the correct hash method
3. Adding the fix to the reset_database.py script
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash
import shutil

# Force SQLite for local development
print("Using SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def fix_user_model():
    """Update the User model to use a specific hash method."""
    try:
        user_model_path = 'models/user.py'
        backup_path = 'models/user.py.bak'
        
        # Create a backup
        shutil.copy2(user_model_path, backup_path)
        print(f"Created backup of User model at {backup_path}")
        
        # Read the current model
        with open(user_model_path, 'r') as f:
            content = f.read()
        
        # Replace the set_password method to use a specific hash method
        if 'def set_password(self, password):' in content:
            old_method = """    def set_password(self, password):
        self.password_hash = generate_password_hash(password)"""
            
            new_method = """    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)"""
            
            content = content.replace(old_method, new_method)
            
            # Write the updated model
            with open(user_model_path, 'w') as f:
                f.write(content)
            
            print("Updated User.set_password method to use pbkdf2:sha256 hash method")
        else:
            print("Could not find set_password method in User model")
        
        return True
    except Exception as e:
        print(f"Error updating User model: {str(e)}")
        return False

def create_users_with_correct_hash():
    """Create users with the correct hash method."""
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
        admin_password_hash = generate_password_hash(admin_password, method='pbkdf2:sha256', salt_length=8)
        
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
        operator_password_hash = generate_password_hash(operator_password, method='pbkdf2:sha256', salt_length=8)
        
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
        
        print("Users created with correct hash method.")
        return True
    except Exception as e:
        print(f"Error creating users: {str(e)}")
        return False

def update_reset_database_script():
    """Update the reset_database.py script to use the correct hash method."""
    try:
        reset_script_path = 'reset_database.py'
        backup_path = 'reset_database.py.bak'
        
        # Create a backup
        shutil.copy2(reset_script_path, backup_path)
        print(f"Created backup of reset_database.py at {backup_path}")
        
        # Read the current script
        with open(reset_script_path, 'r') as f:
            content = f.read()
        
        # Replace the password hash generation
        if 'admin_password_hash = generate_password_hash(admin_password)' in content:
            old_line = 'admin_password_hash = generate_password_hash(admin_password)'
            new_line = 'admin_password_hash = generate_password_hash(admin_password, method=\'pbkdf2:sha256\', salt_length=8)'
            
            content = content.replace(old_line, new_line)
            
            # Also replace the operator password hash generation
            old_line = 'operator_password_hash = generate_password_hash(operator_password)'
            new_line = 'operator_password_hash = generate_password_hash(operator_password, method=\'pbkdf2:sha256\', salt_length=8)'
            
            content = content.replace(old_line, new_line)
            
            # Write the updated script
            with open(reset_script_path, 'w') as f:
                f.write(content)
            
            print("Updated reset_database.py to use pbkdf2:sha256 hash method")
        else:
            print("Could not find password hash generation in reset_database.py")
        
        return True
    except Exception as e:
        print(f"Error updating reset_database.py: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting permanent login fix...")
    
    # Step 1: Update the User model
    if fix_user_model():
        print("✓ User model updated successfully")
    else:
        print("✗ Failed to update User model")
    
    # Step 2: Create users with correct hash
    if create_users_with_correct_hash():
        print("✓ Users created successfully")
    else:
        print("✗ Failed to create users")
    
    # Step 3: Update reset_database.py
    if update_reset_database_script():
        print("✓ reset_database.py updated successfully")
    else:
        print("✗ Failed to update reset_database.py")
    
    print("\nPermanent login fix completed. You should now be able to log in with:")
    print("  Admin: admin / admin123")
    print("  Operator: operator / operator123")
    print("\nThese credentials will persist even after restarting the server or resetting the database.")
