#!/usr/bin/env python

"""
Force Set Vehicles Active Script

This script finds all vehicles with valid coordinates and sets their status to 'active',
helping ensure that vehicles appear on the commuter dashboard.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from datetime import datetime

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

def set_vehicles_active(app):
    """Set all vehicles with coordinates to active status."""
    from models.user import Vehicle
    from models import db
    
    with app.app_context():
        # Find all vehicles that have coordinates
        vehicles_with_coords = Vehicle.query.filter(
            Vehicle.current_latitude.isnot(None),
            Vehicle.current_longitude.isnot(None)
        ).all()
        
        logger.info(f"Found {len(vehicles_with_coords)} vehicles with coordinates")
        
        activated_count = 0
        for vehicle in vehicles_with_coords:
            logger.info(f"Vehicle #{vehicle.id} ({vehicle.registration_number}): "
                       f"Status before = {vehicle.status}, "
                       f"Coords = ({vehicle.current_latitude}, {vehicle.current_longitude})")
            
            # Set to active status and update timestamp
            if vehicle.status != 'active':
                vehicle.status = 'active'
                vehicle.last_updated = datetime.utcnow()
                activated_count += 1
                logger.info(f"  → Updated to active status")
            else:
                logger.info(f"  → Already active, no change needed")
        
        if activated_count > 0:
            db.session.commit()
            logger.info(f"Successfully set {activated_count} vehicles to active status")
        else:
            logger.info("No vehicles needed status update")
        
        # Now list all active vehicles
        active_vehicles = Vehicle.query.filter_by(status='active').all()
        logger.info(f"Total active vehicles after update: {len(active_vehicles)}")
        for v in active_vehicles:
            logger.info(f"Active vehicle #{v.id}: {v.registration_number}, "
                       f"Coords = ({v.current_latitude}, {v.current_longitude}), "
                       f"Last updated = {v.last_updated}")

def main():
    """Run the script."""
    app = create_app()
    set_vehicles_active(app)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 