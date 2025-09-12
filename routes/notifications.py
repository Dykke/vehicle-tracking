from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from models.vehicle import Vehicle

# Create a blueprint that matches the import in app.py
notifications_bp = Blueprint('notifications', __name__)

# Keep the original notification_bp for compatibility with existing code
notification_bp = Blueprint('notification', __name__)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on Earth using the Haversine formula."""
    # Validate inputs
    try:
        lat1, lon1 = float(lat1), float(lon1)
        lat2, lon2 = float(lat2), float(lon2)
    except (TypeError, ValueError):
        print(f"[ERROR] Invalid coordinates in haversine_distance: lat1={lat1}, lon1={lon1}, lat2={lat2}, lon2={lon2}")
        return float('inf')  # Return infinity for invalid coordinates
    
    # Check for valid coordinate ranges
    if not (-90 <= lat1 <= 90 and -180 <= lon1 <= 180 and -90 <= lat2 <= 90 and -180 <= lon2 <= 180):
        print(f"[ERROR] Coordinates out of range in haversine_distance: lat1={lat1}, lon1={lon1}, lat2={lat2}, lon2={lon2}")
        return float('inf')
    
    R = 6371000  # Earth's radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def check_notification_cooldown(user_id, notification_type=None):
    """Check if enough time has passed since the last notification.
    
    Args:
        user_id: The ID of the user to check cooldown for
        notification_type: Optional type of notification to use different cooldowns
    """
    settings = NotificationSetting.query.filter_by(user_id=user_id).first()
    if not settings:
        # Create default settings if they don't exist
        settings = NotificationSetting(
            user_id=user_id,
            enabled=True,
            notification_radius=500,
            notification_cooldown=60
        )
        db.session.add(settings)
        db.session.commit()
        return True
        
    if not settings.last_notification_time:
        return True
    
    # Use different cooldowns based on notification type
    if notification_type == 'vehicle_approaching':
        # For commuters receiving vehicle notifications
        cooldown = 15  # 15 seconds
    elif notification_type == 'nearby_commuter':
        # For operators receiving commuter notifications
        cooldown = 15  # 15 seconds
    elif notification_type == 'manual_refresh':
        # For manual refresh button, use a shorter cooldown
        cooldown = 5  # 5 seconds
    else:
        # For other notifications, use the setting from the database
        cooldown = settings.notification_cooldown or 60  # Default 60 seconds
        
    elapsed = datetime.utcnow() - settings.last_notification_time
    print(f"[DEBUG] Notification cooldown check for user {user_id}, type {notification_type}: elapsed={elapsed.total_seconds()}s, cooldown={cooldown}s")
    return elapsed.total_seconds() > cooldown

@notifications_bp.route('/notifications')
@login_required
def get_notifications():
    """Get all notifications for the current user."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Placeholder implementation until Notification model is fully integrated
    return jsonify({
        'notifications': [],
        'total': 0,
        'pages': 0,
        'current_page': page
    })

@notification_bp.route('/notifications/unread')
@login_required
def get_unread_count():
    """Get the count of unread notifications."""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        status='unread'
    ).count()
    
    return jsonify({'unread_count': count})

@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """Mark a notification as read."""
    # Placeholder implementation until Notification model is fully integrated
    return jsonify({'message': 'Notification marked as read'})

@notification_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_as_read():
    """Mark all notifications as read."""
    Notification.query.filter_by(
        user_id=current_user.id,
        status='unread'
    ).update({'status': 'read'})
    
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'})

@notification_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """Delete a notification."""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification deleted'})

@notification_bp.route('/notifications/clear-all', methods=['DELETE'])
@login_required
def clear_all_notifications():
    """Delete all notifications for the current user."""
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({'message': 'All notifications cleared'})

@notification_bp.route('/notifications/trigger-detection', methods=['POST'])
@login_required
def trigger_notification_detection():
    """Trigger the notification detection process for the current user."""
    user_id = current_user.id
    user_type = current_user.user_type
    
    # Check cooldown to prevent spam
    if not check_notification_cooldown(user_id, 'manual_refresh'):
        return jsonify({'message': 'Please wait before refreshing again'}), 429
    
    try:
        # For commuters, check for nearby vehicles
        if user_type == 'commuter':
            from services.location_service import check_nearby_vehicles
            user_location = current_user.get_current_location()
            if user_location:
                check_nearby_vehicles(user_id, user_location.latitude, user_location.longitude)
        
        # For operators, check for nearby commuters
        elif user_type == 'operator':
            from services.location_service import check_nearby_commuters
            # Get all active vehicles for this operator
            vehicles = Vehicle.query.filter_by(owner_id=user_id, status='active').all()
            for vehicle in vehicles:
                if vehicle.current_location:
                    check_nearby_commuters(vehicle.id, vehicle.current_location.latitude, vehicle.current_location.longitude)
        
        return jsonify({'message': 'Notification detection triggered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notification-settings', methods=['GET', 'PUT'])
@login_required
def notification_settings():
    """Get or update notification settings."""
    settings = NotificationSetting.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'GET':
        if not settings:
            settings = NotificationSetting(user_id=current_user.id)
            db.session.add(settings)
            db.session.commit()
        return jsonify(settings.to_dict())
    
    # Update settings
    if not settings:
        settings = NotificationSetting(user_id=current_user.id)
        db.session.add(settings)
    
    data = request.get_json()
    
    if 'enabled' in data:
        settings.enabled = data['enabled']
    if 'notification_radius' in data:
        settings.notification_radius = data['notification_radius']
    if 'notify_specific_routes' in data:
        settings.notify_specific_routes = data['notify_specific_routes']
    if 'routes' in data:
        settings.routes = data['routes']
    if 'notification_cooldown' in data:
        settings.notification_cooldown = data['notification_cooldown']
    
    db.session.commit()
    return jsonify(settings.to_dict())

@notification_bp.route('/force-notify/<int:commuter_id>/<int:vehicle_id>')
@login_required
def force_notify(commuter_id, vehicle_id):
    """Force a notification to be sent to a commuter about a nearby vehicle."""
    from events import force_notify_commuter
    
    # Only allow operators or admins to force notifications
    if current_user.user_type not in ['operator', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    force_notify_commuter(commuter_id, vehicle_id)
    return jsonify({'success': True, 'message': f'Notification sent to commuter {commuter_id} about vehicle {vehicle_id}'}) 