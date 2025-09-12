from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.vehicle import Vehicle
from datetime import datetime, timedelta

commuter_bp = Blueprint('commuter', __name__)

@commuter_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'commuter':
        flash('Access denied. Commuter account required.', 'error')
        return redirect(url_for('index'))
    return render_template('commuter/dashboard.html')

@commuter_bp.route('/vehicles/active')
def get_active_vehicles():
    """Get all active and delayed vehicles for commuters, with relaxed time constraints."""
    # First, log all vehicles regardless of status to understand what's available
    all_vehicles = Vehicle.query.all()
    print(f"[COMMUTER DASHBOARD] DEBUG: Total vehicles in system: {len(all_vehicles)}")
    for v in all_vehicles:
        print(f"[COMMUTER DASHBOARD] DEBUG: Vehicle #{v.id}: Status={v.status}, "
              f"Updated={v.last_updated}, Coords=({v.current_latitude}, {v.current_longitude})")
    
    # Get all active and delayed vehicles WITHOUT a timestamp filter
    # This is the key change from before - no time restriction
    active_vehicles = Vehicle.query.filter(
        Vehicle.status.in_(['active', 'delayed'])
    ).all()
    
    # Debug information
    print(f"[COMMUTER DASHBOARD] Found {len(active_vehicles)} active/delayed vehicles")
    for v in active_vehicles:
        print(f"[COMMUTER DASHBOARD] Vehicle #{v.id}: {v.registration_number}, "
              f"Status: {v.status}, "
              f"Coords: ({v.current_latitude}, {v.current_longitude}), "
              f"Updated: {v.last_updated}")
    
    # Convert to dict and ensure we have coordinates
    vehicle_dicts = []
    for v in active_vehicles:
        v_dict = v.to_dict()
        # Check if coordinates are present
        if v.current_latitude and v.current_longitude:
            vehicle_dicts.append(v_dict)
            print(f"[COMMUTER DASHBOARD] Including vehicle #{v.id} with coords")
        else:
            print(f"[COMMUTER DASHBOARD] Skipping vehicle #{v.id} - no coords")
    
    response = {'vehicles': vehicle_dicts}
    print(f"[COMMUTER DASHBOARD] Returning {len(vehicle_dicts)} vehicles with coordinates")
    
    return jsonify(response) 