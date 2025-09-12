import os
import sys

def check_environment():
    print("🔍 Environment Check")
    print("=" * 50)
    
    # Check DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    print(f"DATABASE_URL: {database_url if database_url else 'NOT SET'}")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    print(f"Python executable: {sys.executable}")
    print(f"Virtual environment: {'venv' in sys.executable}")
    
    # Check for .env file
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ .env file exists")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.split('=', 1) if '=' in line else (line.strip(), '')
                    if 'DATABASE_URL' in key:
                        print(f"   {key.strip()}: {value.strip()[:50]}...")
    else:
        print(f"❌ .env file not found")
    
    # Check Flask environment
    print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'NOT SET')}")
    print(f"FLASK_APP: {os.getenv('FLASK_APP', 'NOT SET')}")

if __name__ == "__main__":
    check_environment()
