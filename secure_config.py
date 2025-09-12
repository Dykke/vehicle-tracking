"""
Secure Configuration Module

This module provides secure access to configuration values with appropriate defaults.
It's designed to be used throughout the application for consistent security practices.
"""

import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Admin credentials
def get_admin_credentials():
    """Get admin credentials from environment variables or use defaults."""
    admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
    return admin_user, admin_pass

# Operator credentials
def get_operator_credentials():
    """Get operator credentials from environment variables or use defaults."""
    operator_user = os.environ.get('OPERATOR_USERNAME', 'operator')
    operator_pass = os.environ.get('OPERATOR_PASSWORD', 'operator123')
    return operator_user, operator_pass

# Flask secret key
def get_secret_key():
    """Get Flask secret key from environment or generate a secure one."""
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        # Generate a secure random key if not set
        secret_key = secrets.token_hex(32)
        print("WARNING: Using a generated SECRET_KEY. Set the SECRET_KEY environment variable for production.")
    return secret_key

# Security settings
RATE_LIMIT_MAX_ATTEMPTS = int(os.environ.get('RATE_LIMIT_MAX_ATTEMPTS', 5))
RATE_LIMIT_LOCKOUT_TIME = int(os.environ.get('RATE_LIMIT_LOCKOUT_TIME', 300))  # 5 minutes
PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))

# Regex patterns for validation
USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
EMAIL_PATTERN = r'^[^@]+@[^@]+\.[^@]+$'

# Create a .env.example file if it doesn't exist
def create_env_example():
    """Create a .env.example file with default values if it doesn't exist."""
    if not os.path.exists('.env.example'):
        with open('.env.example', 'w') as f:
            f.write("""# Database Configuration
DATABASE_URL=sqlite:///app.db
# For PostgreSQL on Render:
# DATABASE_URL=postgres://username:password@host:port/database_name

# Admin Credentials (change these in production)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Operator Credentials (change these in production)
OPERATOR_USERNAME=operator
OPERATOR_PASSWORD=operator123

# Flask Secret Key (generate a secure random key for production)
SECRET_KEY=change_this_to_a_secure_random_key

# Security Settings
RATE_LIMIT_MAX_ATTEMPTS=5
RATE_LIMIT_LOCKOUT_TIME=300
PASSWORD_MIN_LENGTH=8

# Server Configuration
PORT=5000
HOST=0.0.0.0
DEBUG=True
""")
