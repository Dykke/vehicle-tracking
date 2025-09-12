"""
Migration and Server Startup Script

This script:
1. Runs database migrations using direct SQL
2. Creates default admin user if it doesn't exist
3. Starts the Flask development server
"""

import os
import sys
import subprocess
import tempfile
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Force SQLite for local development
print("Forcing SQLite for local development.")
DATABASE_URL = 'sqlite:///app.db'
os.environ['DATABASE_URL'] = DATABASE_URL

def run_command(command):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    
    # Wait for the process to finish
    process.wait()
    
    # Return the exit code
    return process.returncode

def run_migration():
    """Run database migrations using direct SQL."""
    print("Running database migrations...")
    
    # Use direct SQL execution
    print("Using direct SQL execution for migrations.")
    
    if os.path.exists('migrations/complete_schema.sql'):
        # Create a temporary Python file to execute SQL
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write("""
import os
import sqlite3

# Force SQLite for local development
DATABASE_URL = 'sqlite:///app.db'

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

# Commit changes and close connection
conn.commit()
conn.close()
print("SQL migration complete!")
""")
        
        # Execute the temporary Python file
        temp_file_path = f.name
        exit_code = run_command(f'py "{temp_file_path}"')
        
        # Delete the temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass
        
        if exit_code != 0:
            print("SQL execution failed!")
            return False
    else:
        print("No SQL migration file found!")
        return False
    
    return True

def create_admin_user():
    """Create default admin user if it doesn't exist."""
    print("Creating default admin user if it doesn't exist...")
    
    # Create a temporary Python file to create admin user
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write("""
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Force SQLite for local development
DATABASE_URL = 'sqlite:///app.db'

# Extract the SQLite database path
db_path = DATABASE_URL.replace('sqlite:///', '')
if db_path.startswith('/'):
    db_path = db_path[1:]

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if admin user already exists
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
admin_exists = cursor.fetchone()

if not admin_exists:
    # Create admin user
    admin_username = 'admin'
    admin_email = 'admin@example.com'
    admin_password = 'admin123'
    admin_password_hash = generate_password_hash(admin_password)
    
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
        (admin_username, admin_email, admin_password_hash, 'admin', 1)
    )
    
    print(f"Admin user created: {admin_username} / {admin_password}")
else:
    print("Admin user already exists.")

# Check if operator user already exists
cursor.execute("SELECT id FROM users WHERE username = 'operator'")
operator_exists = cursor.fetchone()

if not operator_exists:
    # Create operator user
    operator_username = 'operator'
    operator_email = 'operator@example.com'
    operator_password = 'operator123'
    operator_password_hash = generate_password_hash(operator_password)
    
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, user_type, is_active) VALUES (?, ?, ?, ?, ?)",
        (operator_username, operator_email, operator_password_hash, 'operator', 1)
    )
    
    print(f"Operator user created: {operator_username} / {operator_password}")
else:
    print("Operator user already exists.")

# Commit changes and close connection
conn.commit()
conn.close()
""")
    
    # Execute the temporary Python file
    temp_file_path = f.name
    exit_code = run_command(f'py "{temp_file_path}"')
    
    # Delete the temporary file
    try:
        os.unlink(temp_file_path)
    except:
        pass
    
    if exit_code != 0:
        print("Admin user creation failed!")
        return False
    
    return True

def start_server():
    """Start the Flask development server."""
    print("Starting Flask development server...")
    
    # Start the server using the existing app.py
    exit_code = run_command('py app.py')
    
    if exit_code != 0:
        print("Server startup failed!")
        return False
    
    return True

def main():
    """Main function to run migrations and start the server."""
    # Run migrations
    if not run_migration():
        print("Migration failed! Exiting...")
        return 1
    
    # Create admin user
    if not create_admin_user():
        print("Admin user creation failed! Continuing anyway...")
    
    # Start the server
    if not start_server():
        print("Server startup failed! Exiting...")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())