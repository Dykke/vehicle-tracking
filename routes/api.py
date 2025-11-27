from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from models.vehicle import Vehicle
from models.location_log import LocationLog
from models.user import Trip, PassengerEvent
from models import db
from datetime import datetime
from sqlalchemy import func
import json

api_bp = Blueprint('api', __name__)

def _build_vehicle_response(vehicle):
    """Helper to include passenger summary information with a vehicle."""
    data = vehicle.to_dict()
    summary = _get_vehicle_passenger_summary(vehicle.id)
    data['passenger_summary'] = summary
    data['capacity'] = vehicle.capacity or 15  # Default to 15 if not set
    return data


def _get_vehicle_passenger_summary(vehicle_id):
    """Return passenger summary for the vehicle's active trip."""
    active_trip = Trip.query.filter_by(
        vehicle_id=vehicle_id,
        status='active'
    ).first()
    
    if not active_trip:
        return {
            'trip_id': None,
            'current_passengers': 0,
            'boards': 0,
            'alights': 0
        }
    
    boards = (
        db.session.query(func.coalesce(func.sum(PassengerEvent.count), 0))
        .filter_by(trip_id=active_trip.id, event_type='board')
        .scalar() or 0
    )
    
    alights = (
        db.session.query(func.coalesce(func.sum(PassengerEvent.count), 0))
        .filter_by(trip_id=active_trip.id, event_type='alight')
        .scalar() or 0
    )
    
    current = max(0, boards - alights)
    
    return {
        'trip_id': active_trip.id,
        'current_passengers': current,
        'boards': boards,
        'alights': alights
    }


@api_bp.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
@login_required
def get_vehicle(vehicle_id):
    """Get vehicle details by ID."""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Check if user owns this vehicle or is admin
        if current_user.user_type != 'admin' and vehicle.owner_id != current_user.id:
            return jsonify({'error': 'Unauthorized to access this vehicle'}), 403
        
        return jsonify({
            'success': True,
            'vehicle': _build_vehicle_response(vehicle)
        })
        
    except Exception as e:
        current_app.logger.error(f'Error getting vehicle: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/api/vehicles/operator', methods=['GET'])
@login_required
def get_operator_vehicles():
    """Get all vehicles owned by the current operator."""
    try:
        if current_user.user_type not in ['admin', 'operator']:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        # Get all vehicles owned by the current operator
        vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
        
        vehicle_payload = [_build_vehicle_response(v) for v in vehicles]
        
        return jsonify({
            'success': True,
            'vehicles': vehicle_payload,
            'count': len(vehicle_payload)
        })
        
    except Exception as e:
        current_app.logger.error(f'Error getting operator vehicles: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/api/vehicles/active', methods=['GET'])
def get_active_vehicles():
    """Get all active vehicles."""
    try:
        # Get all active vehicles
        active_vehicles = Vehicle.query.filter(
            Vehicle.status.in_(['active', 'delayed']),
            Vehicle.current_latitude.isnot(None),
            Vehicle.current_longitude.isnot(None)
        ).all()
        
        vehicle_payload = [_build_vehicle_response(v) for v in active_vehicles]
        
        return jsonify({
            'success': True,
            'vehicles': vehicle_payload,
            'count': len(vehicle_payload)
        })
        
    except Exception as e:
        current_app.logger.error(f'Error getting active vehicles: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/api/vehicles/<int:vehicle_id>/route', methods=['POST'])
@login_required
def update_vehicle_route(vehicle_id):
    """Update a vehicle's route."""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Check if user owns this vehicle or is admin
        if current_user.user_type != 'admin' and vehicle.owner_id != current_user.id:
            return jsonify({'error': 'Unauthorized to modify this vehicle'}), 403
        
        data = request.get_json()
        route = data.get('route')
        
        if not route:
            return jsonify({'error': 'Route is required'}), 400
        
        # Create route_info object if route follows "A to B" format
        route_info = None
        if ' to ' in route:
            route_parts = route.split(' to ')
            if len(route_parts) == 2:
                route_info = {
                    "route_name": route,
                    "origin": route_parts[0],
                    "destination": route_parts[1]
                }
        
        # Update vehicle route
        vehicle.route = route
        vehicle.route_info = route_info
        
        # Log the action if DriverActionLog is available
        try:
            from models.user import DriverActionLog
            action_log = DriverActionLog(
                driver_id=current_user.id,
                vehicle_id=vehicle_id,
                action='route_start',
                meta_data={
                    'route': route,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(action_log)
        except ImportError:
            # DriverActionLog not available, skip logging
            pass
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Route updated successfully',
            'route': route,
            'route_info': route_info
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating route: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/api/vehicles/<int:vehicle_id>/route', methods=['DELETE'])
@login_required
def delete_vehicle_route(vehicle_id):
    """Delete a vehicle's route (abort route)."""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Check if user owns this vehicle or is admin
        if current_user.user_type != 'admin' and vehicle.owner_id != current_user.id:
            return jsonify({'error': 'Unauthorized to modify this vehicle'}), 403
        
        # Store old route for logging
        old_route = vehicle.route
        
        # Clear vehicle route
        vehicle.route = None
        vehicle.route_info = None
        
        # Log the action if DriverActionLog is available
        try:
            from models.user import DriverActionLog
            action_log = DriverActionLog(
                driver_id=current_user.id,
                vehicle_id=vehicle_id,
                action='route_abort',
                meta_data={
                    'old_route': old_route,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            db.session.add(action_log)
        except ImportError:
            # DriverActionLog not available, skip logging
            pass
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Route aborted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error aborting route: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/geocode/search', methods=['GET'])
def geocode_search():
    """Proxy for OpenStreetMap Nominatim search API."""
    import requests
    
    query = request.args.get('q')
    limit = request.args.get('limit', 10)
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'format': 'json',
                'q': query,
                'limit': limit
            },
            headers={
                'User-Agent': 'DriveMonitoring/1.0'
            }
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Geocoding service unavailable'}), 503
            
    except Exception as e:
        return jsonify({'error': 'Geocoding service error'}), 500

@api_bp.route('/geocode/reverse', methods=['GET'])
def geocode_reverse():
    """Proxy for OpenStreetMap Nominatim reverse geocoding API."""
    import requests
    
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude parameters are required'}), 400
    
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={
                'format': 'json',
                'lat': lat,
                'lon': lon
            },
            headers={
                'User-Agent': 'DriveMonitoring/1.0'
            }
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Reverse geocoding service unavailable'}), 503
            
    except Exception as e:
        return jsonify({'error': 'Reverse geocoding service error'}), 500