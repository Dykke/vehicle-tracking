from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from models.notification import NotificationSetting
from models import db
import os
import time
import hashlib
import hmac
import secrets
import re
from secure_config import (
    get_admin_credentials, 
    get_operator_credentials,
    RATE_LIMIT_MAX_ATTEMPTS,
    RATE_LIMIT_LOCKOUT_TIME,
    USERNAME_PATTERN,
    EMAIL_PATTERN,
    PASSWORD_MIN_LENGTH
)

auth_bp = Blueprint('auth', __name__)

# Secure constant-time string comparison to prevent timing attacks
def secure_compare(a, b):
    return hmac.compare_digest(a, b)

# Rate limiting for failed login attempts
login_attempts = {}

@auth_bp.route('/staff')
def staff_portal():
    """Staff portal page - entry point for employees."""
    return render_template('auth/staff.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data with sanitization
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Basic input validation
        if not username:
            flash('Username is required')
            return render_template('auth/login.html')
            
        if not password:
            flash('Password is required')
            return render_template('auth/login.html')
        
        # Check for username injection attempts
        if not re.match(USERNAME_PATTERN, username):
            flash('Invalid username format')
            return render_template('auth/login.html')
        
        # Check rate limiting
        client_ip = request.remote_addr
        current_time = time.time()
        
        if client_ip in login_attempts:
            attempts, lockout_time = login_attempts[client_ip]
            
            # Check if user is in lockout period
            if attempts >= RATE_LIMIT_MAX_ATTEMPTS and current_time < lockout_time + RATE_LIMIT_LOCKOUT_TIME:
                remaining = int(lockout_time + RATE_LIMIT_LOCKOUT_TIME - current_time)
                flash(f'Too many failed login attempts. Please try again in {remaining} seconds.')
                return render_template('auth/login.html')
            
            # Reset attempts if lockout period has passed
            if current_time > lockout_time + RATE_LIMIT_LOCKOUT_TIME:
                login_attempts[client_ip] = (0, current_time)
        else:
            login_attempts[client_ip] = (0, current_time)
        
        # Get admin and operator credentials
        admin_user, admin_pass = get_admin_credentials()
        operator_user, operator_pass = get_operator_credentials()
        
        # Special case for admin and operator with secure comparison
        if secure_compare(username, admin_user) and secure_compare(password, admin_pass):
            # Hard-coded admin login
            user = User.query.filter_by(username=admin_user).first()
            if not user:
                # Create admin user if it doesn't exist
                user = User(username=admin_user, email=f'{admin_user}@example.com', user_type='admin')
                user.set_password(admin_pass)
                db.session.add(user)
                db.session.commit()
            
            # Reset login attempts on successful login
            if client_ip in login_attempts:
                login_attempts.pop(client_ip)
                
            login_user(user)
            return redirect(url_for('operator.dashboard'))
        
        elif secure_compare(username, operator_user) and secure_compare(password, operator_pass):
            # Hard-coded operator login
            user = User.query.filter_by(username=operator_user).first()
            if not user:
                # Create operator user if it doesn't exist
                user = User(username=operator_user, email=f'{operator_user}@example.com', user_type='operator')
                user.set_password(operator_pass)
                db.session.add(user)
                db.session.commit()
            
            # Reset login attempts on successful login
            if client_ip in login_attempts:
                login_attempts.pop(client_ip)
                
            login_user(user)
            return redirect(url_for('operator.dashboard'))
        
        # Normal login flow for other users
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                # Increment failed login attempts
                attempts, lockout_time = login_attempts[client_ip]
                login_attempts[client_ip] = (attempts + 1, current_time)
                
                flash('Username not found. Please check your username or register a new account.')
                return render_template('auth/login.html')
            
            if not user.check_password(password):
                # Increment failed login attempts
                attempts, lockout_time = login_attempts[client_ip]
                login_attempts[client_ip] = (attempts + 1, current_time)
                
                flash('Invalid password. Please try again.')
                return render_template('auth/login.html')
            
            # Check if user is active
            if hasattr(user, 'is_active') and not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.')
                return render_template('auth/login.html')
            
            # Reset login attempts on successful login
            if client_ip in login_attempts:
                login_attempts.pop(client_ip)
                
            login_user(user)
            if user.user_type == 'admin' or user.user_type == 'operator':
                return redirect(url_for('operator.dashboard'))
            elif user.user_type == 'driver':
                return redirect(url_for('driver.dashboard'))
            else:
                return redirect(url_for('commuter.dashboard'))
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.')
            return render_template('auth/login.html')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data with sanitization
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        middle_name = request.form.get('middle_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        # Force user_type to commuter for public registration
        user_type = 'commuter'
        terms_accepted = request.form.get('terms_accepted')
        
        # Basic input validation
        if not re.match(USERNAME_PATTERN, username):
            flash('Invalid username format. Use only letters, numbers, and underscores.')
            return redirect(url_for('auth.register'))
            
        if not re.match(EMAIL_PATTERN, email):
            flash('Invalid email format')
            return redirect(url_for('auth.register'))
            
        if len(password) < PASSWORD_MIN_LENGTH:
            flash(f'Password must be at least {PASSWORD_MIN_LENGTH} characters long')
            return redirect(url_for('auth.register'))
        
        # Check if terms were accepted
        if not terms_accepted:
            flash('You must accept the Terms and Conditions to register')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
            
        try:
            user = User(
                username=username, 
                email=email, 
                user_type=user_type,
                first_name=first_name if first_name else None,
                middle_name=middle_name if middle_name else None,
                last_name=last_name if last_name else None
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(f"Registration error: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.')
            return render_template('auth/register.html')
        
        # Create notification settings for the new user
        notification_settings = NotificationSetting(
            user_id=user.id,
            enabled=True,
            notification_radius=500,  # Default 500 meters
            notify_specific_routes=False,
            routes=[],
            notification_cooldown=300  # Default 5 minutes
        )
        db.session.add(notification_settings)
        db.session.commit()
        
        login_user(user)
        if user_type == 'operator':
            return redirect(url_for('operator.dashboard'))
        else:
            return redirect(url_for('commuter.dashboard'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route - optimized for fast response."""
    try:
        logout_user()
    except Exception as e:
        # Log error but don't fail logout
        print(f"Logout error (non-critical): {str(e)}")
    # Always redirect regardless of errors
    return redirect(url_for('index'))