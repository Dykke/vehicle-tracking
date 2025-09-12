import sqlite3

try:
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Check if vehicles table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicles'")
    if cursor.fetchone():
        print("✅ Vehicles table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(vehicles)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Vehicles table schema ({len(columns)} columns):")
        print("Column ID | Name | Type | Not Null | Default | Primary Key")
        print("-" * 70)
        
        for col in columns:
            print(f"Column: {col}")
            if len(col) >= 6:
                cid, name, type_name, not_null, default_val, pk = col[:6]
                print(f"{cid:9} | {name:20} | {type_name:15} | {not_null:8} | {str(default_val):7} | {pk:12}")
            
        # Check table creation SQL
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='vehicles'")
        create_sql = cursor.fetchone()
        if create_sql:
            print(f"\n🔧 CREATE TABLE SQL:")
            print(create_sql[0])
            
        # Check if there are any existing vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        count = cursor.fetchone()[0]
        print(f"\n📊 Current vehicle count: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, registration_number, vehicle_type FROM vehicles LIMIT 3")
            vehicles = cursor.fetchall()
            print(f"\n🚗 Sample vehicles:")
            for vehicle in vehicles:
                print(f"  ID: {vehicle[0]}, Reg: {vehicle[1]}, Type: {vehicle[2]}")
        
        # Check for specific columns
        print(f"\n🔍 Checking for specific columns:")
        column_names = [col[1] for col in columns]
        
        required_columns = ['id', 'registration_number', 'vehicle_type', 'capacity', 'owner_id', 'assigned_driver_id']
        for col in required_columns:
            if col in column_names:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} - MISSING")
            
    else:
        print("❌ Vehicles table does not exist")
        
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
