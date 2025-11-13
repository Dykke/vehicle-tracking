from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, make_response
from flask_login import login_required, current_user
from models.user import User, DriverActionLog, Trip, PassengerEvent
from models.vehicle import Vehicle
from models import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import json

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/dashboard')
@driver_bp.route('/dashboard/<int:cache_buster>')
@login_required
def dashboard(cache_buster=None):
    """Driver dashboard page."""
    print("🚨 ROUTE CALLED: /driver/dashboard - Starting function execution")
    
    if current_user.user_type != 'driver':
        print("❌ ROUTE ERROR: User is not a driver")
        flash('Access denied. Driver account required.', 'error')
        return redirect(url_for('index'))
    
    print(f"✅ ROUTE SUCCESS: User {current_user.id} is a driver")
    
    # Reload user object from database to get latest profile_image_url
    # Flask-Login might cache the user object, so we need to refresh it
    user_id = current_user.id
    db.session.expire(current_user)  # Expire the current session object
    fresh_user = User.query.get(user_id)  # Query fresh from database
    print(f"🔍 DEBUG: Driver profile_image_url: {fresh_user.profile_image_url}")
    
    # Get vehicles assigned to this driver
    vehicles = Vehicle.query.filter_by(assigned_driver_id=user_id).all()
    
    # Debug logging
    print(f"🔍 DEBUG: Driver dashboard request for user {current_user.id}")
    print(f"🔍 DEBUG: Found {len(vehicles)} vehicles")
    for vehicle in vehicles:
        print(f"🔍 DEBUG: Vehicle {vehicle.id} - Route: {vehicle.route}, Route Info: {vehicle.route_info}")
    
    print("🚨 ROUTE: About to render template with version 1.0.2")
    # Pass fresh_user to template as driver_user to ensure we use latest profile_image_url
    # The template can use driver_user.profile_image_url if available, otherwise fall back to current_user
    response = make_response(render_template('driver/dashboard.html', 
                                             vehicles=vehicles, 
                                             driver_user=fresh_user,
                                             template_version='1.0.2'))
    
    # Add aggressive cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return response

@driver_bp.route('/change-password')
@login_required
def change_password_page():
    """Change password page."""
    if current_user.user_type != 'driver':
        flash('Access denied. Driver account required.', 'error')
        return redirect(url_for('index'))
    
    return render_template('driver/change_password.html')

@driver_bp.route('/vehicle/<int:vehicle_id>/occupancy', methods=['POST'])
@login_required
def update_occupancy(vehicle_id):
    """Update vehicle occupancy status."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # Get the new occupancy status from the request
    data = request.get_json()
    new_status = data.get('occupancy_status')
    
    if not new_status or new_status not in ['vacant', 'full']:
        return jsonify({'error': 'Invalid occupancy status. Must be "vacant" or "full".'}), 400
    
    # Store the old status for logging
    old_status = vehicle.occupancy_status
    
    # Update the vehicle occupancy status
    vehicle.occupancy_status = new_status
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=vehicle_id,
        action='occupancy_change',
        meta_data={
            'old_value': old_status,
            'new_value': new_status,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save changes to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Vehicle occupancy status updated to {new_status}',
        'occupancy_status': new_status
    })

@driver_bp.route('/vehicle/<int:vehicle_id>/details')
@login_required
def get_vehicle_details(vehicle_id):
    """Get detailed vehicle information for the driver."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # Return vehicle details
    return jsonify({
        'success': True,
        'vehicle': {
            'id': vehicle.id,
            'registration_number': vehicle.registration_number,
            'vehicle_type': vehicle.vehicle_type,
            'status': vehicle.status,
            'occupancy_status': vehicle.occupancy_status,
            'route': vehicle.route,
            'route_info': vehicle.route_info,
            'assigned_driver_id': vehicle.assigned_driver_id,
            'last_location_update': vehicle.last_location_update.isoformat() if vehicle.last_location_update else None
        }
    })

@driver_bp.route('/trip/start', methods=['POST'])
@login_required
def start_trip():
    """Start a new trip."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get data from request
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    route_name = data.get('route_name')
    
    if not vehicle_id:
        return jsonify({'error': 'Vehicle ID is required.'}), 400
    
    if not route_name:
        return jsonify({'error': 'Route name is required.'}), 400
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # Check if there's already an active trip for this vehicle
    active_trip = Trip.query.filter_by(
        vehicle_id=vehicle_id,
        status='active'
    ).first()
    
    if active_trip:
        return jsonify({'error': 'There is already an active trip for this vehicle.'}), 400
    
    # Create a new trip
    trip = Trip(
        vehicle_id=vehicle_id,
        driver_id=current_user.id,
        route_name=route_name,
        start_time=datetime.utcnow(),
        status='active'
    )
    
    # Clear the public vehicle cache so the vehicle immediately appears on the map
    try:
        from routes.public import clear_vehicle_cache
        clear_vehicle_cache()
    except Exception as e:
        print(f"Could not clear vehicle cache: {e}")
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=vehicle_id,
        action='trip_start',
        meta_data={
            'trip_id': None,  # Will be updated after commit
            'route_name': route_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save changes to database
    db.session.add(trip)
    db.session.add(log)
    db.session.commit()
    
    # Update the log with the trip ID
    log.meta_data['trip_id'] = trip.id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Trip started successfully',
        'trip': {
            'id': trip.id,
            'vehicle_id': trip.vehicle_id,
            'driver_id': trip.driver_id,
            'route_name': trip.route_name,
            'start_time': trip.start_time.isoformat(),
            'status': trip.status
        }
    })

@driver_bp.route('/trip/end', methods=['POST'])
@login_required
def end_trip():
    """End an active trip."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get data from request
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    
    if not vehicle_id:
        return jsonify({'error': 'Vehicle ID is required.'}), 400
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # Get the active trip for this vehicle
    active_trip = Trip.query.filter_by(
        vehicle_id=vehicle_id,
        status='active'
    ).first()
    
    if not active_trip:
        return jsonify({'error': 'No active trip found for this vehicle.'}), 404
    
    # End the trip
    active_trip.end_time = datetime.utcnow()
    active_trip.status = 'completed'
    
    # Clear the public vehicle cache so the vehicle is immediately hidden from the map
    try:
        from routes.public import clear_vehicle_cache
        clear_vehicle_cache()
    except Exception as e:
        print(f"Could not clear vehicle cache: {e}")
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=vehicle_id,
        action='trip_end',
        meta_data={
            'trip_id': active_trip.id,
            'route_name': active_trip.route_name,
            'duration_minutes': int((active_trip.end_time - active_trip.start_time).total_seconds() / 60),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save changes to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Trip ended successfully',
        'trip': {
            'id': active_trip.id,
            'vehicle_id': active_trip.vehicle_id,
            'driver_id': active_trip.driver_id,
            'route_name': active_trip.route_name,
            'start_time': active_trip.start_time.isoformat(),
            'end_time': active_trip.end_time.isoformat(),
            'status': active_trip.status
        }
    })

@driver_bp.route('/passenger', methods=['POST'])
@login_required
def record_passenger_event():
    """Record a passenger boarding or alighting event."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get data from request
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    event_type = data.get('event_type')
    count = data.get('count', 1)
    notes = data.get('notes', '')
    
    if not vehicle_id:
        return jsonify({'error': 'Vehicle ID is required.'}), 400
    
    if not event_type or event_type not in ['board', 'alight']:
        return jsonify({'error': 'Event type must be "board" or "alight".'}), 400
    
    try:
        count = int(count)
        if count < 1:
            return jsonify({'error': 'Count must be a positive integer.'}), 400
    except ValueError:
        return jsonify({'error': 'Count must be a valid integer.'}), 400
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # Get the active trip for this vehicle
    active_trip = Trip.query.filter_by(
        vehicle_id=vehicle_id,
        status='active'
    ).first()
    
    if not active_trip:
        return jsonify({'error': 'No active trip found for this vehicle. Start a trip first.'}), 404
    
    # Create a passenger event
    event = PassengerEvent(
        trip_id=active_trip.id,
        event_type=event_type,
        count=count,
        notes=notes
    )
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=vehicle_id,
        action=f'passenger_{event_type}',
        meta_data={
            'trip_id': active_trip.id,
            'count': count,
            'notes': notes,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save changes to database
    db.session.add(event)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Passenger {event_type} event recorded successfully',
        'event': {
            'id': event.id,
            'trip_id': event.trip_id,
            'event_type': event.event_type,
            'count': event.count,
            'created_at': event.created_at.isoformat()
        }
    })

@driver_bp.route('/password', methods=['POST'])
@login_required
def change_password():
    """Change driver's password."""
    print(f"🔍 Password change request from user {current_user.id}")
    
    if current_user.user_type != 'driver':
        print("❌ Access denied - user is not a driver")
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get data from request
    data = request.get_json()
    print(f"🔍 Request data: {data}")
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not current_password:
        return jsonify({'error': 'Current password is required.'}), 400
    
    if not new_password:
        return jsonify({'error': 'New password is required.'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'New password and confirmation do not match.'}), 400
    
    # Check if current password is correct
    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'error': 'Current password is incorrect.'}), 401
    
    # Update password
    current_user.password_hash = generate_password_hash(new_password)
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=None,
        action='password_change',
        meta_data={
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save changes to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    })

@driver_bp.route('/export/trip-history')
@login_required
def export_trip_history():
    """Export driver's trip history."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    try:
        # Get driver's trip history
        trips = Trip.query.filter_by(driver_id=current_user.id).order_by(Trip.start_time.desc()).all()
        
        # Create CSV content
        csv_content = "Trip ID,Vehicle ID,Route Name,Start Time,End Time,Status,Total Passengers\n"
        
        for trip in trips:
            # Calculate total passengers for this trip
            passenger_events = PassengerEvent.query.filter_by(trip_id=trip.id).all()
            boards = sum(event.count for event in passenger_events if event.event_type == 'board')
            alights = sum(event.count for event in passenger_events if event.event_type == 'alight')
            total_passengers = max(0, boards - alights)
            
            end_time = trip.end_time.isoformat() if trip.end_time else 'N/A'
            
            csv_content += f"{trip.id},{trip.vehicle_id},{trip.route_name},{trip.start_time.isoformat()},{end_time},{trip.status},{total_passengers}\n"
        
        # Create response with CSV
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=trip-history-{current_user.id}-{datetime.utcnow().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Error exporting trip history: {e}")
        return jsonify({'error': 'Failed to export trip history'}), 500

@driver_bp.route('/export/action-logs')
@login_required
def export_action_logs():
    """Export driver's action logs."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    try:
        # Get driver's action logs
        logs = DriverActionLog.query.filter_by(driver_id=current_user.id).order_by(DriverActionLog.created_at.desc()).all()
        
        # Create CSV content
        csv_content = "Timestamp,Action,Vehicle ID,Meta Data\n"
        
        for log in logs:
            meta_data = json.dumps(log.meta_data) if log.meta_data else 'N/A'
            csv_content += f"{log.created_at.isoformat()},{log.action},{log.vehicle_id or 'N/A'},{meta_data}\n"
        
        # Create response with CSV
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=action-logs-{current_user.id}-{datetime.utcnow().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        print(f"Error exporting action logs: {e}")
        return jsonify({'error': 'Failed to export action logs'}), 500

@driver_bp.route('/export/profile-data')
@login_required
def export_profile_data():
    """Export driver's profile data."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    try:
        # Prepare profile data
        profile_data = {
            'user_id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'user_type': current_user.user_type,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'is_active': current_user.is_active,
            'profile_image_url': current_user.profile_image_url,
            'company_name': current_user.company_name,
            'contact_number': current_user.contact_number,
            'current_latitude': current_user.current_latitude,
            'current_longitude': current_user.current_longitude,
            'accuracy': current_user.accuracy
        }
        
        # Create response with JSON
        response = make_response(json.dumps(profile_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=profile-data-{current_user.id}-{datetime.utcnow().strftime("%Y%m%d")}.json'
        
        return response
        
    except Exception as e:
        print(f"Error exporting profile data: {e}")
        return jsonify({'error': 'Failed to export profile data'}), 500

@driver_bp.route('/deactivate-account', methods=['POST'])
@login_required
def deactivate_account():
    """Deactivate driver's account."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    try:
        # Deactivate the account
        current_user.is_active = False
        
        # Create a driver action log
        log = DriverActionLog(
            driver_id=current_user.id,
            vehicle_id=None,
            action='account_deactivated',
            meta_data={
                'timestamp': datetime.utcnow().isoformat(),
                'reason': 'Driver requested deactivation'
            }
        )
        
        # Save changes to database
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deactivated successfully'
        })
        
    except Exception as e:
        print(f"Error deactivating account: {e}")
        return jsonify({'error': 'Failed to deactivate account'}), 500

@driver_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete driver's account permanently."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    try:
        # Create a driver action log before deletion
        log = DriverActionLog(
            driver_id=current_user.id,
            vehicle_id=None,
            action='account_deleted',
            meta_data={
                'timestamp': datetime.utcnow().isoformat(),
                'reason': 'Driver requested permanent deletion'
            }
        )
        
        # Save the log first
        db.session.add(log)
        db.session.commit()
        
        # Delete the user account
        db.session.delete(current_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting account: {e}")
        return jsonify({'error': 'Failed to delete account'}), 500

@driver_bp.route('/trip-stats')
@login_required
def get_trip_stats():
    """Get trip statistics for the current driver."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    try:
        # Get today's date
        today = datetime.utcnow().date()
        
        # Count today's trips
        today_trips = Trip.query.filter(
            Trip.driver_id == current_user.id,
            Trip.start_time >= datetime.combine(today, datetime.min.time()),
            Trip.start_time < datetime.combine(today, datetime.max.time())
        ).count()
        
        # Count total trips
        total_trips = Trip.query.filter_by(driver_id=current_user.id).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'today_trips': today_trips,
                'total_trips': total_trips
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@driver_bp.route('/current-trip/<int:vehicle_id>')
@login_required
def get_current_trip(vehicle_id):
    """Get the current active trip for a vehicle."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # Get the active trip for this vehicle
    active_trip = Trip.query.filter_by(
        vehicle_id=vehicle_id,
        status='active'
    ).first()
    
    if not active_trip:
        return jsonify({
            'success': True,
            'trip': None
        })
    
    # Get passenger events for this trip
    passenger_events = PassengerEvent.query.filter_by(trip_id=active_trip.id).all()
    
    # Calculate current passenger count (boards - alights)
    boards = sum(event.count for event in passenger_events if event.event_type == 'board')
    alights = sum(event.count for event in passenger_events if event.event_type == 'alight')
    current_passengers = max(0, boards - alights)
    
    return jsonify({
        'success': True,
        'trip': {
            'id': active_trip.id,
            'vehicle_id': active_trip.vehicle_id,
            'driver_id': active_trip.driver_id,
            'route_name': active_trip.route_name,
            'start_time': active_trip.start_time.isoformat(),
            'status': active_trip.status,
            'passenger_summary': {
                'boards': boards,
                'alights': alights,
                'current_passengers': current_passengers
            }
        }
    })

@driver_bp.route('/action-logs')
@login_required
def view_action_logs():
    """View driver action logs."""
    if current_user.user_type != 'driver':
        flash('Access denied. Driver account required.', 'error')
        return redirect(url_for('index'))
    
    # Get logs for this driver
    logs = DriverActionLog.query.filter_by(driver_id=current_user.id)\
        .order_by(DriverActionLog.created_at.desc())\
        .limit(100)\
        .all()
    
    return render_template('driver/action_logs.html', logs=logs)

@driver_bp.route('/trip/<int:trip_id>/events')
@login_required
def get_trip_events(trip_id):
    """Get all passenger events for a trip."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get the trip
    trip = Trip.query.get_or_404(trip_id)
    
    # Check if the driver owns this trip
    if trip.driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You do not own this trip.'}), 403
    
    # Get all passenger events for this trip
    events = PassengerEvent.query.filter_by(trip_id=trip_id).order_by(PassengerEvent.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'events': [
            {
                'id': event.id,
                'trip_id': event.trip_id,
                'event_type': event.event_type,
                'count': event.count,
                'notes': event.notes,
                'created_at': event.created_at.isoformat()
            }
            for event in events
        ]
    })

@driver_bp.route('/calculate-route', methods=['POST'])
@login_required
def calculate_route():
    """Calculate route between start and end points."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get data from request
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    start_point = data.get('start_point')
    end_point = data.get('end_point')
    
    if not vehicle_id:
        return jsonify({'error': 'Vehicle ID is required.'}), 400
    
    if not start_point:
        return jsonify({'error': 'Start point is required.'}), 400
    
    if not end_point:
        return jsonify({'error': 'End point is required.'}), 400
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You are not assigned to this vehicle.'}), 403
    
    # In a real application, you would use a mapping API to calculate the route
    # For this implementation, we'll simulate route calculation
    
    # Calculate a random distance between 5 and 30 km
    distance_km = round(5 + (25 * float(hash(start_point + end_point) % 100) / 100), 1)
    
    # Calculate ETA based on average speed of 30 km/h
    eta_minutes = int(distance_km * 60 / 30)
    
    # Create a route name
    route_name = f"{start_point} to {end_point}"
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=vehicle_id,
        action='route_calculated',
        meta_data={
            'start_point': start_point,
            'end_point': end_point,
            'distance_km': distance_km,
            'eta_minutes': eta_minutes,
            'route_name': route_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save log to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'route': {
            'vehicle_id': vehicle_id,
            'start_point': start_point,
            'end_point': end_point,
            'distance_km': distance_km,
            'eta_minutes': eta_minutes,
            'route_name': route_name
        }
    })

@driver_bp.route('/passenger-counter/<int:vehicle_id>')
@login_required
def passenger_counter(vehicle_id):
    """Passenger counter page for a vehicle."""
    if current_user.user_type != 'driver':
        flash('Access denied. Driver account required.', 'error')
        return redirect(url_for('index'))
    
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the driver is assigned to this vehicle
    if vehicle.assigned_driver_id != current_user.id:
        flash('Access denied. You are not assigned to this vehicle.', 'error')
        return redirect(url_for('driver.dashboard'))
    
    return render_template('operator/passenger_counter.html', vehicle=vehicle)

@driver_bp.route('/settings')
@login_required
def settings():
    """Driver settings page."""
    if current_user.user_type != 'driver':
        flash('Access denied. Driver account required.', 'error')
        return redirect(url_for('index'))
    
    # Include recent action logs for embedding in settings page
    logs = DriverActionLog.query.filter_by(driver_id=current_user.id) \
        .order_by(DriverActionLog.created_at.desc()) \
        .limit(50) \
        .all()
    
    return render_template('driver/settings.html', logs=logs)



@driver_bp.route('/vehicle-assignment')
@login_required
def get_driver_vehicle_assignment():
    """Get the current driver's vehicle assignment."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Get vehicles assigned to this driver
    vehicles = Vehicle.query.filter_by(assigned_driver_id=current_user.id).all()
    
    # Format vehicle data for frontend
    vehicles_data = []
    for vehicle in vehicles:
        vehicles_data.append({
            'id': vehicle.id,
            'registration_number': vehicle.registration_number,
            'vehicle_type': vehicle.vehicle_type,
            'status': vehicle.status,
            'occupancy_status': vehicle.occupancy_status,
            'route': vehicle.route,
            'route_info': vehicle.route_info,
            'capacity': vehicle.capacity,
            'assigned_driver_id': vehicle.assigned_driver_id,
            'current_latitude': vehicle.current_latitude,
            'current_longitude': vehicle.current_longitude,
            'last_updated': vehicle.last_updated.isoformat() if vehicle.last_updated else None
        })
    
    return jsonify({
        'success': True,
        'vehicles': vehicles_data,
        'count': len(vehicles_data)
    })

@driver_bp.route('/vehicle/<int:vehicle_id>/route-info')
@login_required
def get_vehicle_route_info(vehicle_id):
    """Get vehicle route information."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Check if driver is assigned to this vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You can only access your assigned vehicles.'}), 403
    
    # Debug logging
    print(f"🔍 DEBUG: Route info request for vehicle {vehicle_id}")
    print(f"🔍 DEBUG: Vehicle route field: {vehicle.route}")
    print(f"🔍 DEBUG: Vehicle route_info field: {vehicle.route_info}")
    print(f"🔍 DEBUG: Vehicle assigned_driver_id: {vehicle.assigned_driver_id}")
    print(f"🔍 DEBUG: Current user ID: {current_user.id}")
    
    # Get route information
    route_info = {
        'vehicle_id': vehicle.id,
        'route': vehicle.route,
        'route_info': vehicle.route_info,
        'debug_info': {
            'route_field_value': str(vehicle.route),
            'route_info_field_value': str(vehicle.route_info),
            'route_field_type': type(vehicle.route).__name__,
            'route_info_field_type': type(vehicle.route_info).__name__
        }
    }
    
    print(f"🔍 DEBUG: Returning route info: {route_info}")
    
    return jsonify(route_info)

@driver_bp.route('/vehicle/<int:vehicle_id>/route', methods=['POST'])
@login_required
def update_vehicle_route(vehicle_id):
    """Update vehicle route (for assigned drivers only)."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Check if driver is assigned to this vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You can only update your assigned vehicles.'}), 403
    
    # Get data from request
    data = request.get_json()
    route_name = data.get('route_name')
    start_location = data.get('start_location')
    end_location = data.get('end_location')
    
    if not all([route_name, start_location, end_location]):
        return jsonify({'error': 'Route name, start location, and end location are required'}), 400
    
    # Create route info JSON
    route_info = {
        'origin': start_location,
        'destination': end_location,
        'route_set_at': datetime.utcnow().isoformat(),
        'route_set_by': current_user.id
    }
    
    # Update vehicle route
    vehicle.route = route_name
    vehicle.route_info = json.dumps(route_info)
    
    # Create a driver action log
    log = DriverActionLog(
        driver_id=current_user.id,
        vehicle_id=vehicle_id,
        action='route_changed',
        meta_data={
            'old_route': vehicle.route,
            'new_route': route_name,
            'start_location': start_location,
            'end_location': end_location,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Save to database
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Vehicle route updated successfully',
        'route': {
            'name': route_name,
            'start_location': start_location,
            'end_location': end_location,
            'updated_at': datetime.utcnow().isoformat()
        }
    })

@driver_bp.route('/vehicle/<int:vehicle_id>/location', methods=['POST'])
@login_required
def update_vehicle_location(vehicle_id):
    """Update vehicle location (for assigned drivers only)."""
    if current_user.user_type != 'driver':
        return jsonify({'error': 'Access denied. Driver account required.'}), 403
    
    # Check if driver is assigned to this vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.assigned_driver_id != current_user.id:
        return jsonify({'error': 'Access denied. You can only update your assigned vehicles.'}), 403
    
    # Handle both JSON and form data
    data = request.get_json() if request.is_json else request.form
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    occupancy_status = data.get('occupancy_status')
    
    if not all([latitude, longitude]):
        return jsonify({'error': 'Missing location data'}), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        accuracy = float(accuracy) if accuracy else None
    except ValueError:
        return jsonify({'error': 'Invalid location format'}), 400
    
    # Update vehicle location
    vehicle.current_latitude = latitude
    vehicle.current_longitude = longitude
    if accuracy:
        vehicle.accuracy = accuracy
    if occupancy_status and occupancy_status in ['vacant', 'full']:
        vehicle.occupancy_status = occupancy_status
    vehicle.last_updated = datetime.utcnow()
    
    # Create location log
    from models.location_log import LocationLog
    location_log = LocationLog(
        vehicle_id=vehicle.id,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy
    )
    
    # Save to database
    db.session.add(location_log)
    db.session.commit()
    
    # Emit WebSocket event for real-time updates
    try:
        from events_optimized import emit_vehicle_update
        emit_vehicle_update(vehicle_id, 'vehicle_updated', {
            'latitude': latitude,
            'longitude': longitude,
            'occupancy_status': vehicle.occupancy_status,
            'last_updated': vehicle.last_updated.isoformat()
        })
    except ImportError:
        pass  # WebSocket events not available
    
    return jsonify({
        'success': True,
        'message': 'Vehicle location updated successfully',
        'location': {
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'occupancy_status': vehicle.occupancy_status,
            'last_updated': vehicle.last_updated.isoformat()
        }
    })