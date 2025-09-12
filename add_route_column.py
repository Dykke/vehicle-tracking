import os
from sqlalchemy import create_engine, text, MetaData, Table, select, update

# This script is intended to be run on the Render.com server to add the route column to the vehicles table

def main():
    try:
        # Get database URL from environment variable
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("ERROR: DATABASE_URL environment variable not found")
            return False
        
        # Render.com PostgreSQL URL fix
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        print(f"Connecting to database...")
        engine = create_engine(database_url)
        
        print("Adding 'route' column to vehicles table...")
        with engine.connect() as connection:
            # Step 1: Add the column if it doesn't exist
            sql = "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS route VARCHAR(50);"
            connection.execute(text(sql))
            
            # Step 2: Set default values for existing vehicles
            # This helps with existing records that would otherwise have NULL route values
            sql = """
            UPDATE vehicles 
            SET route = 'Default Route' 
            WHERE route IS NULL;
            """
            connection.execute(text(sql))
            
            connection.commit()
        
        print("Migration successful: Added 'route' column to vehicles table and set default values")
        return True
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 