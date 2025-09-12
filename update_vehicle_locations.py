#!/usr/bin/env python

"""
Update Vehicle Locations Script

This script ensures all active/delayed vehicles have coordinates by updating
their location information from their most recent location logs if needed.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import desc
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask app."""
    from models import db
    app = Flask(__name__)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set!")
        sys.exit(1)
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def update_vehicle_locations(app):
    """Update vehicle locations from their most recent location logs."""
    from models.user import Vehicle, LocationLog
    from models import db
    
    with app.app_context():
        # Get all active/delayed vehicles without coordinates
        vehicles_missing_coords = Vehicle.query.filter(
            Vehicle.status.in_(['active', 'delayed']),
            (Vehicle.current_latitude.is_(None) | Vehicle.current_longitude.is_(None))
        ).all()
        
        logger.info(f"Found {len(vehicles_missing_coords)} active/delayed vehicles without coordinates")
        
        updated_count = 0
        for vehicle in vehicles_missing_coords:
            # Find most recent location log for this vehicle
            latest_log = LocationLog.query.filter_by(vehicle_id=vehicle.id).order_by(desc(LocationLog.timestamp)).first()
            
            if latest_log:
                logger.info(f"Updating vehicle #{vehicle.id} ({vehicle.registration_number}) with coordinates "
                           f"from log #{latest_log.id}: ({latest_log.latitude}, {latest_log.longitude})")
                
                # Update vehicle coordinates
                vehicle.current_latitude = latest_log.latitude
                vehicle.current_longitude = latest_log.longitude
                vehicle.accuracy = latest_log.accuracy
                vehicle.last_updated = datetime.utcnow()
                
                updated_count += 1
            else:
                logger.warning(f"No location logs found for vehicle #{vehicle.id}")
        
        if updated_count > 0:
            db.session.commit()
            logger.info(f"Successfully updated {updated_count} vehicles with coordinates from location logs")
        else:
            logger.info("No vehicles were updated")
        
        # Now check all active/delayed vehicles to ensure they have proper coordinates
        all_active = Vehicle.query.filter(
            Vehicle.status.in_(['active', 'delayed'])
        ).all()
        
        for vehicle in all_active:
            if not vehicle.current_latitude or not vehicle.current_longitude:
                logger.warning(f"Vehicle #{vehicle.id} still missing coordinates after update attempt")
            else:
                logger.info(f"Vehicle #{vehicle.id} has coordinates: ({vehicle.current_latitude}, {vehicle.current_longitude})")

def main():
    """Run the script."""
    app = create_app()
    update_vehicle_locations(app)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 