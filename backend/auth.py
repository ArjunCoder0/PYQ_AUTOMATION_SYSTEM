"""
Authentication module for PYQ Management System
Handles admin login, logout, and session management
"""
import os
from flask import Blueprint, request, jsonify
from security import (
    verify_password, generate_jwt_token, verify_jwt_token,
    get_client_ip, check_rate_limit, record_failed_login, 
    clear_failed_logins, hash_password
)
from database import Session, AdminUser
from sqlalchemy.sql import func

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = None

def init_admin_user():
    """
    Initialize admin user in database
    Creates admin user if it doesn't exist
    """
    global ADMIN_PASSWORD_HASH
    
    session = Session()
    try:
        # Check if admin user exists
        admin_user = session.query(AdminUser).filter(
            AdminUser.username == ADMIN_USERNAME
        ).first()
        
        if admin_user:
            # Admin exists, load password hash
            ADMIN_PASSWORD_HASH = admin_user.password_hash
            print(f"✓ Admin user '{ADMIN_USERNAME}' loaded")
        else:
            # Create admin user
            admin_password = os.environ.get('ADMIN_PASSWORD')
            
            if not admin_password:
                # Generate random password if not set
                import secrets
                admin_password = secrets.token_urlsafe(16)
                print(f"⚠️  ADMIN_PASSWORD not set in environment!")
                print(f"🔑 Generated admin password: {admin_password}")
                print(f"⚠️  Please save this password and set ADMIN_PASSWORD in environment variables!")
            
            # Hash and store password
            ADMIN_PASSWORD_HASH = hash_password(admin_password)
            
            new_admin = AdminUser(
                username=ADMIN_USERNAME,
                password_hash=ADMIN_PASSWORD_HASH
            )
            session.add(new_admin)
            session.commit()
            print(f"✓ Admin user '{ADMIN_USERNAME}' created")
    except Exception as e:
        session.rollback()
        print(f"⚠️ Error initializing admin user: {e}")
        raise
    finally:
        session.close()

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Admin login endpoint
    POST /api/auth/login
    Body: { "username": "admin", "password": "..." }
    Returns: { "success": true, "token": "...", "expires_in": 86400 }
    """
    try:
        # Get client IP for rate limiting
        client_ip = get_client_ip()
        
        # Check rate limit
        allowed, remaining = check_rate_limit(client_ip)
        if not allowed:
            return jsonify({
                'success': False,
                'error': 'Too many failed attempts. Please try again later.'
            }), 429
        
        # Get credentials
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify credentials
        if username != ADMIN_USERNAME or not verify_password(ADMIN_PASSWORD_HASH, password):
            # Record failed attempt
            record_failed_login(client_ip)
            
            # Generic error message (don't reveal which field is wrong)
            return jsonify({
                'success': False,
                'error': 'Invalid credentials',
                'remaining_attempts': remaining - 1
            }), 401
        
        # Successful login
        clear_failed_logins(client_ip)
        
        # Update last login time
        session = Session()
        try:
            admin_user = session.query(AdminUser).filter(
                AdminUser.username == username
            ).first()
            if admin_user:
                admin_user.last_login = func.now()
                session.commit()
        finally:
            session.close()
        
        # Generate JWT token
        token = generate_jwt_token(username)
        
        return jsonify({
            'success': True,
            'token': token,
            'expires_in': 86400,  # 24 hours in seconds
            'username': username
        }), 200
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@auth_bp.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """
    Verify if current token is valid
    GET /api/auth/verify
    Headers: Authorization: Bearer <token>
    Returns: { "success": true, "username": "admin" }
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        # Extract token
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'success': False, 'error': 'Invalid authorization header'}), 401
        
        # Verify token
        username = verify_jwt_token(token)
        if not username:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        return jsonify({
            'success': True,
            'username': username
        }), 200
    
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Logout endpoint (client-side token deletion)
    POST /api/auth/logout
    Returns: { "success": true }
    """
    # With JWT, logout is handled client-side by deleting the token
    # We just acknowledge the logout request
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

@auth_bp.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """
    Change admin password (requires authentication)
    POST /api/auth/change-password
    Body: { "current_password": "...", "new_password": "..." }
    """
    global ADMIN_PASSWORD_HASH
    
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'success': False, 'error': 'Invalid authorization header'}), 401
        
        # Verify token
        username = verify_jwt_token(token)
        if not username:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Get passwords
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'error': 'Both passwords are required'}), 400
        
        # Validate new password strength
        if len(new_password) < 8:
            return jsonify({'success': False, 'error': 'New password must be at least 8 characters'}), 400
        
        # Verify current password
        if not verify_password(ADMIN_PASSWORD_HASH, current_password):
            return jsonify({'success': False, 'error': 'Current password is incorrect'}), 401
        
        # Update password
        new_hash = hash_password(new_password)
        
        session = Session()
        try:
            admin_user = session.query(AdminUser).filter(
                AdminUser.username == username
            ).first()
            if admin_user:
                admin_user.password_hash = new_hash
                session.commit()
        finally:
            session.close()
        
        global ADMIN_PASSWORD_HASH
        ADMIN_PASSWORD_HASH = new_hash
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        print(f"Password change error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
