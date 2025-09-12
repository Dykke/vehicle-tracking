from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db
import json

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin', 'operator', 'driver'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for 55% scope
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    profile_image_url = db.Column(db.String(500), nullable=True)
    
    # Added for role management
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For drivers created by operators
    created_by = db.relationship('User', remote_side=[id], backref='created_users')
    
    # Location data
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)  # accuracy in meters
    
    # Profile fields
    company_name = db.Column(db.String(200), nullable=True)
    contact_number = db.Column(db.String(50), nullable=True)
    
    # Relationships - modified to avoid backref conflicts
    # Note: vehicles relationship removed due to ambiguous foreign keys
    # Use specific relationships: owned_vehicles (via owner_id) and assigned_vehicles (via assigned_driver_id)
    notifications = db.relationship('Notification', backref=db.backref('user_backref', uselist=False), lazy='dynamic')
    notification_settings = db.relationship('NotificationSetting', backref=db.backref('user_backref', uselist=False), uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
            'accuracy': self.accuracy,
            'is_active': self.is_active,
            'profile_image_url': self.profile_image_url,
            'company_name': self.company_name,
            'contact_number': self.contact_number
        }

# Vehicle model moved to models/vehicle.py to avoid conflicts

# LocationLog model moved to models/location_log.py to avoid conflicts

# New models for 55% scope
class DriverActionLog(db.Model):
    __tablename__ = 'driver_action_logs'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # 'occupancy_change', 'route_start', 'route_abort', etc.
    meta_data = db.Column(db.JSON, nullable=True)  # Additional data like old_value, new_value, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    driver = db.relationship('User', backref=db.backref('action_logs', lazy=True))
    vehicle = db.relationship('Vehicle', backref=db.backref('action_logs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'vehicle_id': self.vehicle_id,
            'action': self.action,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OperatorActionLog(db.Model):
    __tablename__ = 'operator_action_logs'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'driver_created', 'vehicle_added', 'settings_updated', etc.
    target_type = db.Column(db.String(50), nullable=True)  # 'driver', 'vehicle', 'system', etc.
    target_id = db.Column(db.Integer, nullable=True)  # ID of the target (driver_id, vehicle_id, etc.)
    meta_data = db.Column(db.JSON, nullable=True)  # Additional data like old_value, new_value, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    operator = db.relationship('User', backref=db.backref('operator_action_logs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'operator_id': self.operator_id,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Trip(db.Model):
    __tablename__ = 'trips'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_name = db.Column(db.String(255), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehicle = db.relationship('Vehicle', backref=db.backref('trips', lazy=True))
    driver = db.relationship('User', backref=db.backref('trips', lazy=True))
    passenger_events = db.relationship('PassengerEvent', backref='trip', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'route_name': self.route_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PassengerEvent(db.Model):
    __tablename__ = 'passenger_events'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # 'board', 'alight'
    count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'event_type': self.event_type,
            'count': self.count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        } 