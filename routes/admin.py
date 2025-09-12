from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models.user import User, DriverActionLog
from models.vehicle import Vehicle
from models import db
from sqlalchemy import desc, and_, or_, func
from datetime import datetime, timedelta
import json
import csv
import io
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin account required.', 'error')
        return redirect(url_for('index'))
    
    # Get counts for dashboard
    vehicle_count = Vehicle.query.count()
    active_vehicle_count = Vehicle.query.filter_by(status='active').count()
    driver_count = User.query.filter_by(user_type='driver').count()
    operator_count = User.query.filter_by(user_type='operator').count()
    
    # Get recent logs
    recent_logs = DriverActionLog.query.order_by(desc(DriverActionLog.created_at)).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        vehicle_count=vehicle_count,
        active_vehicle_count=active_vehicle_count,
        driver_count=driver_count,
        operator_count=operator_count,
        recent_logs=recent_logs
    )

@admin_bp.route('/admin/logs/actions')
@login_required
def action_logs():
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        flash('Access denied. Admin or operator account required.', 'error')
        return redirect(url_for('index'))
    
    # Get all drivers, vehicles, and operators for filters
    drivers = User.query.filter_by(user_type='driver').all()
    
    # For operators, only show vehicles they own
    if current_user.user_type == 'operator':
        vehicles = Vehicle.query.filter_by(owner_id=current_user.id).all()
        operators = [current_user]
    else:
        vehicles = Vehicle.query.all()
        operators = User.query.filter_by(user_type='operator').all()
    
    return render_template(
        'admin/action_logs.html',
        drivers=drivers,
        vehicles=vehicles,
        operators=operators
    )

@admin_bp.route('/admin/logs/actions/data')
@login_required
def action_logs_data():
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Get filter parameters
    driver_id = request.args.get('driver_id')
    vehicle_id = request.args.get('vehicle_id')
    operator_id = request.args.get('operator_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_types = request.args.get('action_types', 'all')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Start with base query
    query = db.session.query(
        DriverActionLog,
        User.username.label('driver_username'),
        User.profile_image_url.label('driver_profile_image_url'),
        Vehicle.registration_number.label('vehicle_registration'),
        User.created_by_id.label('operator_id')
    ).join(
        User, DriverActionLog.driver_id == User.id
    ).outerjoin(
        Vehicle, DriverActionLog.vehicle_id == Vehicle.id
    )
    
    # Apply filters
    if driver_id:
        query = query.filter(DriverActionLog.driver_id == driver_id)
    
    if vehicle_id:
        query = query.filter(DriverActionLog.vehicle_id == vehicle_id)
    
    # For operators, only show logs for their drivers or vehicles they own
    if current_user.user_type == 'operator':
        query = query.filter(
            or_(
                User.created_by_id == current_user.id,
                Vehicle.owner_id == current_user.id
            )
        )
    elif operator_id:  # Only apply operator filter for admins
        query = query.filter(User.created_by_id == operator_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(DriverActionLog.created_at >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the entire end day
        query = query.filter(DriverActionLog.created_at < end_date_obj)
    
    if action_types and action_types != 'all':
        action_list = action_types.split(',')
        query = query.filter(DriverActionLog.action.in_(action_list))
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination
    query = query.order_by(desc(DriverActionLog.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    results = query.all()
    
    # Get operator usernames for each log
    operator_ids = [result.operator_id for result in results if result.operator_id]
    operators = {op.id: op.username for op in User.query.filter(User.id.in_(operator_ids)).all()}
    
    # Format results
    logs = []
    for result in results:
        log = result[0]
        log_dict = {
            'id': log.id,
            'driver_id': log.driver_id,
            'driver_username': result.driver_username,
            'driver_profile_image_url': result.driver_profile_image_url,
            'vehicle_id': log.vehicle_id,
            'vehicle_registration': result.vehicle_registration,
            'action': log.action,
            'meta_data': log.meta_data,
            'created_at': log.created_at.isoformat() + 'Z',
            'operator_id': result.operator_id,
            'operator_username': operators.get(result.operator_id) if result.operator_id else None
        }
        logs.append(log_dict)
    
    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': total_pages
    }
    
    return jsonify({
        'success': True,
        'logs': logs,
        'pagination': pagination
    })

@admin_bp.route('/admin/logs/actions/export')
@login_required
def export_action_logs():
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Get filter parameters
    driver_id = request.args.get('driver_id')
    vehicle_id = request.args.get('vehicle_id')
    operator_id = request.args.get('operator_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_types = request.args.get('action_types', 'all')
    
    # Start with base query
    query = db.session.query(
        DriverActionLog,
        User.username.label('driver_username'),
        Vehicle.registration_number.label('vehicle_registration'),
        User.created_by_id.label('operator_id')
    ).join(
        User, DriverActionLog.driver_id == User.id
    ).outerjoin(
        Vehicle, DriverActionLog.vehicle_id == Vehicle.id
    )
    
    # Apply filters
    if driver_id:
        query = query.filter(DriverActionLog.driver_id == driver_id)
    
    if vehicle_id:
        query = query.filter(DriverActionLog.vehicle_id == vehicle_id)
    
    # For operators, only show logs for their drivers or vehicles they own
    if current_user.user_type == 'operator':
        query = query.filter(
            or_(
                User.created_by_id == current_user.id,
                Vehicle.owner_id == current_user.id
            )
        )
    elif operator_id:  # Only apply operator filter for admins
        query = query.filter(User.created_by_id == operator_id)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(DriverActionLog.created_at >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the entire end day
        query = query.filter(DriverActionLog.created_at < end_date_obj)
    
    if action_types and action_types != 'all':
        action_list = action_types.split(',')
        query = query.filter(DriverActionLog.action.in_(action_list))
    
    # Execute query
    results = query.order_by(desc(DriverActionLog.created_at)).all()
    
    # Get operator usernames for each log
    operator_ids = [result.operator_id for result in results if result.operator_id]
    operators = {op.id: op.username for op in User.query.filter(User.id.in_(operator_ids)).all()}
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Date', 'Time', 'Driver', 'Vehicle', 'Action', 'Operator', 'Details'
    ])
    
    # Write data
    for result in results:
        log = result[0]
        
        # Format date and time
        created_at = log.created_at
        date_str = created_at.strftime('%Y-%m-%d')
        time_str = created_at.strftime('%H:%M:%S')
        
        # Format metadata
        meta_data_str = ''
        if log.meta_data:
            try:
                meta_data = log.meta_data if isinstance(log.meta_data, dict) else json.loads(log.meta_data)
                meta_items = []
                for key, value in meta_data.items():
                    meta_items.append(f"{key}: {value}")
                meta_data_str = ' | '.join(meta_items)
            except:
                meta_data_str = str(log.meta_data)
        
        writer.writerow([
            log.id,
            date_str,
            time_str,
            result.driver_username,
            result.vehicle_registration or 'N/A',
            log.action,
            operators.get(result.operator_id) if result.operator_id else 'N/A',
            meta_data_str
        ])
    
    # Generate filename with current date
    filename = f"action_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename=filename
    )

@admin_bp.route('/admin/driver/<int:driver_id>/activate', methods=['POST'])
@login_required
def activate_driver(driver_id):
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        return jsonify({'error': 'Access denied'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if operator has permission to activate this driver
    if current_user.user_type == 'operator' and driver.created_by_id != current_user.id:
        return jsonify({'error': 'You do not have permission to activate this driver'}), 403
    
    driver.is_active = True
    db.session.commit()
    
    return jsonify({'message': f'Driver {driver.username} activated successfully'})

@admin_bp.route('/admin/driver/<int:driver_id>/deactivate', methods=['POST'])
@login_required
def deactivate_driver(driver_id):
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        return jsonify({'error': 'Access denied'}), 403
    
    driver = User.query.get_or_404(driver_id)
    
    # Check if operator has permission to deactivate this driver
    if current_user.user_type == 'operator' and driver.created_by_id != current_user.id:
        return jsonify({'error': 'You do not have permission to deactivate this driver'}), 403
    
    driver.is_active = False
    db.session.commit()
    
    return jsonify({'message': f'Driver {driver.username} deactivated successfully'})

@admin_bp.route('/operator/drivers/profile-picture/upload', methods=['POST'])
@login_required
def upload_profile_picture():
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        return jsonify({'error': 'Access denied'}), 403
    
    driver_id = request.form.get('driver_id')
    if not driver_id:
        return jsonify({'error': 'Driver ID is required'}), 400
    
    driver = User.query.get_or_404(int(driver_id))
    
    # Check if operator has permission to update this driver
    if current_user.user_type == 'operator' and driver.created_by_id != current_user.id:
        return jsonify({'error': 'You do not have permission to update this driver'}), 403
    
    if 'profile_image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['profile_image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate a unique filename
        filename = secure_filename(f"{driver.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        file_path = os.path.join(upload_dir, filename)
        
        # Save the file
        file.save(file_path)
        
        # Update the driver's profile image URL
        relative_path = os.path.join('uploads', 'profiles', filename).replace('\\', '/')
        driver.profile_image_url = f'/static/{relative_path}'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile picture uploaded successfully',
            'profile_image_url': driver.profile_image_url
        })
    
    return jsonify({'error': 'Failed to upload file'}), 500

@admin_bp.route('/operator/drivers/profile-picture/remove', methods=['POST'])
@login_required
def remove_profile_picture():
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    driver_id = data.get('driver_id')
    
    if not driver_id:
        return jsonify({'error': 'Driver ID is required'}), 400
    
    driver = User.query.get_or_404(int(driver_id))
    
    # Check if operator has permission to update this driver
    if current_user.user_type == 'operator' and driver.created_by_id != current_user.id:
        return jsonify({'error': 'You do not have permission to update this driver'}), 403
    
    # Check if driver has a profile image
    if not driver.profile_image_url:
        return jsonify({'error': 'Driver does not have a profile image'}), 400
    
    # Try to delete the file
    try:
        file_path = os.path.join('static', driver.profile_image_url.replace('/static/', ''))
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error removing file: {e}")
    
    # Update the driver record
    driver.profile_image_url = None
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile picture removed successfully'
    })

@admin_bp.route('/admin/drivers')
@login_required
def manage_drivers():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin account required.', 'error')
        return redirect(url_for('index'))
    
    drivers = User.query.filter_by(user_type='driver').all()
    return render_template('operator/manage_drivers.html', drivers=drivers)

@admin_bp.route('/admin/profile-pictures')
@login_required
def manage_profile_pictures():
    if current_user.user_type != 'admin' and current_user.user_type != 'operator':
        flash('Access denied. Admin or operator account required.', 'error')
        return redirect(url_for('index'))
    
    # Get drivers based on user type
    if current_user.user_type == 'admin':
        drivers = User.query.filter_by(user_type='driver').all()
    else:  # operator
        drivers = User.query.filter_by(user_type='driver', created_by_id=current_user.id).all()
    
    return render_template('operator/profile_picture.html', drivers=drivers)