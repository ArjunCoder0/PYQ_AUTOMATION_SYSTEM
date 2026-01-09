"""
Security utilities for PYQ Management System
Handles authentication, password hashing, JWT tokens, and security helpers
"""
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Security Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

# Store failed login attempts (IP -> [timestamps])
failed_login_attempts = {}

def hash_password(password):
    """Hash a password using werkzeug's secure method"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def generate_jwt_token(username):
    """Generate a JWT token for authenticated user"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """
    Verify and decode a JWT token
    Returns username if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get('username')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_client_ip():
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def check_rate_limit(ip_address):
    """
    Check if IP has exceeded login attempt limit
    Returns (allowed: bool, remaining_attempts: int)
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=LOGIN_TIMEOUT_MINUTES)
    
    # Clean old attempts
    if ip_address in failed_login_attempts:
        failed_login_attempts[ip_address] = [
            timestamp for timestamp in failed_login_attempts[ip_address]
            if timestamp > cutoff
        ]
    
    # Check current attempts
    attempts = len(failed_login_attempts.get(ip_address, []))
    remaining = MAX_LOGIN_ATTEMPTS - attempts
    
    return (attempts < MAX_LOGIN_ATTEMPTS, max(0, remaining))

def record_failed_login(ip_address):
    """Record a failed login attempt"""
    if ip_address not in failed_login_attempts:
        failed_login_attempts[ip_address] = []
    failed_login_attempts[ip_address].append(datetime.utcnow())

def clear_failed_logins(ip_address):
    """Clear failed login attempts for IP (on successful login)"""
    if ip_address in failed_login_attempts:
        del failed_login_attempts[ip_address]

def require_auth(f):
    """
    Decorator to require JWT authentication for routes
    Usage: @require_auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Extract token (format: "Bearer <token>")
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'success': False, 'error': 'Invalid authorization header'}), 401
        
        # Verify token
        username = verify_jwt_token(token)
        if not username:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Add username to request context
        request.admin_username = username
        
        return f(*args, **kwargs)
    
    return decorated_function

def sanitize_input(text, max_length=500):
    """
    Sanitize user input to prevent injection attacks
    """
    if not text:
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    text = text[:max_length]
    
    # Remove potentially dangerous characters for SQL
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def generate_csrf_token():
    """Generate a CSRF token"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token, expected_token):
    """Verify CSRF token"""
    return secrets.compare_digest(token, expected_token)

def add_security_headers(response):
    """
    Add security headers to response
    Call this in Flask's after_request handler
    """
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

def validate_url(url):
    """
    Validate URL to prevent SSRF attacks
    Returns (valid: bool, error_message: str)
    """
    if not url:
        return False, "URL is required"
    
    # Must be HTTPS
    if not url.startswith('https://'):
        return False, "Only HTTPS URLs are allowed"
    
    # Block internal/private IP addresses
    blocked_patterns = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '10.',
        '172.16.',
        '192.168.',
        '169.254.',
        '[::1]',
        'metadata.google.internal'
    ]
    
    url_lower = url.lower()
    for pattern in blocked_patterns:
        if pattern in url_lower:
            return False, "Internal/private URLs are not allowed"
    
    return True, ""

def validate_file_upload(file):
    """
    Validate uploaded file
    Returns (valid: bool, error_message: str)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check extension
    if not file.filename.lower().endswith('.zip'):
        return False, "Only ZIP files are allowed"
    
    # Check magic bytes (ZIP file signature)
    file.seek(0)
    magic_bytes = file.read(4)
    file.seek(0)  # Reset file pointer
    
    # ZIP files start with PK (0x504B)
    if not magic_bytes.startswith(b'PK'):
        return False, "Invalid ZIP file format"
    
    return True, ""
