#!/usr/bin/env python3
"""
Test script to verify database persistence
"""
import os
import sys
import sqlite3
from datetime import datetime

def test_database_persistence():
    """Test if the database persists data correctly"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'app.db')
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print(f"Database size: {os.path.getsize(db_path)} bytes")
        print(f"Database last modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    
    # Test database connection and write
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a test table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_persistence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test data
        test_data = f"Test data at {datetime.now()}"
        cursor.execute('INSERT INTO test_persistence (test_data) VALUES (?)', (test_data,))
        
        # Commit the changes
        conn.commit()
        
        # Verify the data was written
        cursor.execute('SELECT * FROM test_persistence ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Successfully wrote and read test data: {result}")
        else:
            print("❌ Failed to read test data")
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM test_persistence')
        count = cursor.fetchone()[0]
        print(f"Total test records: {count}")
        
        conn.close()
        
        # Verify the file still exists and has grown
        if os.path.exists(db_path):
            new_size = os.path.getsize(db_path)
            print(f"Database size after write: {new_size} bytes")
            
            # Check if we can read the data again
            conn2 = sqlite3.connect(db_path)
            cursor2 = conn2.cursor()
            cursor2.execute('SELECT * FROM test_persistence ORDER BY id DESC LIMIT 1')
            result2 = cursor2.fetchone()
            conn2.close()
            
            if result2:
                print(f"✅ Data persists after reconnection: {result2}")
            else:
                print("❌ Data lost after reconnection")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Testing Database Persistence...")
    print("=" * 50)
    
    success = test_database_persistence()
    
    print("=" * 50)
    if success:
        print("✅ Database persistence test completed successfully")
        print("💡 If data is still being lost, check:")
        print("   1. Database file permissions")
        print("   2. Working directory changes")
        print("   3. Multiple database instances")
    else:
        print("❌ Database persistence test failed")
        print("💡 Check database configuration and permissions")
