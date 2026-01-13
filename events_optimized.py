from flask import request, current_app
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
import time
from datetime import datetime, timedelta
from models.vehicle import Vehicle
from models.location_log import LocationLog
from models import db
import json
import math
from sqlalchemy import desc

# Cache for vehicle positions to reduce database queries
vehicle_positions_cache = {}
last_cache_update = 0
CACHE_EXPIRY = 5  # seconds

def handle_connect():
    """Handle client connection."""
    current_app.logger.debug(f"Client connected: {request.sid}")
    
    # Add user to their own room if authenticated
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        current_app.logger.debug(f"User {current_user.id} joined room: user_{current_user.id}")
    
    # Add all clients to a global room
    join_room('all_clients')
    
    # Emit connection acknowledgement
    emit('connect_ack', {'status': 'connected', 'timestamp': time.time()})

def handle_disconnect():
    """Handle client disconnection."""
    current_app.logger.debug(f"Client disconnected: {request.sid}")
    
    # Remove user from their room if authenticated
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")
    
    # Remove from global room
    leave_room('all_clients')

def handle_location_update(data):
    """Handle location update from vehicles."""
    if not current_user.is_authenticated:
        current_app.logger.warning(f"Unauthorized location update attempt: {request.sid}")
        return
    
    # Allow both operators and assigned drivers
    if current_user.user_type not in ['operator', 'admin', 'driver']:
        current_app.logger.warning(f"Unauthorized location update attempt: {request.sid}")
        return
    
    try:
        vehicle_id = data.get('vehicle_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        accuracy = data.get('accuracy')
        
        if not all([vehicle_id, latitude, longitude]):
            current_app.logger.warning(f"Invalid location data: {data}")
            return
        
        # Convert to float
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            accuracy = float(accuracy) if accuracy else None
        except (ValueError, TypeError):
            current_app.logger.warning(f"Invalid location format: {data}")
            return
        
        # Get the vehicle
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            current_app.logger.warning(f"Vehicle not found: {vehicle_id}")
            return
        
        # Check permissions: operators can update owned vehicles, drivers can update assigned vehicles
        if current_user.user_type in ['operator', 'admin']:
            if vehicle.owner_id != current_user.id:
                current_app.logger.warning(f"Vehicle not owned by operator: {vehicle_id}")
                return
        elif current_user.user_type == 'driver':
            if vehicle.assigned_driver_id != current_user.id:
                current_app.logger.warning(f"Vehicle not assigned to driver: {vehicle_id}")
                return
        
        # Calculate speed if we have previous location
        speed_kmh = None
        if vehicle.current_latitude and vehicle.current_longitude and vehicle.last_updated:
            # Calculate distance in kilometers
            distance_km = calculate_distance_km(
                vehicle.current_latitude, vehicle.current_longitude,
                latitude, longitude
            )
            
            # Calculate time difference in hours
            time_diff = (datetime.utcnow() - vehicle.last_updated).total_seconds() / 3600
            
            # Calculate speed if time difference is significant
            if time_diff > 0:
                speed_kmh = distance_km / time_diff
                
                # Filter out unrealistic speeds (e.g., GPS jumps)
                if speed_kmh > 120:  # Max 120 km/h as sanity check
                    speed_kmh = None
        
        # Update vehicle location
        vehicle.current_latitude = latitude
        vehicle.current_longitude = longitude
        if accuracy:
            vehicle.accuracy = accuracy
        vehicle.last_updated = datetime.utcnow()
        if speed_kmh:
            vehicle.last_speed_kmh = speed_kmh
        
        # Create location log
        location_log = LocationLog(
            vehicle_id=vehicle.id,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy
        )
        
        # Save to database
        db.session.add(location_log)
        db.session.commit()
        
        # Update cache
        update_vehicle_cache(vehicle)
        
        # Only broadcast to all clients if vehicle has an active trip
        from models.user import Trip
        active_trip = Trip.query.filter_by(
            vehicle_id=vehicle.id,
            status='active'
        ).first()
        
        if active_trip:
            emit('vehicle_update', {
                'id': vehicle.id,
                'latitude': latitude,
                'longitude': longitude,
                'status': vehicle.status,
                'occupancy_status': vehicle.occupancy_status,
                'type': vehicle.vehicle_type,
                'route': vehicle.route,
                'last_updated': vehicle.last_updated.isoformat(),
                'speed_kmh': speed_kmh
            }, room='all_clients')
        
        current_app.logger.debug(f"Location updated for vehicle {vehicle_id}: {latitude}, {longitude}")
        
    except Exception as e:
        current_app.logger.error(f"Error handling location update: {str(e)}")

def handle_request_vehicle_positions():
    """Handle request for all active vehicle positions."""
    try:
        # Get cached positions or update cache
        positions = get_cached_positions()
        
        # Emit to the requesting client only
        emit('vehicle_positions', {
            'vehicles': positions,
            'count': len(positions),
            'timestamp': time.time()
        })
        
        current_app.logger.debug(f"Sent vehicle positions to client: {request.sid}")
        
    except Exception as e:
        current_app.logger.error(f"Error handling vehicle positions request: {str(e)}")

def update_vehicle_cache(vehicle):
    """Update the cache for a specific vehicle."""
    global vehicle_positions_cache
    
    vehicle_positions_cache[vehicle.id] = {
        'id': vehicle.id,
        'latitude': vehicle.current_latitude,
        'longitude': vehicle.current_longitude,
        'status': vehicle.status,
        'occupancy_status': vehicle.occupancy_status,
        'type': vehicle.vehicle_type,
        'route': vehicle.route,
        'last_updated': vehicle.last_updated.isoformat() if vehicle.last_updated else None,
        'speed_kmh': vehicle.last_speed_kmh
    }

def cache_vehicle_positions():
    """Cache all active vehicle positions."""
    global vehicle_positions_cache, last_cache_update
    
    # Skip if cache is still fresh
    current_time = time.time()
    if current_time - last_cache_update < CACHE_EXPIRY and vehicle_positions_cache:
        return
    
    # Get all active vehicles that have active trips
    from models.user import Trip
    active_vehicles = Vehicle.query.filter(
        Vehicle.status.in_(['active', 'delayed']),
        Vehicle.current_latitude.isnot(None),
        Vehicle.current_longitude.isnot(None)
    ).join(Trip, Vehicle.id == Trip.vehicle_id).filter(
        Trip.status == 'active'
    ).all()
    
    # Update cache
    vehicle_positions_cache = {}
    for vehicle in active_vehicles:
        update_vehicle_cache(vehicle)
    
    last_cache_update = current_time
    current_app.logger.debug(f"Vehicle positions cache updated with {len(vehicle_positions_cache)} vehicles")

def get_cached_positions():
    """Get cached vehicle positions or update cache if expired."""
    global last_cache_update
    
    # Update cache if expired
    current_time = time.time()
    if current_time - last_cache_update > CACHE_EXPIRY or not vehicle_positions_cache:
        cache_vehicle_positions()
    
    # Return cached positions as a list
    return list(vehicle_positions_cache.values())

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    # Earth radius in kilometers
    R = 6371
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def handle_join_vehicle_room(data):
    """Handle client joining a vehicle-specific room for real-time updates."""
    try:
        vehicle_id = data.get('vehicle_id')
        if not vehicle_id:
            current_app.logger.warning("No vehicle_id provided for room join")
            return
        
        # Join the vehicle-specific room
        join_room(f"vehicle_{vehicle_id}")
        current_app.logger.debug(f"Client {request.sid} joined vehicle room: vehicle_{vehicle_id}")
        
        # Send confirmation
        emit('room_joined', {
            'status': 'joined',
            'room': f"vehicle_{vehicle_id}",
            'vehicle_id': vehicle_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error handling vehicle room join: {str(e)}")

def emit_vehicle_update(vehicle_id, update_type, data):
    """Emit vehicle update to all clients in the vehicle's room."""
    try:
        # Import socketio from app to use in HTTP request context
        # Import inside function to avoid circular import issues
        from app import socketio
        
        if socketio:
            # Use socketio.emit() instead of emit() when called from HTTP routes
            socketio.emit(update_type, {
                'vehicle_id': vehicle_id,
                'timestamp': time.time(),
                **data
            }, room=f"vehicle_{vehicle_id}")
            
            current_app.logger.debug(f"Emitted {update_type} for vehicle {vehicle_id}")
        else:
            current_app.logger.warning(f"SocketIO not available, skipping emit for vehicle {vehicle_id}")
        
    except ImportError:
        current_app.logger.warning(f"SocketIO not available, skipping emit for vehicle {vehicle_id}")
    except Exception as e:
        current_app.logger.error(f"Error emitting vehicle update: {str(e)}")

def emit_trip_update(vehicle_id, update_type, data):
    """Emit trip update to all clients in the vehicle's room."""
    try:
        # Import socketio from app to use in HTTP request context
        from app import socketio
        
        if socketio:
            # Use socketio.emit() instead of emit() when called from HTTP routes
            socketio.emit('trip_updated', {
                'vehicle_id': vehicle_id,
                'update_type': update_type,
                'timestamp': time.time(),
                **data
            }, room=f"vehicle_{vehicle_id}")
            
            current_app.logger.debug(f"Emitted trip update {update_type} for vehicle {vehicle_id}")
        else:
            current_app.logger.warning(f"SocketIO not available, skipping trip update for vehicle {vehicle_id}")
        
    except ImportError:
        current_app.logger.warning(f"SocketIO not available, skipping trip update for vehicle {vehicle_id}")
    except Exception as e:
        current_app.logger.error(f"Error emitting trip update: {str(e)}")

def emit_passenger_event(vehicle_id, event_type, data):
    """Emit passenger event to all clients in the vehicle's room."""
    try:
        # Import socketio from app to use in HTTP request context
        from app import socketio
        
        if socketio:
            # Use socketio.emit() instead of emit() when called from HTTP routes
            socketio.emit('passenger_event', {
                'vehicle_id': vehicle_id,
                'event_type': event_type,
                'timestamp': time.time(),
                **data
            }, room=f"vehicle_{vehicle_id}")
            
            current_app.logger.debug(f"Emitted passenger event {event_type} for vehicle {vehicle_id}")
        else:
            current_app.logger.warning(f"SocketIO not available, skipping passenger event for vehicle {vehicle_id}")
        
    except ImportError:
        current_app.logger.warning(f"SocketIO not available, skipping passenger event for vehicle {vehicle_id}")
    except Exception as e:
        current_app.logger.error(f"Error emitting passenger event: {str(e)}")

def handle_driver_vehicle_update(data):
    """Handle vehicle updates from drivers (occupancy, trip status, etc.)."""
    if not current_user.is_authenticated or current_user.user_type != 'driver':
        current_app.logger.warning(f"Unauthorized driver vehicle update attempt: {request.sid}")
        return
    
    try:
        vehicle_id = data.get('vehicle_id')
        update_type = data.get('update_type')
        update_data = data.get('data', {})
        
        if not vehicle_id or not update_type:
            current_app.logger.warning(f"Invalid driver vehicle update data: {data}")
            return
        
        # Get the vehicle and check assignment
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle or vehicle.assigned_driver_id != current_user.id:
            current_app.logger.warning(f"Driver not assigned to vehicle: {vehicle_id}")
            return
        
        # Handle different update types
        if update_type == 'occupancy_change':
            new_status = update_data.get('occupancy_status')
            if new_status in ['vacant', 'full']:
                vehicle.occupancy_status = new_status
                vehicle.last_updated = datetime.utcnow()
                db.session.commit()
                
                # Emit update to all clients
                emit('vehicle_update', {
                    'id': vehicle.id,
                    'occupancy_status': new_status,
                    'last_updated': vehicle.last_updated.isoformat()
                }, room='all_clients')
                
                current_app.logger.debug(f"Driver updated vehicle {vehicle_id} occupancy to {new_status}")
        
        elif update_type == 'trip_status':
            # Handle trip status updates
            trip_status = update_data.get('trip_status')
            if trip_status:
                # Update trip status logic here
                current_app.logger.debug(f"Driver updated vehicle {vehicle_id} trip status to {trip_status}")
        
        # Emit to vehicle-specific room
        emit_vehicle_update(vehicle_id, 'driver_vehicle_updated', {
            'update_type': update_type,
            'driver_id': current_user.id,
            'timestamp': time.time(),
            **update_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error handling driver vehicle update: {str(e)}")

def emit_vehicle_assignment_change(vehicle_id, driver_id, action):
    """Emit vehicle assignment change to relevant users."""
    try:
        # Import socketio from app to use in HTTP request context
        from app import socketio
        
        if socketio:
            # Notify the driver if assigned
            if driver_id:
                socketio.emit('vehicle_assigned', {
                    'vehicle_id': vehicle_id,
                    'action': action,
                    'timestamp': time.time()
                }, room=f"user_{driver_id}")
            
            # Notify all clients about assignment change
            socketio.emit('vehicle_assignment_updated', {
                'vehicle_id': vehicle_id,
                'driver_id': driver_id,
                'action': action,
                'timestamp': time.time()
            }, room='all_clients')
            
            current_app.logger.debug(f"Emitted vehicle assignment change: {action} for vehicle {vehicle_id}")
        else:
            current_app.logger.warning(f"SocketIO not available, skipping assignment change for vehicle {vehicle_id}")
        
    except ImportError:
        current_app.logger.warning(f"SocketIO not available, skipping assignment change for vehicle {vehicle_id}")
    except Exception as e:
        current_app.logger.error(f"Error emitting assignment change: {str(e)}")

def handle_driver_status_update(data):
    """Handle driver status updates (online/offline, availability)."""
    if not current_user.is_authenticated or current_user.user_type != 'driver':
        return
    
    try:
        status = data.get('status')
        vehicle_id = data.get('vehicle_id')
        
        if status in ['online', 'offline', 'available', 'busy']:
            # Update driver status
            current_user.current_latitude = data.get('latitude')
            current_user.current_longitude = data.get('longitude')
            current_user.accuracy = data.get('accuracy')
            
            # Emit driver status update
            emit('driver_status_updated', {
                'driver_id': current_user.id,
                'status': status,
                'vehicle_id': vehicle_id,
                'location': {
                    'latitude': current_user.current_latitude,
                    'longitude': current_user.current_longitude,
                    'accuracy': current_user.accuracy
                },
                'timestamp': time.time()
            }, room='all_clients')
            
            current_app.logger.debug(f"Driver {current_user.id} status updated to {status}")
            
    except Exception as e:
        current_app.logger.error(f"Error handling driver status update: {str(e)}")