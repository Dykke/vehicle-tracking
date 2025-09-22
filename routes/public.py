from flask import Blueprint, render_template, request, jsonify
from models.vehicle import Vehicle
from models.location_log import LocationLog
from models.user import Trip
from models import db
from datetime import datetime, timedelta
from sqlalchemy import desc
import math
import requests
import json
import time

# Simple in-memory cache for vehicle data
_vehicle_cache = {}
_cache_timestamp = 0
CACHE_DURATION = 30  # Cache for 30 seconds

public_bp = Blueprint('public', __name__)

@public_bp.route('/public/map')
def public_map():
    """Public map view that doesn't require login."""
    return render_template('public/map.html')

@public_bp.route('/vehicles/active')
def get_active_vehicles():
    """Get all active vehicles for the public map - OPTIMIZED VERSION with aggressive caching."""
    global _vehicle_cache, _cache_timestamp
    
    try:
        # Check cache first - use a longer cache duration for Render (60 seconds)
        current_time = time.time()
        RENDER_CACHE_DURATION = 60  # 1 minute cache for Render
        
        if _vehicle_cache and (current_time - _cache_timestamp) < RENDER_CACHE_DURATION:
            return jsonify(_vehicle_cache)
        
        # Try to get vehicles from database with error handling
        try:
            # OPTIMIZATION: Use a single efficient query
            # This is a critical performance bottleneck on Render
            active_vehicles = Vehicle.query.filter(
                Vehicle.status.in_(['active', 'delayed']),
                Vehicle.current_latitude.isnot(None),
                Vehicle.current_longitude.isnot(None)
            ).all()
            
            # Format vehicle data for public consumption (no PII) - SIMPLIFIED
            vehicles_data = []
            for vehicle in active_vehicles:
                vehicles_data.append({
                    'id': vehicle.id,
                    'type': vehicle.vehicle_type,
                    'status': vehicle.status,
                    'trip_status': 'active',  # Default status
                    'occupancy_status': vehicle.occupancy_status or 'unknown',
                    'latitude': vehicle.current_latitude,
                    'longitude': vehicle.current_longitude,
                    'route': vehicle.route,
                    'route_info': vehicle.route_info,
                    'last_updated': vehicle.last_updated.isoformat() if vehicle.last_updated else None,
                    'speed_kmh': vehicle.last_speed_kmh or 60,
                    'route_distance_km': None,
                    'eta_minutes': None
                })
            
            # Cache the result
            result = {
                'success': True,
                'vehicles': vehicles_data,
                'count': len(vehicles_data)
            }
            _vehicle_cache = result
            _cache_timestamp = current_time
            
            return jsonify(result)
            
        except Exception as db_error:
            # If database fails but we have a cache (even if expired), use it as fallback
            if _vehicle_cache:
                print(f"Database error in /vehicles/active, using expired cache: {db_error}")
                return jsonify(_vehicle_cache)
            
            # No cache available, return empty result
            print(f"Database error in /vehicles/active: {db_error}")
            return jsonify({
                'success': True,
                'vehicles': [],
                'count': 0,
                'message': 'No vehicles available at the moment'
            })
        
    except Exception as e:
        # Ultimate fallback - return empty result
        return jsonify({
            'success': True,
            'vehicles': [],
            'count': 0,
            'message': 'Service temporarily unavailable'
        })

@public_bp.route('/vehicle/<int:vehicle_id>/eta', methods=['GET'])
def calculate_eta(vehicle_id):
    """Calculate ETA from vehicle to destination."""
    try:
        # Get destination coordinates from query params
        dest_lat = request.args.get('dest_lat', type=float)
        dest_lng = request.args.get('dest_lng', type=float)
        
        if not dest_lat or not dest_lng:
            return jsonify({'error': 'Destination coordinates are required.'}), 400
        
        # Get the vehicle
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        if not vehicle.current_latitude or not vehicle.current_longitude:
            return jsonify({'error': 'Vehicle location is not available.'}), 400
        
        # Calculate distance in kilometers
        distance_km = calculate_distance_km(
            vehicle.current_latitude, vehicle.current_longitude,
            dest_lat, dest_lng
        )
        
        # Get vehicle speed (use recent average or default)
        speed_kmh = vehicle.last_speed_kmh or get_recent_vehicle_speed(vehicle.id) or 30  # Default 30 km/h
        
        # Calculate ETA in minutes
        if speed_kmh > 0:
            eta_minutes = (distance_km / speed_kmh) * 60
        else:
            eta_minutes = (distance_km / 30) * 60  # Default 30 km/h if speed is 0
        
        # Try to get a more accurate route-based ETA using OSRM
        try:
            osrm_eta = get_osrm_eta(
                vehicle.current_latitude, vehicle.current_longitude,
                dest_lat, dest_lng
            )
            
            if osrm_eta:
                # Adjust OSRM time based on current speed vs. typical speed
                # OSRM assumes typical speeds, so we adjust based on actual speed
                typical_speed = 40  # km/h, typical speed assumed by OSRM
                speed_factor = speed_kmh / typical_speed if speed_kmh > 0 else 1
                
                # Limit the adjustment factor to reasonable bounds
                speed_factor = max(0.5, min(speed_factor, 1.5))
                
                # Apply the speed adjustment to the OSRM ETA
                osrm_eta_adjusted = osrm_eta / speed_factor
                
                # Use the adjusted OSRM ETA
                eta_minutes = osrm_eta_adjusted
        except Exception as e:
            # If OSRM fails, we already have a fallback ETA
            print(f"OSRM ETA calculation failed: {str(e)}")
        
        # Round to nearest minute and ensure minimum of 1 minute
        eta_minutes = max(1, round(eta_minutes))
        
        # Calculate arrival time
        arrival_time = datetime.utcnow() + timedelta(minutes=eta_minutes)
        
        return jsonify({
            'success': True,
            'eta_minutes': eta_minutes,
            'distance_km': round(distance_km, 2),
            'speed_kmh': round(speed_kmh, 2),
            'arrival_time': arrival_time.isoformat(),
            'vehicle_id': vehicle.id,
            'vehicle_type': vehicle.vehicle_type,
            'occupancy_status': vehicle.occupancy_status or 'unknown'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

def get_recent_vehicle_speed(vehicle_id):
    """Calculate recent average speed from location logs."""
    try:
        # Get location logs from the last 5 minutes
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        logs = LocationLog.query.filter(
            LocationLog.vehicle_id == vehicle_id,
            LocationLog.created_at >= five_minutes_ago
        ).order_by(desc(LocationLog.created_at)).all()
        
        if len(logs) < 2:
            return None  # Not enough data points
        
        # Calculate speeds between consecutive points
        speeds = []
        for i in range(len(logs) - 1):
            # Calculate distance
            distance_km = calculate_distance_km(
                logs[i].latitude, logs[i].longitude,
                logs[i+1].latitude, logs[i+1].longitude
            )
            
            # Calculate time difference in hours
            time_diff = (logs[i].created_at - logs[i+1].created_at).total_seconds() / 3600
            
            # Calculate speed if time difference is significant
            if time_diff > 0:
                speed = distance_km / time_diff
                
                # Filter out unrealistic speeds (e.g., GPS jumps)
                if speed < 120:  # Max 120 km/h as sanity check
                    speeds.append(speed)
        
        # Return average speed if we have valid measurements
        if speeds:
            return sum(speeds) / len(speeds)
        
        return None
    
    except Exception as e:
        print(f"Error calculating vehicle speed: {str(e)}")
        return None

def get_osrm_eta(start_lat, start_lng, end_lat, end_lng):
    """Get ETA in minutes using OSRM routing service."""
    try:
        # Call OSRM API
        url = f"https://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}"
        response = requests.get(url, params={"overview": "false"})
        data = response.json()
        
        if data["code"] == "Ok" and data["routes"]:
            # OSRM returns duration in seconds, convert to minutes
            return data["routes"][0]["duration"] / 60
        
        return None
    
    except Exception as e:
        print(f"OSRM API error: {str(e)}")
        return None