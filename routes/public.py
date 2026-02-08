from flask import Blueprint, render_template, request, jsonify
from models.vehicle import Vehicle
from models.location_log import LocationLog
from models.user import Trip, User, PassengerEvent
from models import db
from datetime import datetime, timedelta
from sqlalchemy import desc, func, case
import math
import requests
import json
import time

# Simple in-memory cache for vehicle data
_vehicle_cache = {}
_cache_timestamp = 0
CACHE_DURATION = 30  # Cache for 30 seconds

def clear_vehicle_cache():
    """Clear the vehicle cache to force refresh."""
    global _vehicle_cache, _cache_timestamp
    _vehicle_cache = {}
    _cache_timestamp = 0
    print("🔄 Vehicle cache cleared")


def get_current_passenger_count(trip_id):
    """Return the current passenger count for a trip based on passenger events."""
    if not trip_id:
        print(f"⚠️ get_current_passenger_count: No trip_id provided")
        return 0

    boards = (
        db.session.query(func.coalesce(func.sum(PassengerEvent.count), 0))
        .filter_by(trip_id=trip_id, event_type='board')
        .scalar()
        or 0
    )

    alights = (
        db.session.query(func.coalesce(func.sum(PassengerEvent.count), 0))
        .filter_by(trip_id=trip_id, event_type='alight')
        .scalar()
        or 0
    )

    result = max(0, boards - alights)
    print(f"📊 get_current_passenger_count(trip_id={trip_id}): boards={boards}, alights={alights}, result={result}")
    return result

public_bp = Blueprint('public', __name__)

@public_bp.route('/public/map')
def public_map():
    """Public map view that doesn't require login."""
    return render_template('public/map.html')

@public_bp.route('/public/clear-cache')
def clear_cache_endpoint():
    """Manually clear the vehicle cache - for testing."""
    clear_vehicle_cache()
    return jsonify({'success': True, 'message': 'Cache cleared successfully'})

@public_bp.route('/vehicles/active')
def get_active_vehicles():
    """Get all active vehicles for the public map - OPTIMIZED VERSION with aggressive caching."""
    global _vehicle_cache, _cache_timestamp
    
    try:
        # Check if cache should be bypassed (for manual refresh)
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        # Check cache first - use shorter cache for better UX (10 seconds)
        current_time = time.time()
        CACHE_DURATION_SECONDS = 5  # 10 seconds cache - good balance between performance and freshness
        
        if not force_refresh and _vehicle_cache and (current_time - _cache_timestamp) < CACHE_DURATION_SECONDS:
            # Return cached data with no-cache headers
            response = jsonify(_vehicle_cache)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        # Try to get vehicles from database with error handling
        try:
            # Expire all cached objects to ensure fresh data
            db.session.expire_all()
            
            # OPTIMIZATION: Use a single efficient query with eager loading of drivers AND trips
            # This is a critical performance bottleneck on Render - FIXED N+1 QUERY ISSUE
            from sqlalchemy.orm import joinedload, subqueryload
            from models.user import Trip
            
            # Get all active trips first (single query)
            active_trip_ids = db.session.query(Trip.vehicle_id).filter(
                Trip.status == 'active'
            ).subquery()
            
            # Query vehicles with eager loading AND filter for those with active trips
            active_vehicles = Vehicle.query.options(
                joinedload(Vehicle.assigned_driver)
            ).filter(
                Vehicle.status.in_(['active', 'delayed']),
                Vehicle.current_latitude.isnot(None),
                Vehicle.current_longitude.isnot(None),
                Vehicle.id.in_(db.session.query(active_trip_ids.c.vehicle_id))
            ).all()
            
            # Get all active trips in one query (avoid N+1)
            vehicle_ids = [v.id for v in active_vehicles]
            active_trips_dict = {}
            trip_ids_list = []
            if vehicle_ids:
                active_trips = Trip.query.filter(
                    Trip.vehicle_id.in_(vehicle_ids),
                    Trip.status == 'active'
                ).all()
                active_trips_dict = {trip.vehicle_id: trip for trip in active_trips}
                trip_ids_list = [trip.id for trip in active_trips]
            
            # CRITICAL FIX: Get ALL passenger counts in ONE query instead of N queries
            # This was causing 20+ second delays with multiple vehicles!
            passenger_counts_dict = {}
            if trip_ids_list:
                # Get all passenger events for all trips in one query
                passenger_events = db.session.query(
                    PassengerEvent.trip_id,
                    func.sum(
                        case(
                            (PassengerEvent.event_type == 'board', PassengerEvent.count),
                            else_=0
                        )
                    ).label('boards'),
                    func.sum(
                        case(
                            (PassengerEvent.event_type == 'alight', PassengerEvent.count),
                            else_=0
                        )
                    ).label('alights')
                ).filter(
                    PassengerEvent.trip_id.in_(trip_ids_list)
                ).group_by(PassengerEvent.trip_id).all()
                
                # Build dictionary: trip_id -> passenger_count
                for event in passenger_events:
                    trip_id = event.trip_id
                    boards = event.boards or 0
                    alights = event.alights or 0
                    passenger_counts_dict[trip_id] = max(0, boards - alights)
            
            # Format vehicle data for public consumption (no PII) - SIMPLIFIED
            vehicles_data = []
            for vehicle in active_vehicles:
                # Get active trip from dictionary (no query!)
                active_trip = active_trips_dict.get(vehicle.id)
                
                # Only show vehicles with active trips (departed)
                if not active_trip:
                    continue  # Skip vehicles without active trips
                
                # Calculate route distance and ETA from route_info - ALWAYS calculate, no delays!
                route_distance_km = None
                eta_minutes = None
                
                # Variables for coordinates (used for both ETA calculation and route_info)
                dest_lat = None
                dest_lon = None
                
                # Always calculate distance/ETA if we have vehicle coordinates
                if vehicle.current_latitude and vehicle.current_longitude:
                    try:
                        route_info = None
                        if vehicle.route_info:
                            route_info = json.loads(vehicle.route_info) if isinstance(vehicle.route_info, str) else vehicle.route_info
                        
                        # Try to get destination coordinates from route_info
                        
                        # Debug: Log route_info structure
                        if route_info:
                            print(f"🔍 Vehicle {vehicle.id}: route_info keys={list(route_info.keys()) if isinstance(route_info, dict) else 'not dict'}")
                        
                        # Check for dest_coords (primary destination)
                        if route_info and isinstance(route_info, dict):
                            if 'dest_coords' in route_info and route_info['dest_coords']:
                                dest_coords = route_info['dest_coords']
                                if isinstance(dest_coords, dict):
                                    dest_lat = float(dest_coords.get('lat')) if dest_coords.get('lat') is not None else None
                                    dest_lon = float(dest_coords.get('lon')) if dest_coords.get('lon') is not None else None
                                    print(f"🔍 Vehicle {vehicle.id}: dest_coords found - lat={dest_lat}, lon={dest_lon}")
                            
                            # Fallback: Use origin_coords if dest_coords is missing or invalid
                            if (not dest_lat or not dest_lon) and 'origin_coords' in route_info and route_info['origin_coords']:
                                origin_coords = route_info['origin_coords']
                                if isinstance(origin_coords, dict):
                                    dest_lat = float(origin_coords.get('lat')) if origin_coords.get('lat') is not None else None
                                    dest_lon = float(origin_coords.get('lon')) if origin_coords.get('lon') is not None else None
                                    print(f"🔍 Vehicle {vehicle.id}: Using origin_coords as destination - lat={dest_lat}, lon={dest_lon}")
                            
                            # Final fallback: Geocode destination string if coordinates are still missing
                            if (not dest_lat or not dest_lon) and 'destination' in route_info:
                                destination_name = route_info['destination']
                                print(f"🔍 Vehicle {vehicle.id}: No coordinates found, geocoding destination: {destination_name}")
                                try:
                                    geocoded = geocode_place_for_eta(destination_name)
                                    if geocoded:
                                        dest_lat = geocoded.get('lat')
                                        dest_lon = geocoded.get('lon')
                                        print(f"✓ Vehicle {vehicle.id}: Geocoded destination - lat={dest_lat}, lon={dest_lon}")
                                except Exception as geocode_error:
                                    print(f"⚠ Vehicle {vehicle.id}: Geocoding failed: {geocode_error}")
                        
                        # Calculate distance if we have destination coordinates
                        if dest_lat is not None and dest_lon is not None:
                            route_distance_km = round(calculate_distance_km(
                                vehicle.current_latitude, vehicle.current_longitude,
                                dest_lat, dest_lon
                            ), 2)
                            
                            # Calculate ETA based on current speed (always provide ETA, never show "Calculating")
                            speed_kmh = vehicle.last_speed_kmh or 40  # Default 40 km/h for instant calculation
                            if speed_kmh > 0 and route_distance_km > 0:
                                eta_minutes = round((route_distance_km / speed_kmh) * 60)
                            else:
                                # Fallback: calculate with default speed if speed is 0
                                eta_minutes = round((route_distance_km / 40) * 60)
                            
                            print(f"✓ Vehicle {vehicle.id}: distance={route_distance_km}km, eta={eta_minutes}min, speed={speed_kmh}km/h")
                        else:
                            if not vehicle.route_info:
                                print(f"⚠ Vehicle {vehicle.id}: No route_info at all")
                            elif not route_info:
                                print(f"⚠ Vehicle {vehicle.id}: route_info is None or empty after parsing")
                            else:
                                print(f"⚠ Vehicle {vehicle.id}: route_info exists but no valid dest_coords or origin_coords found. route_info={route_info}")
                    except Exception as e:
                        print(f"✗ Error calculating route info for vehicle {vehicle.id}: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Get driver information (already loaded via joinedload, no extra query!)
                driver_name = None
                driver_image_url = None
                driver_contact_number = None
                if vehicle.assigned_driver:
                    driver_name = vehicle.assigned_driver.get_full_name()
                    driver_image_url = vehicle.assigned_driver.profile_image_url
                    driver_contact_number = vehicle.assigned_driver.contact_number
                    print(f"✓ Vehicle {vehicle.id}: Driver = {driver_name}")
                else:
                    print(f"✗ Vehicle {vehicle.id}: No assigned driver")
                
                # Parse route_info if it's a JSON string
                parsed_route_info = None
                if vehicle.route_info:
                    try:
                        parsed_route_info = json.loads(vehicle.route_info) if isinstance(vehicle.route_info, str) else vehicle.route_info
                    except json.JSONDecodeError:
                        print(f"⚠ Vehicle {vehicle.id}: Failed to parse route_info")
                        parsed_route_info = None
                
                # Add geocoded coordinates to route_info if missing (for map markers)
                # We already geocoded destination for ETA calculation, so reuse it here
                if parsed_route_info and isinstance(parsed_route_info, dict):
                    # If we geocoded destination during ETA calculation, add it to route_info
                    if dest_lat is not None and dest_lon is not None:
                        if not parsed_route_info.get('dest_coords'):
                            parsed_route_info['dest_coords'] = {'lat': dest_lat, 'lon': dest_lon}
                            print(f"✓ Vehicle {vehicle.id}: Added geocoded dest_coords to route_info for map markers")
                    
                    # Only geocode origin if dest_coords exists (means geocoding is working)
                    # Skip if network is down to prevent 502 errors
                    if not parsed_route_info.get('origin_coords') and 'origin' in parsed_route_info:
                        # Only try if we successfully have dest_coords (indicates geocoding is working)
                        if parsed_route_info.get('dest_coords'):
                            origin_name = parsed_route_info.get('origin')
                            if origin_name:
                                try:
                                    origin_geocoded = geocode_place_for_eta(origin_name)
                                    if origin_geocoded:
                                        parsed_route_info['origin_coords'] = origin_geocoded
                                        print(f"✓ Vehicle {vehicle.id}: Geocoded and added origin_coords to route_info")
                                except Exception:
                                    # Silently skip if geocoding fails - don't block the request
                                    pass
                
                current_passengers = 0
                active_trip_id = None
                if active_trip:
                    active_trip_id = active_trip.id
                    # Get passenger count from dictionary (no query!) - CRITICAL PERFORMANCE FIX
                    current_passengers = passenger_counts_dict.get(active_trip_id, 0)
                    print(f"📊 Vehicle {vehicle.id}: active_trip_id={active_trip_id}, current_passengers={current_passengers}")

                capacity = vehicle.capacity or 15  # default capacity if not set
                
                # Get seat status from vehicle
                seat_status = vehicle.get_seat_status()
                occupied_seats = vehicle.get_occupied_seat_count()
                
                vehicles_data.append({
                    'id': vehicle.id,
                    'registration_number': vehicle.registration_number,
                    'type': vehicle.vehicle_type,
                    'status': vehicle.status,
                    'trip_status': 'departed',  # Vehicle is on an active trip
                    'occupancy_status': vehicle.occupancy_status or 'unknown',
                    'latitude': vehicle.current_latitude,
                    'longitude': vehicle.current_longitude,
                    'route': vehicle.route,
                    'route_info': parsed_route_info,  # Send parsed object instead of JSON string
                    'last_updated': vehicle.last_updated.isoformat() if vehicle.last_updated else None,
                    'speed_kmh': vehicle.last_speed_kmh or 60,
                    'route_distance_km': route_distance_km,
                    'eta_minutes': eta_minutes,
                    'driver_name': driver_name,
                    'driver_image_url': driver_image_url,
                    'driver_contact_number': driver_contact_number,
                    'capacity': capacity,
                    'current_passengers': current_passengers,
                    'available_seats': max(capacity - current_passengers, 0),
                    'active_trip_id': active_trip_id,
                    'seat_status': seat_status,
                    'occupied_seats': occupied_seats
                })
            
            # Cache the result
            result = {
                'success': True,
                'vehicles': vehicles_data,
                'count': len(vehicles_data)
            }
            _vehicle_cache = result
            _cache_timestamp = current_time
            
            # Return with cache-busting headers to prevent browser caching
            response = jsonify(result)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
            
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

def geocode_place_for_eta(place_name):
    """Geocode a place name for ETA calculation - lightweight fallback with fast failure."""
    try:
        # Very short timeout to prevent blocking - if Nominatim is unreachable, fail fast
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place_name, "format": "json", "limit": 1},
            headers={"User-Agent": "drive-monitoring/1.0"},
            timeout=1  # Reduced from 3s to 1s - fail fast if network is down
        )
        data = resp.json()
        if isinstance(data, list) and data:
            return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        # Network errors - fail silently to prevent 502s
        # Don't log every failure (too noisy), only log occasionally
        pass
    except Exception as e:
        # Other errors - log but don't block
        print(f"Geocoding error for '{place_name}': {e}")
    return None

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