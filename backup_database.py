"""
Database Backup Script
Creates a backup of the current database before any operations
"""
import sqlite3
import shutil
import os
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
    source_db = 'app.db'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_db = f'app.db.backup_{timestamp}'
    
    if not os.path.exists(source_db):
        print(f"❌ Source database {source_db} does not exist!")
        return False
    
    try:
        # Copy the database file
        shutil.copy2(source_db, backup_db)
        print(f"✅ Database backed up to: {backup_db}")
        
        # Verify backup
        if os.path.exists(backup_db):
            source_size = os.path.getsize(source_db)
            backup_size = os.path.getsize(backup_db)
            print(f"📁 Source size: {source_size} bytes")
            print(f"📁 Backup size: {backup_size} bytes")
            
            if source_size == backup_size:
                print("✅ Backup verification successful")
                return True
            else:
                print("❌ Backup verification failed - sizes don't match")
                return False
        else:
            print("❌ Backup file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def restore_database(backup_file):
    """Restore database from backup"""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file {backup_file} does not exist!")
        return False
    
    try:
        # Create backup of current database before restore
        current_backup = f'app.db.before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        if os.path.exists('app.db'):
            shutil.copy2('app.db', current_backup)
            print(f"✅ Current database backed up to: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_file, 'app.db')
        print(f"✅ Database restored from: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Backup Tool")
    print("1. Create backup")
    print("2. Restore from backup")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        backup_database()
    elif choice == "2":
        backup_file = input("Enter backup filename: ").strip()
        restore_database(backup_file)
    else:
        print("Invalid choice")
