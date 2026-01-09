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
from database import get_db_connection

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
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create admin_users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Check if admin user exists
    cursor.execute('SELECT password_hash FROM admin_users WHERE username = ?', (ADMIN_USERNAME,))
    result = cursor.fetchone()
    
    if result:
        # Admin exists, load password hash
        ADMIN_PASSWORD_HASH = result[0]
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
        cursor.execute(
            'INSERT INTO admin_users (username, password_hash) VALUES (?, ?)',
            (ADMIN_USERNAME, ADMIN_PASSWORD_HASH)
        )
        conn.commit()
        print(f"✓ Admin user '{ADMIN_USERNAME}' created")
    
    conn.close()

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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE username = ?',
            (username,)
        )
        conn.commit()
        conn.close()
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE admin_users SET password_hash = ? WHERE username = ?',
            (new_hash, username)
        )
        conn.commit()
        conn.close()
        
        ADMIN_PASSWORD_HASH = new_hash
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        print(f"Password change error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
