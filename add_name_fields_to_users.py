"""
Migration script to add name fields to users table
Run this script to add first_name, middle_name, and last_name columns to the users table
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database configuration
from db_config import get_database_url

def add_name_fields():
    """Add first_name, middle_name, and last_name columns to users table"""
    
    database_url = get_database_url()
    print(f"Database URL: {database_url[:50]}...")
    
    # Create database engine
    engine = create_engine(database_url)
    
    try:
        with engine.begin() as conn:  # begin() auto-commits on success
            # Check if columns already exist
            print("Checking if name fields already exist...")
            
            # For SQLite
            if database_url.startswith('sqlite'):
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'first_name' in columns:
                    print("✓ Name fields already exist in the database")
                    return
                
                print("Adding name fields to users table...")
                
                # Add columns
                conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(100)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN middle_name VARCHAR(100)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(100)"))
                
                print("✓ Successfully added first_name, middle_name, and last_name columns")
            
            # For PostgreSQL
            elif database_url.startswith('postgresql'):
                # Check if columns exist
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                """))
                columns = [row[0] for row in result]
                
                if 'first_name' in columns:
                    print("✓ Name fields already exist in the database")
                    return
                
                print("Adding name fields to users table...")
                
                # Add columns
                conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(100)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN middle_name VARCHAR(100)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(100)"))
                
                print("✓ Successfully added first_name, middle_name, and last_name columns")
            
            # For MySQL
            elif database_url.startswith('mysql'):
                # Check if columns exist
                result = conn.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'users'
                """))
                columns = [row[0] for row in result]
                
                if 'first_name' in columns:
                    print("✓ Name fields already exist in the database")
                    return
                
                print("Adding name fields to users table...")
                
                # Add columns
                conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(100)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN middle_name VARCHAR(100)"))
                conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(100)"))
                
                print("✓ Successfully added first_name, middle_name, and last_name columns")
            
            else:
                print(f"❌ Unsupported database type: {database_url[:20]}")
                sys.exit(1)
        
        print("\n✓ Migration completed successfully!")
        print("\nYou can now use the following fields in the User model:")
        print("  - first_name")
        print("  - middle_name")
        print("  - last_name")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION: Add Name Fields to Users Table")
    print("=" * 60)
    print()
    
    # Confirm before proceeding
    response = input("This will add first_name, middle_name, and last_name columns to the users table.\nContinue? (y/n): ")
    
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    print()
    add_name_fields()
