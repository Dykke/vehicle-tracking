from datetime import datetime
from . import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'nearby_commuter', 'vehicle_approaching', etc.
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # JSONB is preferred in PostgreSQL for performance
    data = db.Column(db.JSON, nullable=True)  # For storing additional data like coordinates, vehicle info, etc.
    status = db.Column(db.String(20), default='unread')  # 'unread', 'read'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Updated relationship name to avoid conflicts with backref in User model
    # Relationship is now defined by backref in User model as 'user_backref'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class NotificationSetting(db.Model):
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    enabled = db.Column(db.Boolean, default=True)
    notification_radius = db.Column(db.Float, default=500)  # in meters
    notify_specific_routes = db.Column(db.Boolean, default=False)
    # JSONB is preferred in PostgreSQL for performance
    routes = db.Column(db.JSON, nullable=True)  # List of route IDs to notify for
    notification_cooldown = db.Column(db.Integer, default=300)  # in seconds
    last_notification_time = db.Column(db.DateTime, nullable=True)
    
    # Updated relationship name to avoid conflicts with backref in User model
    # Relationship is now defined by backref in User model as 'user_backref'
    
    def to_dict(self):
        return {
            'enabled': self.enabled,
            'notification_radius': self.notification_radius,
            'notify_specific_routes': self.notify_specific_routes,
            'routes': self.routes,
            'notification_cooldown': self.notification_cooldown
        } 