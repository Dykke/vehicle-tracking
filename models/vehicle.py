"""
Vehicle model for the Drive Monitoring System
"""
from models import db
from datetime import datetime
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.dialects.postgresql import TEXT as PG_TEXT

class Vehicle(db.Model):
    """Vehicle model for storing vehicle information"""
    
    __tablename__ = 'vehicles'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Location tracking fields
    occupancy_status = db.Column(db.String(20), default='empty')
    last_speed_kmh = db.Column(db.Float, default=0.0)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Route and accuracy fields
    accuracy = db.Column(db.Float, default=0.0)
    route = db.Column(db.String(100))
    route_info = db.Column(db.Text)
    
    # Relationship fields
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_driver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_vehicles')
    assigned_driver = db.relationship('User', foreign_keys=[assigned_driver_id], backref='assigned_vehicle')
    
    # Location logs relationship
    location_logs = db.relationship('LocationLog', backref='vehicle', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vehicle {self.registration_number}>'
    
    def to_dict(self):
        """Convert vehicle to dictionary"""
        return {
            'id': self.id,
            'registration_number': self.registration_number,
            'vehicle_type': self.vehicle_type,
            'capacity': self.capacity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'occupancy_status': self.occupancy_status,
            'last_speed_kmh': self.last_speed_kmh,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'accuracy': self.accuracy,
            'route': self.route,
            'route_info': self.route_info,
            'owner_id': self.owner_id,
            'assigned_driver_id': self.assigned_driver_id
        }
    
    def update_location(self, latitude, longitude, speed=None, accuracy=None):
        """Update vehicle location"""
        self.current_latitude = latitude
        self.current_longitude = longitude
        self.last_updated = datetime.utcnow()
        
        if speed is not None:
            self.last_speed_kmh = speed
        
        if accuracy is not None:
            self.accuracy = accuracy
        
        db.session.commit()
    
    def assign_driver(self, driver_id):
        """Assign a driver to this vehicle"""
        self.assigned_driver_id = driver_id
        db.session.commit()
    
    def unassign_driver(self):
        """Unassign the current driver"""
        self.assigned_driver_id = None
        db.session.commit()
    
    @staticmethod
    def get_active_vehicles():
        """Get all active vehicles"""
        return Vehicle.query.filter_by(status='active').all()
    
    @staticmethod
    def get_vehicle_by_registration(registration_number):
        """Get vehicle by registration number"""
        return Vehicle.query.filter_by(registration_number=registration_number).first()
    
    @staticmethod
    def get_vehicles_by_owner(owner_id):
        """Get vehicles owned by a specific user"""
        return Vehicle.query.filter_by(owner_id=owner_id).all()
    
    @staticmethod
    def get_vehicles_by_driver(driver_id):
        """Get vehicles assigned to a specific driver"""
        return Vehicle.query.filter_by(assigned_driver_id=driver_id).all()
