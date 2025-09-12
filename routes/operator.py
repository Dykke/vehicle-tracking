from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import User, DriverActionLog, OperatorActionLog
from models.vehicle import Vehicle
from models.location_log import LocationLog
from models import db
from datetime import datetime, timedelta
from sqlalchemy import text, desc
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
import time # Added for rate limiting retry logic

operator_bp = Blueprint('operator', __name__)

@operator_bp.route('/test-session')
@login_required
def test_session():
    """Test route to debug session state."""
    try:
        from flask import session as flask_session
        return jsonify({
            'success': True,
            'session_info': {
                'session_id': id(flask_session),
                'session_keys': list(flask_session.keys()),
                'user_id_in_session': flask_session.get('user_id', 'NOT_FOUND'),
                'current_user_id': current_user.id,
                'current_user_authenticated': current_user.is_authenticated,
                'current_user_type': current_user.user_type
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })

@operator_bp.route('/test-login-required')
@login_required
def test_login_required():
    """Test route to see if @login_required is working properly."""
    return jsonify({
        'success': True,
        'message': 'Login required decorator is working',
        'user_id': current_user.id,
        'user_type': current_user.user_type
    })

@operator_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    # Get vehicles with assigned driver information (only active, assigned vehicles)
    vehicles = Vehicle.query.filter(
        Vehicle.owner_id == current_user.id,
        Vehicle.assigned_driver_id.isnot(None),
        Vehicle.status == 'active'
    ).all()
    
    # Get active trip information for each vehicle
    from models.user import Trip
    for vehicle in vehicles:
        if vehicle.assigned_driver_id:
            # This will trigger the relationship to load if not already loaded
            _ = vehicle.assigned_driver
        
        # Check for active trip
        active_trip = Trip.query.filter_by(
            vehicle_id=vehicle.id,
            status='active'
        ).first()
        
        # Add trip status to vehicle object for template use
        vehicle.has_active_trip = active_trip is not None
        vehicle.active_trip = active_trip
    
    return render_template('operator/dashboard.html', vehicles=vehicles)

@operator_bp.route('/vehicle-controls')
@login_required
def vehicle_controls():
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        flash('Vehicle ID is required', 'error')
        return redirect(url_for('operator.dashboard'))
    
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        flash('Vehicle not found', 'error')
        return redirect(url_for('operator.dashboard'))
    
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        flash('You do not have permission to access this vehicle', 'error')
        return redirect(url_for('operator.dashboard'))
    
    return render_template('operator/vehicle_controls.html', vehicle=vehicle)

@operator_bp.route('/vehicles/debug')
@login_required
def debug_vehicles():
    """Debugging route to see all vehicles and their current locations."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
    return jsonify({
        'vehicles': [v.to_dict() for v in vehicles],
        'count': len(vehicles)
    })

@operator_bp.route('/vehicle/add', methods=['POST'])
@login_required
def add_vehicle():
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Handle both JSON and form data
    data = request.get_json() if request.is_json else request.form
    
    # Debug logging
    print(f"Request content type: {request.content_type}")
    print(f"Request data: {data}")
    print(f"Request JSON: {request.get_json()}")
    print(f"Request form: {request.form}")
    
    registration_number = data.get('vehicle_number')
    vehicle_type = data.get('vehicle_type')
    route = data.get('route')
    capacity = data.get('capacity')
    
    print(f"Extracted data - registration_number: {registration_number}, vehicle_type: {vehicle_type}, route: {route}, capacity: {capacity}")
    
    # Set default capacity if not provided
    if not capacity:
        default_capacities = {
            'bus': 50,
            'van': 15
        }
        capacity = default_capacities.get(vehicle_type.lower(), 10)
    else:
        try:
            capacity = int(capacity)
        except ValueError:
            capacity = 10
    
    if not all([registration_number, vehicle_type]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check for duplicates with a fresh query
    print(f"🔍 Checking for duplicate vehicle: {registration_number}")
    
    # Use a fresh query without clearing the session
    existing_vehicle = db.session.execute(
        db.select(Vehicle).where(Vehicle.registration_number == registration_number)
    ).scalar_one_or_none()
    
    if existing_vehicle:
        print(f"❌ Duplicate vehicle found: {existing_vehicle.registration_number}")
        return jsonify({'error': 'Vehicle number already exists'}), 400
    
    print(f"✅ No duplicate vehicle found, proceeding with creation")
    
    # Create route_info object if route follows "A to B" format
    route_info = None
    if route and ' to ' in route:
        route_parts = route.split(' to ')
        if len(route_parts) == 2:
            route_info = {
                "route_name": route,
                "origin": route_parts[0].strip(),
                "destination": route_parts[1].strip()
            }
    
    try:
        # Debug: Check session state before creating vehicle
        print(f"🔍 Session state before vehicle creation:")
        print(f"   - Session ID: {id(db.session)}")
        print(f"   - Session active: {db.session.is_active}")
        print(f"   - Current user ID: {current_user.id}")
        print(f"   - Current user authenticated: {current_user.is_authenticated}")
        
        # Create vehicle with all fields directly
        vehicle = Vehicle(
            owner_id=current_user.id,
            registration_number=registration_number,
            vehicle_type=vehicle_type,
            capacity=capacity,
            status='inactive',
            route=route
        )
        
        # Set route_info using the property to handle JSON serialization
        if route_info:
            vehicle.route_info_json = route_info
        
        print(f"Created vehicle object: {vehicle}")
        print(f"Vehicle owner_id: {vehicle.owner_id}")
        print(f"Vehicle registration_number: {vehicle.registration_number}")
        print(f"Vehicle route: {vehicle.route}")
        print(f"Vehicle route_info: {vehicle.route_info}")
        
        # Add the vehicle to the database
        db.session.add(vehicle)
        
        # CRITICAL FIX: Flush to check for any immediate database errors
        db.session.flush()
        print(f"✅ Vehicle flushed to session successfully")
        
        # Additional safety check: Verify no duplicate was created during this transaction
        print(f"🔍 Double-checking for duplicates before commit...")
        duplicate_check = db.session.execute(
            db.select(Vehicle).where(Vehicle.registration_number == registration_number)
        ).all()
        
        if len(duplicate_check) > 1:
            print(f"❌ Duplicate detected during transaction! Found {len(duplicate_check)} vehicles with same registration number")
            db.session.rollback()
            return jsonify({'error': 'Vehicle registration number already exists. Please use a different number.'}), 400
        
        print(f"✅ No duplicates detected, proceeding with commit")
        
        # Commit the transaction
        db.session.commit()
        print(f"✅ Vehicle committed to database successfully")
        
        # Verify the vehicle was actually saved
        db.session.refresh(vehicle)
        print(f"✅ Vehicle refreshed from database, ID: {vehicle.id}")
        
        # Debug: Check session state after vehicle creation
        print(f"🔍 Session state after vehicle creation:")
        print(f"   - Session ID: {id(db.session)}")
        print(f"   - Session active: {db.session.is_active}")
        print(f"   - Current user ID: {current_user.id}")
        print(f"   - Current user authenticated: {current_user.is_authenticated}")
        
        # CRITICAL: Check if current_user is still valid after commit
        try:
            # Try to access current_user properties to see if it's still valid
            test_user_id = current_user.id
            test_username = current_user.username
            print(f"✅ Current user still accessible after commit:")
            print(f"   - User ID: {test_user_id}")
            print(f"   - Username: {test_username}")
        except Exception as e:
                    print(f"❌ Current user became invalid after commit: {e}")
        print(f"❌ This explains the logout issue!")
        
        # Debug: Check Flask session state
        try:
            from flask import session as flask_session
            print(f"🔍 Flask session state after vehicle creation:")
            print(f"   - Flask session ID: {id(flask_session)}")
            print(f"   - Flask session keys: {list(flask_session.keys())}")
            print(f"   - User ID in Flask session: {flask_session.get('user_id', 'NOT_FOUND')}")
        except Exception as e:
            print(f"❌ Error checking Flask session state: {e}")
        
        print(f"Successfully added vehicle with route: {route}")
        
        # Debug: Check what to_dict() returns
        vehicle_dict = vehicle.to_dict()
        print(f"🔍 Vehicle.to_dict() result: {vehicle_dict}")
        print(f"🔍 Vehicle.to_dict() type: {type(vehicle_dict)}")
        
        # Add session debugging to response
        response_data = {
            'message': 'Vehicle added successfully',
            'vehicle': vehicle_dict,
            'debug': {
                'session_id': id(db.session),
                'user_id': current_user.id,
                'user_authenticated': current_user.is_authenticated,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        print(f"🔍 Sending vehicle response: {response_data}")
        
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        print(f"Error adding vehicle: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e}")
        
        # CRITICAL FIX: Always rollback on error
        db.session.rollback()
        print(f"✅ Session rolled back after error")
        
        # Check if it's a duplicate constraint error
        if 'UNIQUE constraint failed' in str(e) and 'vehicles.registration_number' in str(e):
            error_message = 'Vehicle registration number already exists. Please use a different number.'
            print(f"❌ Duplicate vehicle error detected: {error_message}")
        else:
            error_message = f'Database error: {str(e)}'
        
        error_response = jsonify({'error': error_message})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@operator_bp.route('/vehicle/<int:vehicle_id>/update', methods=['POST'])
@login_required
def update_vehicle_location(vehicle_id):
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Handle both JSON and form data
    data = request.get_json() if request.is_json else request.form
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    status = data.get('status')
    
    if status and not latitude and not longitude:
        # If only updating status
        vehicle.status = status
        vehicle.last_updated = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Status updated successfully',
            'status': vehicle.status,
            'last_updated': vehicle.last_updated.isoformat()
        })
    
    if not all([latitude, longitude]):
        return jsonify({'error': 'Missing location data'}), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        accuracy = float(accuracy) if accuracy else None
    except ValueError:
        return jsonify({'error': 'Invalid location format'}), 400
    
    vehicle.current_latitude = latitude
    vehicle.current_longitude = longitude
    if accuracy:
        vehicle.accuracy = accuracy
    if status:
        vehicle.status = status
    vehicle.last_updated = datetime.utcnow()
    
    location_log = LocationLog(
        vehicle_id=vehicle.id,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy
    )
    
    db.session.add(location_log)
    db.session.commit()
    
    return jsonify({
        'message': 'Location updated successfully',
        'location': {
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'status': vehicle.status,
            'last_updated': vehicle.last_updated.isoformat()
        }
    })

@operator_bp.route('/drivers/manage')
@login_required
def manage_drivers_page():
    """Manage drivers page."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    # Get drivers created by this operator
    drivers = User.query.filter_by(created_by_id=current_user.id, user_type='driver').all()
    
    return render_template('operator/manage_drivers.html', drivers=drivers)

@operator_bp.route('/drivers/add', methods=['POST'])
@login_required
def add_driver():
    """Add a new driver."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_active = data.get('is_active', True)
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields.'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists.'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400
    
    # Debug: Check session state before creating driver
    print(f"🔍 Session state before driver creation:")
    print(f"   - Session ID: {id(db.session)}")
    print(f"   - Session active: {db.session.is_active}")
    print(f"   - Current user ID: {current_user.id}")
    print(f"   - Current user authenticated: {current_user.is_authenticated}")
    
    # Create new driver
    driver = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        user_type='driver',
        is_active=is_active,
        created_by_id=current_user.id
    )
    
    db.session.add(driver)
    
    # Additional safety check: Verify no duplicate was created during this transaction
    print(f"🔍 Double-checking for duplicates before commit...")
    username_duplicate_check = db.session.execute(
        db.select(User).where(User.username == username)
    ).all()
    
    email_duplicate_check = db.session.execute(
        db.select(User).where(User.email == email)
    ).all()
    
    if len(username_duplicate_check) > 1:
        print(f"❌ Username duplicate detected during transaction!")
        db.session.rollback()
        return jsonify({'error': 'Username already exists. Please use a different username.'}), 400
    
    if len(email_duplicate_check) > 1:
        print(f"❌ Email duplicate detected during transaction!")
        db.session.rollback()
        return jsonify({'error': 'Email already exists. Please use a different email.'}), 400
    
    print(f"✅ No duplicates detected, proceeding with commit")
    
    # Create an action log for driver creation
    log = OperatorActionLog(
        operator_id=current_user.id,
        action='driver_created',
        target_type='driver',
        target_id=driver.id,
        meta_data={
            'timestamp': datetime.utcnow().isoformat(),
            'driver_username': username,
            'driver_email': email,
            'driver_is_active': is_active
        }
    )
    db.session.add(log)
    
    db.session.commit()
    
    # Debug: Check session state after driver creation
    print(f"🔍 Session state after driver creation:")
    print(f"   - Session ID: {id(db.session)}")
    print(f"   - Session active: {db.session.is_active}")
    print(f"   - Current user ID: {current_user.id}")
    print(f"   - Current user authenticated: {current_user.is_authenticated}")
    
    # CRITICAL: Check if current_user is still valid after commit
    try:
        # Try to access current_user properties to see if it's still valid
        test_user_id = current_user.id
        test_username = current_user.username
        print(f"✅ Current user still accessible after commit:")
        print(f"   - User ID: {test_user_id}")
        print(f"   - Username: {test_username}")
    except Exception as e:
        print(f"❌ Current user became invalid after commit: {e}")
        print(f"❌ This explains the logout issue!")
    
    # Add session debugging to response
    response_data = {
        'success': True,
        'message': 'Driver added successfully.',
        'driver': {
            'id': driver.id,
            'username': driver.username,
            'email': driver.email,
            'is_active': driver.is_active
        },
        'debug': {
            'session_id': id(db.session),
            'user_id': current_user.id,
            'user_authenticated': current_user.is_authenticated,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    print(f"🔍 Sending response: {response_data}")
    
    response = jsonify(response_data)
    response.headers['Content-Type'] = 'application/json'
    return response

@operator_bp.route('/drivers/<int:driver_id>', methods=['GET'])
@login_required
def get_driver(driver_id):
    """Get driver details."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if the driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You did not create this driver.'}), 403
    
    return jsonify({
        'success': True,
        'driver': {
            'id': driver.id,
            'username': driver.username,
            'email': driver.email,
            'is_active': driver.is_active,
            'created_at': driver.created_at.isoformat(),
            'profile_image_url': driver.profile_image_url
        }
    })

@operator_bp.route('/drivers/<int:driver_id>', methods=['PUT'])
@login_required
def update_driver(driver_id):
    """Update driver details."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if the driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You did not create this driver.'}), 403
    
    data = request.get_json()
    
    email = data.get('email')
    is_active = data.get('is_active')
    
    if email:
        # Check if email already exists for another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != driver_id:
            return jsonify({'error': 'Email already exists.'}), 400
        
        driver.email = email
    
    if is_active is not None:
        driver.is_active = is_active
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Driver updated successfully.',
        'driver': {
            'id': driver.id,
            'username': driver.username,
            'email': driver.email,
            'is_active': driver.is_active
        }
    })

@operator_bp.route('/drivers/<int:driver_id>/activate', methods=['POST'])
@login_required
def activate_driver(driver_id):
    """Activate a driver account."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if the driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You did not create this driver.'}), 403
    
    if driver.is_active:
        return jsonify({'error': 'Driver account is already active.'}), 400
    
    driver.is_active = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Driver {driver.username} activated successfully.'
    })

@operator_bp.route('/drivers/<int:driver_id>/deactivate', methods=['POST'])
@login_required
def deactivate_driver(driver_id):
    """Deactivate a driver account."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if the driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You did not create this driver.'}), 403
    
    if not driver.is_active:
        return jsonify({'error': 'Driver account is already inactive.'}), 400
    
    driver.is_active = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Driver {driver.username} deactivated successfully.'
    })

@operator_bp.route('/drivers/<int:driver_id>/reset-password', methods=['POST'])
@login_required
def reset_driver_password(driver_id):
    """Reset a driver's password."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if the driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You did not create this driver.'}), 403
    
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({'error': 'New password is required.'}), 400
    
    driver.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Password for {driver.username} reset successfully.'
    })

@operator_bp.route('/drivers/<int:driver_id>/details', methods=['GET'])
@login_required
def get_driver_details(driver_id):
    """Get detailed information about a driver."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if the driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You did not create this driver.'}), 403
    
    # Get vehicles assigned to this driver
    vehicles = Vehicle.query.filter_by(owner_id=driver.id).all()
    
    # Get recent activity logs
    recent_activity = DriverActionLog.query.filter_by(driver_id=driver.id).order_by(desc(DriverActionLog.created_at)).limit(5).all()
    
    return jsonify({
        'success': True,
        'driver': {
            'id': driver.id,
            'username': driver.username,
            'email': driver.email,
            'is_active': driver.is_active,
            'created_at': driver.created_at.isoformat(),
            'profile_image_url': driver.profile_image_url
        },
        'vehicles': [
            {
                'id': vehicle.id,
                'registration_number': vehicle.registration_number,
                'vehicle_type': vehicle.vehicle_type,
                'status': vehicle.status
            }
            for vehicle in vehicles
        ],
        'recent_activity': [
            {
                'id': log.id,
                'action': log.action,
                'created_at': log.created_at.isoformat(),
                'meta_data': log.meta_data
            }
            for log in recent_activity
        ]
    })

@operator_bp.route('/vehicle/<int:vehicle_id>/occupancy', methods=['POST'])
@login_required
def update_vehicle_occupancy(vehicle_id):
    """Update vehicle occupancy status."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to access this vehicle'}), 403
    
    data = request.get_json()
    occupancy_status = data.get('occupancy_status')
    
    if not occupancy_status or occupancy_status not in ['vacant', 'full']:
        return jsonify({'error': 'Invalid occupancy status. Must be "vacant" or "full".'}), 400
    
    try:
        vehicle.occupancy_status = occupancy_status
        vehicle.last_updated = datetime.utcnow()
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        try:
            from events_optimized import emit_vehicle_update
            emit_vehicle_update(vehicle_id, 'vehicle_updated', {
                'occupancy_status': occupancy_status,
                'last_updated': vehicle.last_updated.isoformat()
            })
        except ImportError:
            pass  # WebSocket events not available
        
        return jsonify({
            'success': True,
            'message': f'Vehicle occupancy status updated to {occupancy_status}',
            'occupancy_status': occupancy_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/vehicle/<int:vehicle_id>/trip/start', methods=['POST'])
@login_required
def start_vehicle_trip(vehicle_id):
    """Start a new trip for a vehicle."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to access this vehicle'}), 403
    
    data = request.get_json()
    route_name = data.get('route_name', 'No route')
    
    try:
        # Check if there's already an active trip
        from models.user import Trip
        active_trip = Trip.query.filter_by(
            vehicle_id=vehicle_id,
            status='active'
        ).first()
        
        if active_trip:
            return jsonify({'error': 'Vehicle already has an active trip'}), 400
        
        # Create new trip
        trip = Trip(
            vehicle_id=vehicle_id,
            driver_id=current_user.id,
            route_name=route_name,
            status='active',
            start_time=datetime.utcnow()
        )
        
        db.session.add(trip)
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        try:
            from events_optimized import emit_trip_update
            emit_trip_update(vehicle_id, 'started', {
                'trip_id': trip.id,
                'start_time': trip.start_time.isoformat(),
                'route_name': trip.route_name
            })
        except ImportError:
            pass  # WebSocket events not available
        
        return jsonify({
            'success': True,
            'message': 'Trip started successfully',
            'trip': {
                'id': trip.id,
                'start_time': trip.start_time.isoformat(),
                'route_name': trip.route_name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/vehicle/<int:vehicle_id>/trip/end', methods=['POST'])
@login_required
def end_vehicle_trip(vehicle_id):
    """End the active trip for a vehicle."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to access this vehicle'}), 403
    
    try:
        from models.user import Trip
        active_trip = Trip.query.filter_by(
            vehicle_id=vehicle_id,
            status='active'
        ).first()
        
        if not active_trip:
            return jsonify({'error': 'No active trip found for this vehicle'}), 400
        
        # End the trip
        active_trip.status = 'completed'
        active_trip.end_time = datetime.utcnow()
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        try:
            from events_optimized import emit_trip_update
            emit_trip_update(vehicle_id, 'ended', {
                'trip_id': active_trip.id,
                'end_time': active_trip.end_time.isoformat()
            })
        except ImportError:
            pass  # WebSocket events not available
        
        return jsonify({
            'success': True,
            'message': 'Trip ended successfully',
            'trip': {
                'id': active_trip.id,
                'end_time': active_trip.end_time.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/vehicle/<int:vehicle_id>/trip/current', methods=['GET'])
@login_required
def get_current_trip(vehicle_id):
    """Get the current active trip for a vehicle."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to access this vehicle'}), 403
    
    try:
        from models.user import Trip
        active_trip = Trip.query.filter_by(
            vehicle_id=vehicle_id,
            status='active'
        ).first()
        
        if not active_trip:
            return jsonify({'trip': None})
        
        # Get passenger summary
        from models.user import PassengerEvent
        passenger_events = PassengerEvent.query.filter_by(trip_id=active_trip.id).all()
        
        current_passengers = 0
        for event in passenger_events:
            if event.event_type == 'board':
                current_passengers += event.count
            elif event.event_type == 'alight':
                current_passengers -= event.count
        
        return jsonify({
            'trip': {
                'id': active_trip.id,
                'start_time': active_trip.start_time.isoformat(),
                'route_name': active_trip.route_name,
                'passenger_summary': {
                    'current_passengers': max(0, current_passengers)
                }
            }
        })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/vehicle/<int:vehicle_id>/passenger', methods=['POST'])
@login_required
def record_passenger_event(vehicle_id):
    """Record a passenger boarding or alighting event."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to access this vehicle'}), 403
    
    data = request.get_json()
    event_type = data.get('event_type')
    count = data.get('count')
    notes = data.get('notes', '')
    
    if not event_type or event_type not in ['board', 'alight']:
        return jsonify({'error': 'Invalid event type. Must be "board" or "alight".'}), 400
    
    if not count or not isinstance(count, int) or count < 1:
        return jsonify({'error': 'Invalid passenger count. Must be a positive integer.'}), 400
    
    try:
        from models.user import Trip, PassengerEvent
        
        # Get active trip
        active_trip = Trip.query.filter_by(
            vehicle_id=vehicle_id,
            status='active'
        ).first()
        
        if not active_trip:
            return jsonify({'error': 'No active trip found for this vehicle'}), 400
        
        # Create passenger event
        passenger_event = PassengerEvent(
            trip_id=active_trip.id,
            event_type=event_type,
            count=count,
            notes=notes,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(passenger_event)
        db.session.commit()
        
        # Emit WebSocket event for real-time updates
        try:
            from events_optimized import emit_passenger_event
            emit_passenger_event(vehicle_id, event_type, {
                'event_id': passenger_event.id,
                'count': count,
                'notes': notes,
                'timestamp': passenger_event.timestamp.isoformat()
            })
        except ImportError:
            pass  # WebSocket events not available
        
        return jsonify({
            'success': True,
            'message': f'Passenger {event_type} event recorded successfully',
            'event': {
                'id': passenger_event.id,
                'event_type': event_type,
                'count': count,
                'timestamp': passenger_event.timestamp.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/settings')
@login_required
def settings():
    """Operator settings page."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    return render_template('operator/settings.html')

@operator_bp.route('/profile')
@login_required
def profile():
    """Operator profile page."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get operator's vehicles with explicit session handling
        vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
        
        # Debug: Check if routes are preserved
        for vehicle in vehicles:
            print(f"🔍 DEBUG: Vehicle {vehicle.id} - Route: {vehicle.route}, Route Info: {vehicle.route_info}")
        
        # Get recent action logs for this operator
        recent_logs = OperatorActionLog.query.filter_by(operator_id=current_user.id).order_by(OperatorActionLog.created_at.desc()).limit(10).all()
        
        # Ensure session is active and commit any pending changes
        if db.session.is_active:
            db.session.commit()
        
        return render_template('operator/profile.html', vehicles=vehicles, recent_logs=recent_logs)
        
    except Exception as e:
        print(f"❌ Error in operator profile route: {e}")
        # Rollback and try to recover
        try:
            db.session.rollback()
        except:
            pass
        
        # Return a basic response without vehicles if there's an error
        return render_template('operator/profile.html', vehicles=[], recent_logs=[])

@operator_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update operator profile information."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    data = request.get_json()
    email = data.get('email')
    company_name = data.get('company_name', '')
    contact_number = data.get('contact_number', '')
    
    if not email:
        return jsonify({'error': 'Email is required.'}), 400
    
    # Check if email already exists for another user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != current_user.id:
        return jsonify({'error': 'Email already exists.'}), 400
    
    # Update profile
    current_user.email = email
    current_user.company_name = company_name
    current_user.contact_number = contact_number
    
    # Create an action log
    log = OperatorActionLog(
        operator_id=current_user.id,
        action='profile_updated',
        target_type='system',
        target_id=None,
        meta_data={
            'timestamp': datetime.utcnow().isoformat(),
            'old_email': getattr(current_user, 'email', None),
            'new_email': email,
            'company_name': company_name,
            'contact_number': contact_number
        }
    )
    
    # Save changes to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    })

@operator_bp.route('/password', methods=['POST'])
@login_required
def change_password():
    """Change operator password."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'error': 'All password fields are required.'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'New password and confirmation do not match.'}), 400
    
    # Verify current password
    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'error': 'Current password is incorrect.'}), 400
    
    # Check password strength
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters long.'}), 400
    
    # Update password
    current_user.password_hash = generate_password_hash(new_password)
    
    # Create an action log
    log = OperatorActionLog(
        operator_id=current_user.id,
        action='password_changed',
        target_type='system',
        target_id=None,
        meta_data={
            'timestamp': datetime.utcnow().isoformat(),
            'password_changed': True
        }
    )
    
    # Save changes to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    })

@operator_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update operator settings."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    data = request.get_json()
    
    # Update notification settings
    notification_settings = data.get('notifications', {})
    if hasattr(current_user, 'notification_settings'):
        current_user.notification_settings = notification_settings
    
    # Update privacy settings
    privacy_settings = data.get('privacy', {})
    if hasattr(current_user, 'privacy_settings'):
        current_user.privacy_settings = privacy_settings
    
    # Update system settings
    system_settings = data.get('system', {})
    if hasattr(current_user, 'system_settings'):
        current_user.system_settings = system_settings
    
    # Create an action log
    log = OperatorActionLog(
        operator_id=current_user.id,
        action='settings_updated',
        target_type='system',
        target_id=None,
        meta_data={
            'timestamp': datetime.utcnow().isoformat(),
            'notification_settings': notification_settings,
            'privacy_settings': privacy_settings,
            'system_settings': system_settings
        }
    )
    
    # Save changes to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Settings updated successfully'
    })

@operator_bp.route('/vehicle/<int:vehicle_id>/assign', methods=['POST'])
@login_required
def assign_vehicle_to_driver(vehicle_id):
    """Assign a vehicle to a driver."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to assign this vehicle'}), 403
    
    data = request.get_json()
    driver_id = data.get('driver_id')
    
    if not driver_id:
        return jsonify({'error': 'Driver ID is required.'}), 400
    
    # Check if driver exists and is a driver
    driver = User.query.get(driver_id)
    if not driver or driver.user_type != 'driver':
        return jsonify({'error': 'Invalid driver ID or user is not a driver.'}), 400
    
    # Check if driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You can only assign vehicles to drivers you created.'}), 403
    
    try:
        # Check if vehicle is already assigned to another driver
        if vehicle.assigned_driver_id and vehicle.assigned_driver_id != driver_id:
            return jsonify({'error': 'Vehicle is already assigned to another driver.'}), 400
        
        # CRITICAL FIX: Preserve existing route information before assignment
        existing_route = vehicle.route
        existing_route_info = vehicle.route_info
        
        # Assign vehicle to driver
        vehicle.assigned_driver_id = driver_id
        vehicle.status = 'active'  # Activate the vehicle when assigned
        
        # Ensure route information is preserved
        if existing_route:
            vehicle.route = existing_route
        if existing_route_info:
            vehicle.route_info = existing_route_info
        
        db.session.commit()
        
        # Create an action log for the driver
        driver_log = DriverActionLog(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            action='vehicle_assigned',
            meta_data={
                'assigned_by': current_user.id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        db.session.add(driver_log)
        
        # Create an action log for the operator
        operator_log = OperatorActionLog(
            operator_id=current_user.id,
            action='vehicle_assigned_to_driver',
            target_type='vehicle',
            target_id=vehicle_id,
            meta_data={
                'timestamp': datetime.utcnow().isoformat(),
                'driver_id': driver_id,
                'driver_username': driver.username,
                'vehicle_registration': vehicle.registration_number
            }
        )
        db.session.add(operator_log)
        
        db.session.commit()
        
        # Emit WebSocket notification for real-time updates
        try:
            from events_optimized import emit_vehicle_assignment_change
            emit_vehicle_assignment_change(vehicle_id, driver_id, 'assigned')
        except ImportError:
            pass  # WebSocket events not available
        
        return jsonify({
            'success': True,
            'message': f'Vehicle {vehicle.registration_number} assigned to driver {driver.username} successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/vehicle/<int:vehicle_id>/unassign', methods=['POST'])
@login_required
def unassign_vehicle_from_driver(vehicle_id):
    """Unassign a vehicle from a driver."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You do not have permission to unassign this vehicle'}), 403
    
    if not vehicle.assigned_driver_id:
        return jsonify({'error': 'Vehicle is not assigned to any driver.'}), 400
    
    try:
        # Get driver info for logging
        driver = User.query.get(vehicle.assigned_driver_id)
        driver_username = driver.username if driver else 'Unknown'
        
        # CRITICAL FIX: Preserve existing route information before unassignment
        existing_route = vehicle.route
        existing_route_info = vehicle.route_info
        
        # Unassign vehicle
        vehicle.assigned_driver_id = None
        vehicle.status = 'inactive'  # Deactivate the vehicle when unassigned
        
        # Ensure route information is preserved
        if existing_route:
            vehicle.route = existing_route
        if existing_route_info:
            vehicle.route_info = existing_route_info
        
        db.session.commit()
        
        # Create an action log for the driver (if we have the driver ID)
        if vehicle.assigned_driver_id:
            driver_log = DriverActionLog(
                driver_id=vehicle.assigned_driver_id,
                vehicle_id=vehicle_id,
                action='vehicle_unassigned',
                meta_data={
                    'unassigned_by': current_user.id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(driver_log)
        
        # Create an action log for the operator
        operator_log = OperatorActionLog(
            operator_id=current_user.id,
            action='vehicle_unassigned_from_driver',
            target_type='vehicle',
            target_id=vehicle_id,
            meta_data={
                'timestamp': datetime.utcnow().isoformat(),
                'previous_driver_id': vehicle.assigned_driver_id,
                'previous_driver_username': driver_username,
                'vehicle_registration': vehicle.registration_number
            }
        )
        db.session.add(operator_log)
        
        db.session.commit()
        
        # Emit WebSocket notification for real-time updates
        try:
            from events_optimized import emit_vehicle_assignment_change
            emit_vehicle_assignment_change(vehicle_id, None, 'unassigned')
        except ImportError:
            pass  # WebSocket events not available
        
        return jsonify({
            'success': True,
            'message': f'Vehicle {vehicle.registration_number} unassigned from driver {driver_username} successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@operator_bp.route('/vehicles/unassigned', methods=['GET'])
@login_required
def get_unassigned_vehicles():
    """Get all unassigned vehicles for the operator."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicles = Vehicle.query.filter_by(
        owner_id=current_user.id,
        assigned_driver_id=None
    ).all()
    
    return jsonify({
        'success': True,
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    })

@operator_bp.route('/drivers/<int:driver_id>/vehicles', methods=['GET'])
@login_required
def get_driver_vehicles(driver_id):
    """Get all vehicles assigned to a specific driver."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    driver = User.query.get_or_404(driver_id)
    if driver.user_type != 'driver':
        return jsonify({'error': 'User is not a driver.'}), 400
    
    # Check if driver was created by this operator
    if driver.created_by_id != current_user.id and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. You can only view vehicles for drivers you created.'}), 403
    
    vehicles = Vehicle.query.filter_by(assigned_driver_id=driver_id).all()
    
    return jsonify({
        'success': True,
        'driver': {
            'id': driver.id,
            'username': driver.username,
            'email': driver.email
        },
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    })

@operator_bp.route('/vehicles/manage')
@login_required
def manage_vehicles():
    """Vehicle management page for operators."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    # Get all vehicles owned by this operator
    vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
    
    # Get all drivers created by this operator
    drivers = User.query.filter_by(
        user_type='driver',
        created_by_id=current_user.id
    ).all()
    
    return render_template('operator/manage_vehicle.html', vehicles=vehicles, drivers=drivers)

@operator_bp.route('/drivers')
@login_required
def get_drivers():
    """Get all drivers created by this operator."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    drivers = User.query.filter_by(
        user_type='driver',
        created_by_id=current_user.id
    ).all()
    
    return jsonify({
        'success': True,
        'drivers': [
            {
                'id': driver.id,
                'username': driver.username,
                'email': driver.email,
                'is_active': driver.is_active
            }
            for driver in drivers
        ]
    })

@operator_bp.route('/vehicles')
@login_required
def get_vehicles():
    """Get all vehicles owned by this operator."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied. Operator account required.'}), 403
    
    vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
    
    return jsonify({
        'success': True,
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    })

@operator_bp.route('/account/export', methods=['GET'])
@login_required
def export_operator_account():
    """Export operator account data as JSON download."""
    if current_user.user_type not in ['operator', 'admin']:
        return jsonify({'error': 'Access denied. Operator account required.'}), 403

    # Collect basic operator data and owned resources summary
    vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
    drivers = User.query.filter_by(created_by_id=current_user.id, user_type='driver').all()

    export_data = {
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'user_type': current_user.user_type,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'is_active': current_user.is_active,
        },
        'vehicles': [v.to_dict() for v in vehicles],
        'drivers': [
            {
                'id': d.id,
                'username': d.username,
                'email': d.email,
                'is_active': d.is_active
            } for d in drivers
        ]
    }

    response = jsonify(export_data)
    response.headers['Content-Disposition'] = 'attachment; filename=operator_account_export.json'
    return response

# Delete a vehicle (only if owned by operator and not assigned)
@operator_bp.route('/vehicle/<int:vehicle_id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_vehicle(vehicle_id):
    """Delete a vehicle owned by the current operator.
    Only allowed when the vehicle is not assigned to a driver.
    """
    if current_user.user_type not in ['operator', 'admin']:
        return jsonify({'error': 'Access denied. Operator account required.'}), 403

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # Operators can only delete their own vehicles unless admin
    if current_user.user_type != 'admin' and vehicle.owner_id != current_user.id:
        return jsonify({'error': 'Access denied. You can only delete your own vehicles.'}), 403

    # Prevent deleting when assigned to a driver
    if vehicle.assigned_driver_id is not None:
        return jsonify({'error': 'Cannot delete a vehicle that is currently assigned to a driver.'}), 400

    try:
        # First, delete all related records in the correct order
        
        # 1. Delete passenger events (they reference trips)
        from models.user import PassengerEvent, Trip
        trips = Trip.query.filter_by(vehicle_id=vehicle_id).all()
        for trip in trips:
            PassengerEvent.query.filter_by(trip_id=trip.id).delete()
        
        # 2. Delete trips (they reference vehicles)
        Trip.query.filter_by(vehicle_id=vehicle_id).delete()
        
        # 3. Delete driver action logs (they reference vehicles)
        from models.user import DriverActionLog
        DriverActionLog.query.filter_by(vehicle_id=vehicle_id).delete()
        
        # 4. Delete location logs (they reference vehicles)
        from models.location_log import LocationLog
        LocationLog.query.filter_by(vehicle_id=vehicle_id).delete()
        
        # 5. Finally, delete the vehicle
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vehicle deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete vehicle: {str(e)}'}), 500

@operator_bp.route('/database/health', methods=['GET'])
@login_required
def database_health_check():
    """Database health check endpoint for debugging."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Get vehicle count
        vehicle_count = db.session.execute(db.select(db.func.count(Vehicle.id))).scalar()
        
        # Get user count
        user_count = db.session.execute(db.select(db.func.count(User.id))).scalar()
        
        # Check for any vehicles with the same registration number
        duplicate_check = db.session.execute(db.text("""
            SELECT registration_number, COUNT(*) as count 
            FROM vehicles 
            GROUP BY registration_number 
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        # Get recent vehicles
        recent_vehicles = db.session.execute(
            db.select(Vehicle.id, Vehicle.registration_number, Vehicle.vehicle_type, Vehicle.created_at)
            .order_by(Vehicle.created_at.desc())
            .limit(5)
        ).fetchall()
        
        health_data = {
            'status': 'healthy',
            'database_connected': True,
            'vehicle_count': vehicle_count,
            'user_count': user_count,
            'duplicate_registration_numbers': [row[0] for row in duplicate_check],
            'recent_vehicles': [
                {
                    'id': v[0],
                    'registration_number': v[1],
                    'vehicle_type': v[2],
                    'created_at': v[3].isoformat() if v[3] else None
                }
                for v in recent_vehicles
            ],
            'session_info': {
                'session_id': id(db.session),
                'is_active': db.session.is_active,
                'is_modified': db.session.is_modified(db.session.new),
                'dirty_objects': len(db.session.dirty),
                'new_objects': len(db.session.new),
                'deleted_objects': len(db.session.deleted)
            }
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@operator_bp.route('/debug/session', methods=['GET'])
@login_required
def debug_session():
    """Debug session and authentication state."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from flask import session as flask_session
        
        session_info = {
            'user_id': current_user.id if current_user.is_authenticated else None,
            'username': current_user.username if current_user.is_authenticated else None,
            'user_type': current_user.user_type if current_user.is_authenticated else None,
            'is_authenticated': current_user.is_authenticated,
            'flask_session_id': id(flask_session),
            'flask_session_keys': list(flask_session.keys()),
            'db_session_id': id(db.session),
            'db_session_active': db.session.is_active,
            'db_session_modified': db.session.is_modified(),
            'dirty_objects': len(db.session.dirty),
            'new_objects': len(db.session.new),
            'deleted_objects': len(db.session.deleted)
        }
        
        return jsonify(session_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@operator_bp.route('/debug/test-session', methods=['GET'])
@login_required
def test_session_persistence():
    """Test if session persists without database operations."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from flask import session as flask_session
        
        # Get initial state
        initial_state = {
            'user_id': current_user.id,
            'username': current_user.username,
            'user_type': current_user.user_type,
            'is_authenticated': current_user.is_authenticated,
            'flask_session_id': id(flask_session),
            'db_session_id': id(db.session)
        }
        
        # Simulate a simple database query (read-only)
        test_user = User.query.get(current_user.id)
        
        # Get state after query
        after_query_state = {
            'user_id': current_user.id,
            'username': current_user.username,
            'user_type': current_user.user_type,
            'is_authenticated': current_user.is_authenticated,
            'flask_session_id': id(flask_session),
            'db_session_id': id(db.session),
            'test_user_found': test_user is not None
        }
        
        return jsonify({
            'initial_state': initial_state,
            'after_query_state': after_query_state,
            'session_persisted': initial_state['flask_session_id'] == after_query_state['flask_session_id'],
            'user_persisted': initial_state['user_id'] == after_query_state['user_id']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@operator_bp.route('/debug/test-commit', methods=['GET'])
@login_required
def test_commit_persistence():
    """Test if session persists after a commit operation."""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from flask import session as flask_session
        
        # Get initial state
        initial_state = {
            'user_id': current_user.id,
            'username': current_user.username,
            'user_type': current_user.user_type,
            'is_authenticated': current_user.is_authenticated,
            'flask_session_id': id(flask_session),
            'db_session_id': id(db.session)
        }
        
        # Create a test log entry (this will be committed)
        test_log = DriverActionLog(
            driver_id=current_user.id,
            vehicle_id=None,
            action='test_commit',
            meta_data={'test': True, 'timestamp': datetime.utcnow().isoformat()}
        )
        
        db.session.add(test_log)
        db.session.commit()
        
        # Get state after commit
        after_commit_state = {
            'user_id': current_user.id,
            'username': current_user.username,
            'user_type': current_user.user_type,
            'is_authenticated': current_user.is_authenticated,
            'flask_session_id': id(flask_session),
            'db_session_id': id(db.session),
            'test_log_created': test_log.id is not None
        }
        
        # Clean up - remove the test log
        db.session.delete(test_log)
        db.session.commit()
        
        return jsonify({
            'initial_state': initial_state,
            'after_commit_state': after_commit_state,
            'session_persisted': initial_state['flask_session_id'] == after_commit_state['flask_session_id'],
            'user_persisted': initial_state['user_id'] == after_commit_state['user_id'],
            'db_session_persisted': initial_state['db_session_id'] == after_commit_state['db_session_id']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@operator_bp.route('/test', methods=['GET'])
@login_required
def test_route():
    """Test route to verify blueprint is working"""
    return jsonify({'message': 'Operator blueprint is working!', 'user': current_user.username})

@operator_bp.route('/geocode')
def geocode():
    """Geocoding proxy to handle both forward and reverse geocoding."""
    try:
        # Get query parameters
        query = request.args.get('q', '')
        lat = request.args.get('lat', '')
        lon = request.args.get('lon', '')
        
        # Determine if this is forward or reverse geocoding
        if query:
            # Forward geocoding (address to coordinates)
            print(f"🔍 Forward geocoding request: {query}")
            
            # Build Nominatim URL for forward geocoding
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 5,
                'addressdetails': 1,
                'extratags': 1,
                'namedetails': 1,
                'accept-language': 'en'
            }
            
        elif lat and lon:
            # Reverse geocoding (coordinates to address)
            print(f"🔍 Reverse geocoding: lat={lat}, lon={lon}")
            
            # Build Nominatim URL for reverse geocoding
            nominatim_url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'format': 'json',
                'lat': lat,
                'lon': lon,
                'addressdetails': 1,
                'extratags': 1,
                'namedetails': 1,
                'accept-language': 'en',
                'zoom': 18
            }
            
        else:
            return jsonify({'error': 'Missing required parameters. Use "q" for forward geocoding or "lat" and "lon" for reverse geocoding.'}), 400
        
        # Add required headers for Nominatim API
        headers = {
            'User-Agent': 'DriveMonitoringSystem/1.0 (https://github.com/your-repo; your-email@example.com)',
            'Accept': 'application/json',
            'Accept-Language': 'en'
        }
        
        print(f"🔍 Making request to Nominatim: {nominatim_url} with params: {params}")
        
        # Make request to Nominatim with timeout and retry logic
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    nominatim_url, 
                    params=params, 
                    headers=headers, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle single result from reverse geocoding
                    if lat and lon and not isinstance(data, list):
                        data = [data]
                    
                    print(f"✅ Geocoding successful: {len(data) if isinstance(data, list) else 1} results")
                    return jsonify(data)
                    
                elif response.status_code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limited, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print("❌ Rate limit exceeded after all retries")
                        return jsonify({'error': 'Geocoding service temporarily unavailable due to rate limiting. Please try again later.'}), 429
                        
                elif response.status_code == 403:  # Forbidden
                    print(f"❌ Access forbidden by Nominatim: {response.status_code}")
                    return jsonify({'error': 'Geocoding service access denied. Please try again later.'}), 503
                    
                else:
                    print(f"❌ Nominatim error: {response.status_code} - {response.text}")
                    return jsonify({'error': f'Geocoding service error: {response.status_code}'}), 503
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ Timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("❌ Timeout after all retries")
                    return jsonify({'error': 'Geocoding service timeout. Please try again.'}), 503
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}")
                return jsonify({'error': f'Geocoding service error: {str(e)}'}), 503
                
    except Exception as e:
        print(f"❌ Geocoding request error: {e}")
        return jsonify({'error': f'Internal geocoding error: {str(e)}'}), 500

@operator_bp.route('/vehicle/route/set', methods=['POST'])
@login_required
def set_vehicle_route():
    """Set or update the route for a specific vehicle"""
    try:
        if current_user.user_type != 'operator' and current_user.user_type != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get route data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        vehicle_id = data.get('vehicle_id')
        origin = data.get('origin')
        destination = data.get('destination')
        origin_lat = data.get('origin_lat')
        origin_lon = data.get('origin_lon')
        dest_lat = data.get('dest_lat')
        dest_lon = data.get('dest_lon')
        
        # Validate required fields
        if not all([vehicle_id, origin, destination]):
            return jsonify({'error': 'Missing required fields: vehicle_id, origin, destination'}), 400
        
        # Find the vehicle
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Check if user has permission to modify this vehicle
        if vehicle.owner_id != current_user.id and current_user.user_type != 'admin':
            return jsonify({'error': 'Access denied to this vehicle'}), 403
        
        # Update vehicle route information
        vehicle.route = f"{origin} → {destination}"
        
        # Try to geocode if coordinates were not provided
        def geocode_place(name: str):
            try:
                import requests
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": name, "format": "json", "limit": 1},
                    headers={"User-Agent": "drive-monitoring/1.0"},
                    timeout=5
                )
                data = resp.json()
                if isinstance(data, list) and data:
                    return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"]) }
            except Exception:
                return None
            return None

        origin_coords_val = { 'lat': origin_lat, 'lon': origin_lon } if origin_lat and origin_lon else None
        dest_coords_val = { 'lat': dest_lat, 'lon': dest_lon } if dest_lat and dest_lon else None
        
        if not origin_coords_val:
            origin_coords_val = geocode_place(origin)
        if not dest_coords_val:
            dest_coords_val = geocode_place(destination)

        # Store additional route details in route_info field
        route_details = {
            'origin': origin,
            'destination': destination,
            'origin_coords': origin_coords_val,
            'dest_coords': dest_coords_val,
            'route_set_at': datetime.utcnow().isoformat(),
            'route_set_by': current_user.id
        }
        
        # Store route details as JSON string in route_info field
        vehicle.route_info = json.dumps(route_details)
        
        # Save to database
        db.session.commit()
        
        print(f"✅ Route updated for vehicle {vehicle_id}: {origin} → {destination}")
        
        # Debug: Check if current_user is still valid after commit
        try:
            test_user_id = current_user.id
            test_username = current_user.username
            print(f"✅ Current user still accessible after route commit:")
            print(f"   - User ID: {test_user_id}")
            print(f"   - Username: {test_username}")
        except Exception as e:
            print(f"❌ Current user became invalid after route commit: {e}")
            print(f"❌ This explains the logout issue!")
        
        # Debug: Check session state
        try:
            from flask import session as flask_session
            print(f"🔍 Session state after route commit:")
            print(f"   - Flask session ID: {id(flask_session)}")
            print(f"   - DB session ID: {id(db.session)}")
            print(f"   - DB session active: {db.session.is_active}")
        except Exception as e:
            print(f"❌ Error checking session state: {e}")
        
        # Ensure we're returning proper JSON response
        response_data = {
            'message': 'Route updated successfully',
            'vehicle_id': vehicle_id,
            'route': vehicle.route,
            'route_info': vehicle.route_info
        }
        
        print(f"🔍 Sending route response: {response_data}")
        
        # Set explicit content type to ensure JSON response
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    except Exception as e:
        print(f"❌ Error setting vehicle route: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Error details: {e}")
        
        # Always rollback on error
        try:
            db.session.rollback()
            print(f"✅ Session rolled back after error")
        except Exception as rollback_error:
            print(f"❌ Error during rollback: {rollback_error}")
        
        # Ensure error response is also proper JSON
        error_response = jsonify({'error': f'Failed to update route: {str(e)}'})
        error_response.headers['Content-Type'] = 'application/json'
        return error_response, 500

@operator_bp.route('/logs/actions')
@login_required
def operator_action_logs():
    """Operator action logs page - shows logs for their drivers and vehicles"""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        flash('Access denied. Operator account required.', 'error')
        return redirect(url_for('index'))
    
    # Get drivers and vehicles for this operator
    drivers = User.query.filter_by(created_by_id=current_user.id, user_type='driver').all()
    vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
    
    return render_template(
        'operator/action_logs.html',
        drivers=drivers,
        vehicles=vehicles
    )

@operator_bp.route('/logs/actions/data')
@login_required
def operator_action_logs_data():
    """API endpoint for operator action logs data"""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Get filter parameters
    driver_id = request.args.get('driver_id')
    vehicle_id = request.args.get('vehicle_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_types = request.args.get('action_types', 'all')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Start with base query - only show logs for operator's drivers and vehicles
    query = db.session.query(
        DriverActionLog,
        User.username.label('driver_username'),
        User.profile_image_url.label('driver_profile_image_url'),
        Vehicle.registration_number.label('vehicle_registration')
    ).join(
        User, DriverActionLog.driver_id == User.id
    ).outerjoin(
        Vehicle, DriverActionLog.vehicle_id == Vehicle.id
    ).filter(
        # Only show logs for drivers created by this operator
        User.created_by_id == current_user.id
    )
    
    # Apply additional filters
    if driver_id:
        query = query.filter(DriverActionLog.driver_id == driver_id)
    
    if vehicle_id:
        query = query.filter(DriverActionLog.vehicle_id == vehicle_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(DriverActionLog.created_at >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(DriverActionLog.created_at < end_date_obj)
    
    if action_types and action_types != 'all':
        action_list = action_types.split(',')
        query = query.filter(DriverActionLog.action.in_(action_list))
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination
    query = query.order_by(desc(DriverActionLog.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    results = query.all()
    
    # Format results
    logs = []
    for result in results:
        log = result[0]
        log_dict = {
            'id': log.id,
            'driver_id': log.driver_id,
            'driver_username': result.driver_username,
            'driver_profile_image_url': result.driver_profile_image_url,
            'vehicle_id': log.vehicle_id,
            'vehicle_registration': result.vehicle_registration,
            'action': log.action,
            'meta_data': log.meta_data,
            'created_at': log.created_at.isoformat() + 'Z'
        }
        logs.append(log_dict)
    
    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': total_pages
    }
    
    return jsonify({
        'success': True,
        'logs': logs,
        'pagination': pagination
    })

@operator_bp.route('/logs/actions/export')
@login_required
def operator_export_action_logs():
    """Export operator action logs as CSV"""
    if current_user.user_type != 'operator' and current_user.user_type != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Get filter parameters
    driver_id = request.args.get('driver_id')
    vehicle_id = request.args.get('vehicle_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_types = request.args.get('action_types', 'all')
    
    # Start with base query - only show logs for operator's drivers
    query = db.session.query(
        DriverActionLog,
        User.username.label('driver_username'),
        Vehicle.registration_number.label('vehicle_registration')
    ).join(
        User, DriverActionLog.driver_id == User.id
    ).outerjoin(
        Vehicle, DriverActionLog.vehicle_id == Vehicle.id
    ).filter(
        # Only show logs for drivers created by this operator
        User.created_by_id == current_user.id
    )
    
    # Apply filters
    if driver_id:
        query = query.filter(DriverActionLog.driver_id == driver_id)
    
    if vehicle_id:
        query = query.filter(DriverActionLog.vehicle_id == vehicle_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(DriverActionLog.created_at >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(DriverActionLog.created_at < end_date_obj)
    
    if action_types and action_types != 'all':
        action_list = action_types.split(',')
        query = query.filter(DriverActionLog.action.in_(action_list))
    
    # Execute query
    results = query.order_by(desc(DriverActionLog.created_at)).all()
    
    # Create CSV in memory
    import io
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Date', 'Time', 'Driver', 'Vehicle', 'Action', 'Details'
    ])
    
    # Write data
    for result in results:
        log = result[0]
        date = log.created_at.strftime('%Y-%m-%d')
        time = log.created_at.strftime('%H:%M:%S')
        
        # Format metadata
        meta_data_str = ''
        if log.meta_data:
            try:
                meta_data = json.loads(log.meta_data) if isinstance(log.meta_data, str) else log.meta_data
                
                if log.action == 'occupancy_change':
                    meta_data_str = f"Changed from {meta_data.get('old_value', 'N/A')} to {meta_data.get('new_value', 'N/A')}"
                elif log.action in ['route_start', 'route_abort']:
                    meta_data_str = f"Route: {meta_data.get('route', 'N/A')}"
                elif log.action == 'vehicle_assigned':
                    assigned_by = meta_data.get('assigned_by', 'Unknown')
                    timestamp = meta_data.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    meta_data_str = f"Assigned by: Operator ID {assigned_by}, Time: {timestamp}"
                elif log.action in ['passenger_board', 'passenger_alight']:
                    passenger_count = meta_data.get('passenger_count', meta_data.get('count', 'N/A'))
                    location = meta_data.get('location', 'N/A')
                    meta_data_str = f"Passengers: {passenger_count}, Location: {location}"
                else:
                    # For other actions, format in a user-friendly way
                    details = []
                    for key, value in meta_data.items():
                        if key != 'timestamp':
                            formatted_key = key.replace('_', ' ').title()
                            formatted_value = value
                            
                            # Format timestamp if present
                            if key == 'timestamp' or (isinstance(value, str) and 'T' in value):
                                try:
                                    formatted_value = datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    pass
                            
                            details.append(f"{formatted_key}: {formatted_value}")
                    
                    meta_data_str = '; '.join(details) if details else str(meta_data)
            except:
                meta_data_str = str(log.meta_data)
        
        writer.writerow([
            log.id,
            date,
            time,
            result.driver_username,
            result.vehicle_registration or 'N/A',
            log.action,
            meta_data_str
        ])
    
    # Prepare response
    output.seek(0)
    from flask import Response
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=operator_action_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )