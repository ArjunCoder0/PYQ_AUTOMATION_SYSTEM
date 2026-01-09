// Authentication utilities for frontend
// Handles token storage, API requests with auth, and session management

// API Configuration
const API_BASE = window.location.origin;

// Auth Helper Functions
const Auth = {
    // Get stored token
    getToken() {
        return sessionStorage.getItem('admin_token');
    },

    // Get stored username
    getUsername() {
        return sessionStorage.getItem('admin_username');
    },

    // Store auth data
    setAuth(token, username) {
        sessionStorage.setItem('admin_token', token);
        sessionStorage.setItem('admin_username', username);
    },

    // Clear auth data
    clearAuth() {
        sessionStorage.removeItem('admin_token');
        sessionStorage.removeItem('admin_username');
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Verify token with server
    async verifyToken() {
        const token = this.getToken();
        if (!token) return false;

        try {
            const response = await fetch(`${API_BASE}/api/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.success;
            }
            return false;
        } catch (error) {
            console.error('Token verification error:', error);
            return false;
        }
    },

    // Logout
    async logout() {
        const token = this.getToken();

        // Call logout endpoint
        if (token) {
            try {
                await fetch(`${API_BASE}/api/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }

        // Clear local auth data
        this.clearAuth();

        // Redirect to login
        window.location.href = '/internal/uni-pyq-control-83F9/login';
    },

    // Make authenticated API request
    async fetch(url, options = {}) {
        const token = this.getToken();

        if (!token) {
            throw new Error('Not authenticated');
        }

        // Add Authorization header
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle 401 Unauthorized
        if (response.status === 401) {
            // Token expired or invalid
            this.clearAuth();
            window.location.href = '/internal/uni-pyq-control-83F9/login';
            throw new Error('Session expired');
        }

        return response;
    },

    // Require authentication (call on page load)
    async requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/internal/uni-pyq-control-83F9/login';
            return false;
        }

        // Verify token is still valid
        const valid = await this.verifyToken();
        if (!valid) {
            this.clearAuth();
            window.location.href = '/internal/uni-pyq-control-83F9/login';
            return false;
        }

        return true;
    }
};

// Session timeout handler (24 hours)
const SESSION_CHECK_INTERVAL = 5 * 60 * 1000; // Check every 5 minutes

function startSessionMonitor() {
    setInterval(async () => {
        if (Auth.isAuthenticated()) {
            const valid = await Auth.verifyToken();
            if (!valid) {
                alert('Your session has expired. Please log in again.');
                Auth.clearAuth();
                window.location.href = '/internal/uni-pyq-control-83F9/login';
            }
        }
    }, SESSION_CHECK_INTERVAL);
}

// Start monitoring when page loads
if (Auth.isAuthenticated()) {
    startSessionMonitor();
}

// Export for use in other scripts
window.Auth = Auth;
