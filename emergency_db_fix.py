"""
EMERGENCY DATABASE FIX SCRIPT
Run this directly from the Render console to add missing columns
"""
import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set!")
        return 1
    
    # Handle Render's postgres:// URLs
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info("Converted postgres:// URL to postgresql://")
    
    logger.info("Attempting to connect to database...")
    
    try:
        # Connect directly with psycopg2
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        logger.info("Connected to database successfully")
        
        # Check if vehicles table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'vehicles')")
        if not cursor.fetchone()[0]:
            logger.error("CRITICAL ERROR: 'vehicles' table does not exist!")
            return 1
        
        logger.info("Vehicles table exists")
        
        # Check for existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vehicles'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing columns in vehicles table: {existing_columns}")
        
        # Define columns to add
        columns_to_add = [
            ("accuracy", "FLOAT"),
            ("route", "VARCHAR(255)"),
            ("route_info", "JSON")
        ]
        
        # Add missing columns one by one in a transaction
        try:
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    logger.info(f"Adding column: {column_name} ({column_type})...")
                    
                    try:
                        # Try standard syntax first
                        cursor.execute(f"ALTER TABLE vehicles ADD COLUMN {column_name} {column_type}")
                        logger.info(f"Successfully added {column_name} column")
                    except Exception as e:
                        logger.error(f"Error adding {column_name} column: {str(e)}")
                        
                        try:
                            # Try alternative syntax
                            cursor.execute(f"ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
                            logger.info(f"Successfully added {column_name} column with IF NOT EXISTS syntax")
                        except Exception as e2:
                            logger.error(f"All attempts to add {column_name} column failed: {str(e2)}")
                            conn.rollback()
                            return 1
                else:
                    logger.info(f"Column {column_name} already exists")
            
            # Commit all changes
            conn.commit()
            logger.info("All column additions committed successfully")
            
            # Verify the columns were added
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'vehicles'
            """)
            final_columns = [row[0] for row in cursor.fetchall()]
            logger.info(f"Final columns in vehicles table: {final_columns}")
            
            # Check if all required columns exist
            missing = [col for col, _ in columns_to_add if col not in final_columns]
            if missing:
                logger.error(f"VERIFICATION FAILED: Columns still missing: {missing}")
                return 1
            else:
                logger.info("VERIFICATION SUCCESSFUL: All required columns exist")
                
        except Exception as e:
            logger.error(f"Transaction error: {str(e)}")
            conn.rollback()
            return 1
        finally:
            cursor.close()
            conn.close()
        
        return 0
        
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 