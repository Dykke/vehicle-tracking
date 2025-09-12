#!/usr/bin/env python3
"""
Test script to verify database models and connection
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_models():
    """Test if database models can be imported and used"""
    try:
        print("🔍 Testing database models...")
        
        # Import Flask app and models
        from app import app
        from models import db
        from models.user import User
        from models.vehicle import Vehicle
        from models.location_log import LocationLog
        
        print("✅ All models imported successfully")
        
        with app.app_context():
            # Test database connection
            print("🔍 Testing database connection...")
            
            # Get database URL
            from db_config import get_database_url
            db_url = get_database_url()
            print(f"Database URL: {db_url}")
            
            # Test if we can query the database
            try:
                # Test users table
                user_count = User.query.count()
                print(f"✅ Users table accessible: {user_count} users found")
                
                # Test vehicles table
                vehicle_count = Vehicle.query.count()
                print(f"✅ Vehicles table accessible: {vehicle_count} vehicles found")
                
                # Test location_logs table
                log_count = LocationLog.query.count()
                print(f"✅ Location logs table accessible: {log_count} logs found")
                
                # Test creating a test vehicle
                print("🔍 Testing vehicle creation...")
                test_vehicle = Vehicle(
                    registration_number="TEST001",
                    vehicle_type="Test Vehicle",
                    capacity=4,
                    owner_id=1  # Assuming user ID 1 exists
                )
                
                db.session.add(test_vehicle)
                db.session.commit()
                print(f"✅ Test vehicle created with ID: {test_vehicle.id}")
                
                # Verify the vehicle was saved
                saved_vehicle = Vehicle.query.filter_by(registration_number="TEST001").first()
                if saved_vehicle:
                    print(f"✅ Vehicle saved successfully: {saved_vehicle.registration_number}")
                    
                    # Clean up test data
                    db.session.delete(saved_vehicle)
                    db.session.commit()
                    print("✅ Test vehicle cleaned up")
                else:
                    print("❌ Vehicle not found after creation")
                
                return True
                
            except Exception as e:
                print(f"❌ Database query failed: {e}")
                return False
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Models Test")
    print("=" * 50)
    
    if test_database_models():
        print("\n✅ All tests passed!")
        print("💡 Your database and models are working correctly!")
        print("💡 You should now be able to add drivers and save data!")
    else:
        print("\n❌ Tests failed!")
        print("💡 Check the error messages above for details")
