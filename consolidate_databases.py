#!/usr/bin/env python3
"""
Database consolidation script to fix the duplicate database issue
This script will merge data from both database files and ensure consistency
"""
import os
import sqlite3
import shutil
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_paths():
    """Get the paths of both database files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_db = os.path.join(current_dir, 'app.db')
    instance_db = os.path.join(current_dir, 'instance', 'app.db')
    
    return root_db, instance_db

def backup_database(db_path, suffix='.backup'):
    """Create a backup of the database file"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}{suffix}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    return None

def get_table_schema(conn, table_name):
    """Get the schema of a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_table_data(conn, table_name):
    """Get all data from a table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    return cursor.fetchall()

def consolidate_databases():
    """Consolidate the two database files"""
    root_db, instance_db = get_database_paths()
    
    logger.info("🔍 Starting database consolidation...")
    logger.info(f"Root DB: {root_db}")
    logger.info(f"Instance DB: {instance_db}")
    
    # Check if both databases exist
    if not os.path.exists(root_db) and not os.path.exists(instance_db):
        logger.error("❌ No database files found!")
        return False
    
    if not os.path.exists(root_db):
        logger.info("✅ Only instance database exists - moving to root")
        if os.path.exists(instance_db):
            shutil.move(instance_db, root_db)
            logger.info("✅ Database moved to root directory")
        return True
    
    if not os.path.exists(instance_db):
        logger.info("✅ Only root database exists - no consolidation needed")
        return True
    
    # Both databases exist - need to consolidate
    logger.info("⚠️  Both databases exist - consolidating data...")
    
    # Create backups
    root_backup = backup_database(root_db, '.consolidation_backup')
    instance_backup = backup_database(instance_db, '.consolidation_backup')
    
    try:
        # Connect to both databases
        root_conn = sqlite3.connect(root_db)
        instance_conn = sqlite3.connect(instance_db)
        
        # Get list of tables from both databases
        root_cursor = root_conn.cursor()
        instance_cursor = instance_conn.cursor()
        
        root_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        root_tables = [row[0] for row in root_cursor.fetchall()]
        
        instance_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        instance_tables = [row[0] for row in instance_cursor.fetchall()]
        
        logger.info(f"Root DB tables: {root_tables}")
        logger.info(f"Instance DB tables: {instance_tables}")
        
        # Merge tables
        all_tables = list(set(root_tables + instance_tables))
        
        for table in all_tables:
            logger.info(f"Processing table: {table}")
            
            # Check if table exists in both databases
            if table in root_tables and table in instance_tables:
                # Get data from both
                root_data = get_table_data(root_conn, table)
                instance_data = get_table_data(instance_conn, table)
                
                logger.info(f"  Root DB: {len(root_data)} rows")
                logger.info(f"  Instance DB: {len(root_data)} rows")
                
                # Use the database with more data (likely the more recent one)
                if len(instance_data) > len(root_data):
                    logger.info(f"  Using instance DB data (more rows)")
                    # Drop and recreate table in root DB
                    root_cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    
                    # Get schema from instance DB
                    instance_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                    create_sql = instance_cursor.fetchone()[0]
                    root_cursor.execute(create_sql)
                    
                    # Copy data
                    if instance_data:
                        placeholders = ','.join(['?' for _ in instance_data[0]])
                        root_cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", instance_data)
                else:
                    logger.info(f"  Using root DB data (more rows or equal)")
            
            elif table in instance_tables and table not in root_tables:
                # Table only exists in instance DB - copy it
                logger.info(f"  Copying table {table} from instance DB")
                instance_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                create_sql = instance_cursor.fetchone()[0]
                root_cursor.execute(create_sql)
                
                instance_data = get_table_data(instance_conn, table)
                if instance_data:
                    placeholders = ','.join(['?' for _ in instance_data[0]])
                    root_cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", instance_data)
            
            # Table only in root DB - no action needed
        
        # Commit changes
        root_conn.commit()
        logger.info("✅ Database consolidation completed successfully")
        
        # Close connections
        root_conn.close()
        instance_conn.close()
        
        # Remove the instance database
        os.remove(instance_db)
        logger.info("✅ Removed duplicate instance database")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during consolidation: {e}")
        
        # Restore from backups if available
        if root_backup and os.path.exists(root_backup):
            shutil.copy2(root_backup, root_db)
            logger.info("✅ Restored root database from backup")
        
        if instance_backup and os.path.exists(instance_backup):
            shutil.copy2(instance_backup, instance_db)
            logger.info("✅ Restored instance database from backup")
        
        return False

def verify_consolidation():
    """Verify that the consolidation was successful"""
    root_db, instance_db = get_database_paths()
    
    logger.info("🔍 Verifying consolidation...")
    
    if os.path.exists(instance_db):
        logger.error("❌ Instance database still exists!")
        return False
    
    if not os.path.exists(root_db):
        logger.error("❌ Root database not found!")
        return False
    
    # Test database connection
    try:
        conn = sqlite3.connect(root_db)
        cursor = conn.cursor()
        
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"✅ Consolidated database has {len(tables)} tables: {tables}")
        
        # Check total size
        total_size = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_size += count
            logger.info(f"  {table}: {count} rows")
        
        logger.info(f"✅ Total rows across all tables: {total_size}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Consolidation Tool")
    print("=" * 50)
    
    # Consolidate databases
    if consolidate_databases():
        print("✅ Consolidation completed successfully!")
        
        # Verify the result
        if verify_consolidation():
            print("✅ Verification passed - database is ready!")
            print("\n💡 Next steps:")
            print("1. Restart your Flask server")
            print("2. Test that data persists across restarts")
            print("3. Check that new data is being saved correctly")
        else:
            print("❌ Verification failed!")
    else:
        print("❌ Consolidation failed!")
        print("💡 Check the logs above for details")
