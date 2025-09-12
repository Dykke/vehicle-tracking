import sqlite3
import os

def check_database():
    db_path = 'app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist!")
        return
    
    print(f"✅ Database file exists: {db_path}")
    print(f"📁 File size: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tables: {[t[0] for t in tables]}")
        
        # Check users
        if 'users' in [t[0] for t in tables]:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Users: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT username, user_type FROM users LIMIT 5")
                users = cursor.fetchall()
                print(f"📝 Sample users: {users}")
        
        # Check vehicles
        if 'vehicles' in [t[0] for t in tables]:
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            vehicle_count = cursor.fetchone()[0]
            print(f"🚗 Vehicles: {vehicle_count}")
            
            if vehicle_count > 0:
                cursor.execute("SELECT registration_number, vehicle_type FROM vehicles LIMIT 5")
                vehicles = cursor.fetchall()
                print(f"📝 Sample vehicles: {vehicles}")
        
        conn.close()
        print("✅ Database check completed successfully")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()
