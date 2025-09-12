from flask_socketio import emit
from flask_login import current_user
from models.notification import Notification, NotificationSetting
from models.user import User
from models.vehicle import Vehicle
from models import db
from datetime import datetime
from routes.notifications import haversine_distance, check_notification_cooldown

def handle_location_update(data):
    """Handle location updates and send proximity notifications."""
    print(f"[DEBUG] Received location update: {data}")
    
    if not current_user.is_authenticated:
        print("[DEBUG] Ignoring location update: User not authenticated")
        return
    
    vehicle_id = data.get('vehicle_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not all([vehicle_id, latitude, longitude]):
        print(f"[DEBUG] Ignoring location update: Missing data - vehicle_id: {vehicle_id}, lat: {latitude}, lng: {longitude}")
        return
    
    print(f"[DEBUG] Processing location update for vehicle {vehicle_id}: lat={latitude}, lng={longitude}")
    
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        print(f"[DEBUG] Vehicle {vehicle_id} not found in database")
        return
    
    # Update vehicle location
    vehicle.current_latitude = float(latitude)
    vehicle.current_longitude = float(longitude)
    vehicle.last_updated = datetime.utcnow()
    db.session.commit()
    
    print(f"[DEBUG] Updated location for vehicle {vehicle_id} (operator: {vehicle.owner_id}): lat={latitude}, lng={longitude}")
    
    # Notify nearby commuters
    print(f"[DEBUG] Calling notify_nearby_commuters for vehicle {vehicle_id}")
    notify_nearby_commuters(vehicle)
    
    # For testing: directly force notifications to all commuters
    commuters = User.query.filter_by(user_type='commuter').all()
    for commuter in commuters:
        if commuter.current_latitude and commuter.current_longitude:
            print(f"[DEBUG] Forcing notification to commuter {commuter.id} about vehicle {vehicle_id}")
            force_notify_commuter(commuter.id, vehicle_id)
    
    # Notify commuters waiting for this route
    notify_route_subscribers(vehicle)

def notify_nearby_commuters(vehicle):
    """Notify commuters who are within the notification radius."""
    print(f"[DEBUG] Checking for commuters near vehicle {vehicle.id} ({vehicle.registration_number})")
    
    if not vehicle.current_latitude or not vehicle.current_longitude:
        print(f"[DEBUG] Vehicle {vehicle.id} has invalid coordinates: lat={vehicle.current_latitude}, lng={vehicle.current_longitude}")
        return
        
    print(f"[DEBUG] Vehicle coordinates: lat={vehicle.current_latitude}, lng={vehicle.current_longitude}")
    
    # Get all commuters
    commuters = User.query.filter_by(user_type='commuter').all()
    print(f"[DEBUG] Found {len(commuters)} commuters in total")
    
    notifications_sent = 0
    
    for commuter in commuters:
        if not commuter.current_latitude or not commuter.current_longitude:
            print(f"[DEBUG] Skipping commuter {commuter.id} due to missing location data: lat={commuter.current_latitude}, lng={commuter.current_longitude}")
            continue
            
        print(f"[DEBUG] Commuter {commuter.id} coordinates: lat={commuter.current_latitude}, lng={commuter.current_longitude}")
        
        # Get commuter's notification settings
        settings = NotificationSetting.query.filter_by(user_id=commuter.id).first()
        if not settings:
            # Create default settings if they don't exist
            settings = NotificationSetting(
                user_id=commuter.id,
                enabled=True,
                notification_radius=500,
                notification_cooldown=60
            )
            db.session.add(settings)
            db.session.commit()
            print(f"[DEBUG] Created default notification settings for commuter {commuter.id}")
        
        if not settings.enabled:
            print(f"[DEBUG] Skipping commuter {commuter.id}: Notifications disabled")
            continue
            
        # Skip if commuter only wants notifications for specific routes
        if settings.notify_specific_routes and settings.routes:
            if not vehicle.route or str(vehicle.route) not in settings.routes:
                print(f"[DEBUG] Skipping commuter {commuter.id} as they don't subscribe to route {vehicle.route}")
                continue
        
        # Calculate distance
        try:
            distance = haversine_distance(
                commuter.current_latitude, commuter.current_longitude,
                vehicle.current_latitude, vehicle.current_longitude
            )
            
            print(f"[DEBUG] Distance between commuter {commuter.id} and vehicle {vehicle.id}: {distance:.2f}m (radius: {settings.notification_radius}m)")
            
            # If within radius, create and send notification
            if distance <= settings.notification_radius:
                # Check cooldown for this specific commuter
                if check_notification_cooldown(commuter.id, 'vehicle_approaching'):
                    # Calculate ETA (rough estimate: assume 30km/h average speed)
                    eta_minutes = max(1, int((distance / 1000) * 2))  # 2 minutes per kilometer, minimum 1 minute
                    
                    print(f"[DEBUG] Creating notification for commuter {commuter.id} about vehicle {vehicle.id}")
                    
                    notification = Notification(
                        user_id=commuter.id,
                        type='vehicle_approaching',
                        title=f'{vehicle.vehicle_type.title()} Approaching',
                        message=f'A {vehicle.vehicle_type} on route {vehicle.route} is {int(distance)}m away. '
                               f'ETA: ~{eta_minutes} minutes',
                        data={
                            'vehicle_id': vehicle.id,
                            'vehicle_type': vehicle.vehicle_type,
                            'route': vehicle.route,
                            'distance': distance,
                            'eta_minutes': eta_minutes,
                            'location': {
                                'lat': vehicle.current_latitude,
                                'lng': vehicle.current_longitude
                            }
                        }
                    )
                    
                    db.session.add(notification)
                    settings.last_notification_time = datetime.utcnow()
                    db.session.commit()
                    
                    # Emit via WebSocket
                    print(f"[DEBUG] Emitting notification to room: user_{commuter.id}")
                    emit('notification', notification.to_dict(), room=f'user_{commuter.id}', namespace='/')
                    
                    # Also emit a vehicle_approaching event for direct handling
                    emit('vehicle_approaching', {
                        'vehicle_id': vehicle.id,
                        'vehicle_type': vehicle.vehicle_type,
                        'registration_number': vehicle.registration_number,
                        'route': vehicle.route,
                        'distance': int(distance),
                        'eta': eta_minutes
                    }, room=f'user_{commuter.id}', namespace='/')
                    
                    notifications_sent += 1
                else:
                    print(f"[DEBUG] Skipping commuter {commuter.id} due to cooldown")
        except Exception as e:
            print(f"[ERROR] Error calculating distance or sending notification to commuter {commuter.id}: {str(e)}")
    
    print(f"[DEBUG] Notify_nearby_commuters complete. Sent {notifications_sent} notifications.")

def notify_route_subscribers(vehicle):
    """Notify commuters who are subscribed to this route."""
    # Get all commuters subscribed to this route
    route_subscribers = NotificationSetting.query.join(NotificationSetting.user)\
        .filter(
            NotificationSetting.enabled == True,
            NotificationSetting.notify_specific_routes == True,
            NotificationSetting.routes.contains(str(vehicle.route))
        ).all()
    
    for settings in route_subscribers:
        # Skip if notification cooldown hasn't elapsed
        if not check_notification_cooldown(settings.user_id):
            continue
        
        commuter = settings.user
        if not commuter.current_latitude or not commuter.current_longitude:
            continue
        
        # Calculate distance
        distance = haversine_distance(
            commuter.current_latitude, commuter.current_longitude,
            vehicle.current_latitude, vehicle.current_longitude
        )
        
        # Create route update notification
        notification = Notification(
            user_id=commuter.id,
            type='route_update',
            title=f'Route {vehicle.route} Update',
            message=f'A {vehicle.vehicle_type} on your subscribed route is {int(distance/1000)}km away.',
            data={
                'vehicle_id': vehicle.id,
                'vehicle_type': vehicle.vehicle_type,
                'route': vehicle.route,
                'distance': distance,
                'location': {
                    'lat': vehicle.current_latitude,
                    'lng': vehicle.current_longitude
                }
            }
        )
        
        db.session.add(notification)
        settings.last_notification_time = datetime.utcnow()
        db.session.commit()
        
        # Emit via WebSocket
        emit('notification', notification.to_dict(), room=f'user_{commuter.id}')

def handle_commuter_location(data):
    """Handle commuter location updates and notify nearby operators."""
    print(f"[DEBUG] Received commuter location update: {data}")
    
    if not current_user.is_authenticated or current_user.user_type != 'commuter':
        print("[DEBUG] Ignoring location update: User not authenticated or not a commuter")
        return
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    
    if not all([latitude, longitude]):
        print("[DEBUG] Ignoring location update: Missing latitude or longitude")
        return
    
    print(f"[DEBUG] Updating location for commuter {current_user.id}: lat={latitude}, lng={longitude}, accuracy={accuracy}")
    
    # Update commuter location
    current_user.current_latitude = float(latitude)
    current_user.current_longitude = float(longitude)
    if accuracy:
        current_user.accuracy = float(accuracy)
    db.session.commit()
    
    # Get nearby active vehicles
    vehicles = Vehicle.query.filter_by(status='active').all()
    print(f"[DEBUG] Found {len(vehicles)} active vehicles to check for proximity")
    
    # Get commuter's notification settings
    commuter_settings = NotificationSetting.query.filter_by(user_id=current_user.id).first()
    if not commuter_settings:
        # Create default settings if they don't exist
        commuter_settings = NotificationSetting(
            user_id=current_user.id,
            enabled=True,
            notification_radius=500,
            notification_cooldown=60
        )
        db.session.add(commuter_settings)
        db.session.commit()
        print(f"[DEBUG] Created default notification settings for commuter {current_user.id}")
    
    if commuter_settings.enabled:
        # Check for nearby vehicles to notify the commuter
        for vehicle in vehicles:
            if not vehicle.current_latitude or not vehicle.current_longitude:
                print(f"[DEBUG] Skipping vehicle {vehicle.id} due to missing location data: lat={vehicle.current_latitude}, lng={vehicle.current_longitude}")
                continue
            
            print(f"[DEBUG] Vehicle {vehicle.id} coordinates: lat={vehicle.current_latitude}, lng={vehicle.current_longitude}")
            
            try:
                # Calculate distance
                distance = haversine_distance(
                    float(latitude), float(longitude),
                    vehicle.current_latitude, vehicle.current_longitude
                )
                
                print(f"[DEBUG] Distance between commuter {current_user.id} and vehicle {vehicle.id}: {distance:.2f}m (radius: {commuter_settings.notification_radius}m)")
                
                # If within radius, create and send notification to commuter
                if distance <= commuter_settings.notification_radius:
                    if check_notification_cooldown(current_user.id, 'vehicle_approaching'):
                        # Calculate ETA (rough estimate: assume 30km/h average speed)
                        eta_minutes = max(1, int((distance / 1000) * 2))  # 2 minutes per kilometer, minimum 1 minute
                        
                        print(f"[DEBUG] Creating notification for commuter {current_user.id} about vehicle {vehicle.id}")
                        
                        notification = Notification(
                            user_id=current_user.id,
                            type='vehicle_approaching',
                            title=f'{vehicle.vehicle_type.title()} Approaching',
                            message=f'A {vehicle.vehicle_type} on route {vehicle.route} is {int(distance)}m away. '
                                   f'ETA: ~{eta_minutes} minutes',
                            data={
                                'vehicle_id': vehicle.id,
                                'vehicle_type': vehicle.vehicle_type,
                                'route': vehicle.route,
                                'distance': distance,
                                'eta_minutes': eta_minutes,
                                'location': {
                                    'lat': vehicle.current_latitude,
                                    'lng': vehicle.current_longitude
                                }
                            }
                        )
                        
                        db.session.add(notification)
                        commuter_settings.last_notification_time = datetime.utcnow()
                        db.session.commit()
                        
                        # Emit via WebSocket
                        print(f"[DEBUG] Emitting notification to room: user_{current_user.id}")
                        emit('notification', notification.to_dict(), room=f'user_{current_user.id}', namespace='/')
                        
                        # Also emit a vehicle_approaching event for direct handling
                        emit('vehicle_approaching', {
                            'vehicle_id': vehicle.id,
                            'vehicle_type': vehicle.vehicle_type,
                            'registration_number': vehicle.registration_number,
                            'route': vehicle.route,
                            'distance': int(distance),
                            'eta': eta_minutes
                        }, room=f'user_{current_user.id}', namespace='/')
                    else:
                        print(f"[DEBUG] Skipping notification for commuter {current_user.id} due to cooldown")
            except Exception as e:
                print(f"[ERROR] Error calculating distance or sending notification to commuter {current_user.id}: {str(e)}")
    
    # Now check for operators to notify about this commuter
    for vehicle in vehicles:
        if not vehicle.current_latitude or not vehicle.current_longitude:
            print(f"[DEBUG] Skipping vehicle {vehicle.id} due to missing location data: lat={vehicle.current_latitude}, lng={vehicle.current_longitude}")
            continue
        
        print(f"[DEBUG] Vehicle {vehicle.id} coordinates: lat={vehicle.current_latitude}, lng={vehicle.current_longitude}")
        
        try:
            # Calculate distance
            distance = haversine_distance(
                float(latitude), float(longitude),
                vehicle.current_latitude, vehicle.current_longitude
            )
            
            print(f"[DEBUG] Distance between commuter {current_user.id} and vehicle {vehicle.id}: {distance:.2f}m")
            
            # Get operator's notification settings
            settings = NotificationSetting.query.filter_by(user_id=vehicle.owner_id).first()
            if not settings:
                # Create default settings if they don't exist
                settings = NotificationSetting(
                    user_id=vehicle.owner_id,
                    enabled=True,
                    notification_radius=500,
                    notification_cooldown=60
                )
                db.session.add(settings)
                db.session.commit()
                print(f"[DEBUG] Created default notification settings for operator {vehicle.owner_id}")
            
            if not settings.enabled:
                print(f"[DEBUG] Skipping vehicle {vehicle.id}: Operator {vehicle.owner_id} has notifications disabled")
                continue
            
            # Check if within notification radius and cooldown period
            if distance <= settings.notification_radius:
                print(f"[DEBUG] Vehicle {vehicle.id} is within notification radius ({settings.notification_radius}m)")
                
                if check_notification_cooldown(vehicle.owner_id, 'nearby_commuter'):
                    print(f"[DEBUG] Creating notification for operator {vehicle.owner_id} about nearby commuter")
                    
                    notification = Notification(
                        user_id=vehicle.owner_id,
                        type='nearby_commuter',
                        title='Commuter Nearby',
                        message=f'A commuter is {int(distance)}m away from your vehicle.',
                        data={
                            'distance': distance,
                            'location': {
                                'lat': latitude,
                                'lng': longitude
                            }
                        }
                    )
                    
                    db.session.add(notification)
                    settings.last_notification_time = datetime.utcnow()
                    db.session.commit()
                    
                    # Emit via WebSocket
                    print(f"[DEBUG] Emitting notification to room: user_{vehicle.owner_id}")
                    emit('nearby_commuter', {
                        'distance': int(distance),
                        'location': f"({float(latitude):.6f}, {float(longitude):.6f})"
                    }, room=f'user_{vehicle.owner_id}', namespace='/')
                    emit('notification', notification.to_dict(), room=f'user_{vehicle.owner_id}', namespace='/')
                else:
                    print(f"[DEBUG] Skipping notification for operator {vehicle.owner_id} due to cooldown")
        except Exception as e:
            print(f"[ERROR] Error calculating distance or sending notification to operator {vehicle.owner_id}: {str(e)}")

def force_notify_commuter(commuter_id, vehicle_id):
    """Force a notification to be sent to a commuter about a nearby vehicle.
    This function bypasses the cooldown check for testing purposes.
    """
    commuter = User.query.get(commuter_id)
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not commuter or not vehicle:
        print(f"[DEBUG] Commuter {commuter_id} or Vehicle {vehicle_id} not found")
        return
    
    if not vehicle.current_latitude or not vehicle.current_longitude or not commuter.current_latitude or not commuter.current_longitude:
        print(f"[DEBUG] Missing location data for commuter or vehicle")
        return
    
    # Calculate distance
    distance = haversine_distance(
        commuter.current_latitude, commuter.current_longitude,
        vehicle.current_latitude, vehicle.current_longitude
    )
    
    # Calculate ETA (rough estimate: assume 30km/h average speed)
    eta_minutes = max(1, int((distance / 1000) * 2))  # 2 minutes per kilometer, minimum 1 minute
    
    print(f"[DEBUG] Forcing notification for commuter {commuter_id} about vehicle {vehicle_id}")
    
    notification = Notification(
        user_id=commuter_id,
        type='vehicle_approaching',
        title=f'{vehicle.vehicle_type.title()} Approaching',
        message=f'A {vehicle.vehicle_type} on route {vehicle.route} is {int(distance)}m away. '
               f'ETA: ~{eta_minutes} minutes',
        data={
            'vehicle_id': vehicle.id,
            'vehicle_type': vehicle.vehicle_type,
            'route': vehicle.route,
            'distance': distance,
            'eta_minutes': eta_minutes,
            'location': {
                'lat': vehicle.current_latitude,
                'lng': vehicle.current_longitude
            }
        }
    )
    
    db.session.add(notification)
    db.session.commit()
    
    # Emit via WebSocket
    print(f"[DEBUG] Emitting forced notification to room: user_{commuter_id}")
    emit('notification', notification.to_dict(), room=f'user_{commuter_id}', namespace='/')
    
    # Also emit a vehicle_approaching event for direct handling
    emit('vehicle_approaching', {
        'vehicle_id': vehicle.id,
        'vehicle_type': vehicle.vehicle_type,
        'registration_number': vehicle.registration_number,
        'route': vehicle.route,
        'distance': int(distance),
        'eta': eta_minutes
    }, room=f'user_{commuter_id}', namespace='/') 