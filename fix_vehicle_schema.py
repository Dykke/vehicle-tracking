import sqlite3

def fix_vehicle_schema():
    """Add missing columns to the vehicles table."""
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute('PRAGMA table_info(vehicles)')
        current_columns = [col[1] for col in cursor.fetchall()]
        print("Current columns:", current_columns)
        
        # Add missing columns
        missing_columns = []
        
        if 'vehicle_type' not in current_columns:
            missing_columns.append('vehicle_type')
            cursor.execute('ALTER TABLE vehicles ADD COLUMN vehicle_type VARCHAR(50) DEFAULT "bus"')
            print("✅ Added vehicle_type column")
        
        if 'capacity' not in current_columns:
            missing_columns.append('capacity')
            cursor.execute('ALTER TABLE vehicles ADD COLUMN capacity INTEGER DEFAULT 50')
            print("✅ Added capacity column")
        
        if 'assigned_driver_id' not in current_columns:
            missing_columns.append('assigned_driver_id')
            cursor.execute('ALTER TABLE vehicles ADD COLUMN assigned_driver_id INTEGER')
            print("✅ Added assigned_driver_id column")
        
        if 'status' not in current_columns:
            missing_columns.append('status')
            cursor.execute('ALTER TABLE vehicles ADD COLUMN status VARCHAR(20) DEFAULT "active"')
            print("✅ Added status column")
        
        if missing_columns:
            print(f"✅ Added {len(missing_columns)} missing columns: {missing_columns}")
        else:
            print("✅ All required columns already exist")
        
        # Verify the changes
        cursor.execute('PRAGMA table_info(vehicles)')
        new_columns = [col[1] for col in cursor.fetchall()]
        print("\nUpdated columns:", new_columns)
        
        # Check if we can now query assigned_driver_id
        try:
            cursor.execute('SELECT COUNT(*) FROM vehicles WHERE assigned_driver_id IS NOT NULL')
            count = cursor.fetchone()[0]
            print(f"✅ assigned_driver_id column is working. Vehicles with assigned drivers: {count}")
        except Exception as e:
            print(f"❌ assigned_driver_id column still has issues: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Vehicle schema fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing vehicle schema: {e}")
        try:
            conn.rollback()
        except:
            pass

if __name__ == "__main__":
    fix_vehicle_schema()
