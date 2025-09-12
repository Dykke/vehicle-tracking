import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_running_database():
    print("🔍 Checking Running Database Configuration")
    print("=" * 60)
    
    # Load environment variables first
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment variables
    print("📋 Environment Variables:")
    database_url = os.getenv('DATABASE_URL')
    print(f"   DATABASE_URL: {database_url[:50] if database_url else 'NOT SET'}...")
    print(f"   FLASK_ENV: {os.getenv('FLASK_ENV', 'NOT SET')}")
    
    # Import and check db_config
    try:
        from db_config import get_database_url, get_sqlalchemy_config
        print("\n📋 Database Configuration:")
        
        # Get the actual database URL being used
        actual_db_url = get_database_url()
        print(f"   Actual Database URL: {actual_db_url[:50]}...")
        
        # Get SQLAlchemy config
        sqlalchemy_config = get_sqlalchemy_config()
        print(f"   SQLAlchemy URI: {sqlalchemy_config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        
        # Check if it's PostgreSQL
        if 'postgresql' in actual_db_url:
            print("   🐘 Database Type: PostgreSQL (Remote)")
            print("   📍 Location: Render Cloud")
        elif 'mysql' in actual_db_url:
            print("   🐬 Database Type: MySQL (Remote)")
            print("   📍 Location: Railway")
        elif 'sqlite' in actual_db_url:
            print("   🗄️ Database Type: SQLite (Local)")
            print("   📍 Location: Local file (app.db)")
        else:
            print("   ❓ Database Type: Unknown")
            
        print(f"\n💡 Key Insight:")
        if 'postgresql' in actual_db_url:
            print("   Your app is using PostgreSQL on Render, NOT local SQLite!")
            print("   This explains why data 'disappears' from app.db")
        elif 'sqlite' in actual_db_url:
            print("   Your app is using local SQLite database")
            
    except ImportError as e:
        print(f"❌ Error importing db_config: {e}")
    except Exception as e:
        print(f"❌ Error checking database config: {e}")

if __name__ == "__main__":
    check_running_database()
