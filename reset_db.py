import os
import sys
import logging
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

load_dotenv()

def reset_database():
    """Reset the database by dropping all tables and disabling migrations"""
    logger.info("==== Starting database reset ====")
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set!")
        return False
    
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info("Converted postgres:// URL to postgresql://")
    
    try:
        # Parse the database URL
        logger.info("Parsing database URL")
        parsed_url = urlparse(database_url)
        
        dbname = parsed_url.path[1:]  # Remove leading slash
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port or 5432
        
        logger.info(f"Connecting to PostgreSQL: host={host}, port={port}, dbname={dbname}, user={user}")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        
        with conn.cursor() as cur:
            logger.info("Connected to database, dropping all tables")
            
            # Check if alembic_version exists and drop it
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
            if cur.fetchone()[0]:
                logger.info("Dropping alembic_version table")
                cur.execute("DROP TABLE alembic_version")
            
            # Drop all tables in public schema
            cur.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            
            logger.info("All tables dropped successfully")
        
        conn.close()
        logger.info("==== Database reset completed successfully ====")
        return True
    
    except Exception as e:
        logger.error(f"Database reset failed: {str(e)}")
        logger.error("==== Database reset FAILED ====")
        return False

if __name__ == '__main__':
    success = reset_database()
    if not success:
        logger.error("Exiting with error due to database reset failure")
        sys.exit(1)
    logger.info("Database reset script completed successfully") 