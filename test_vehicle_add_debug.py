import requests
import json

def test_vehicle_add():
    """Test the vehicle add endpoint to see the exact error"""
    
    # Test data
    test_vehicle = {
        "vehicle_number": "TEST001",
        "vehicle_type": "van",
        "route": "Test Route",
        "capacity": 15
    }
    
    print("🧪 TESTING VEHICLE ADD ENDPOINT")
    print("=" * 50)
    print(f"📤 Sending data: {json.dumps(test_vehicle, indent=2)}")
    
    try:
        # First, try to add the vehicle
        response = requests.post(
            'http://192.168.1.9:5000/operator/vehicle/add',
            json=test_vehicle,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📥 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📥 Response Text: {response.text}")
        
        # Now try to add the same vehicle again to see if we get the duplicate error
        print(f"\n🔄 Testing duplicate submission...")
        response2 = requests.post(
            'http://192.168.1.9:5000/operator/vehicle/add',
            json=test_vehicle,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 Duplicate Response Status: {response2.status_code}")
        try:
            response_data2 = response2.json()
            print(f"📥 Duplicate Response Data: {json.dumps(response_data2, indent=2)}")
        except:
            print(f"📥 Duplicate Response Text: {response2.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_vehicle_add()
