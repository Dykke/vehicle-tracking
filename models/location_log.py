"""
Location Log model for tracking vehicle locations
"""
from models import db
from datetime import datetime

class LocationLog(db.Model):
    """Location log for tracking vehicle movements"""
    
    __tablename__ = 'location_logs'
    __table_args__ = {'extend_existing': True}  # Handle existing table
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed_kmh = db.Column(db.Float, default=0.0)
    accuracy = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional tracking data
    heading = db.Column(db.Float)  # Direction in degrees
    altitude = db.Column(db.Float)  # Altitude in meters
    route_info = db.Column(db.Text)  # Route information
    
    def __repr__(self):
        return f'<LocationLog {self.vehicle_id} at {self.timestamp}>'
    
    def to_dict(self):
        """Convert location log to dictionary"""
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed_kmh': self.speed_kmh,
            'accuracy': self.accuracy,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'heading': self.heading,
            'altitude': self.altitude,
            'route_info': self.route_info
        }
    
    @staticmethod
    def get_vehicle_locations(vehicle_id, limit=100):
        """Get recent location logs for a vehicle"""
        return LocationLog.query.filter_by(vehicle_id=vehicle_id)\
                               .order_by(LocationLog.timestamp.desc())\
                               .limit(limit).all()
    
    @staticmethod
    def get_locations_in_timeframe(vehicle_id, start_time, end_time):
        """Get location logs for a vehicle within a time frame"""
        return LocationLog.query.filter_by(vehicle_id=vehicle_id)\
                               .filter(LocationLog.timestamp.between(start_time, end_time))\
                               .order_by(LocationLog.timestamp.asc()).all()
    
    @staticmethod
    def get_latest_location(vehicle_id):
        """Get the most recent location for a vehicle"""
        return LocationLog.query.filter_by(vehicle_id=vehicle_id)\
                               .order_by(LocationLog.timestamp.desc())\
                               .first()
