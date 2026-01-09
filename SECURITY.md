# Security Documentation

## 🔐 Security Features

This application implements comprehensive security measures to protect against common web vulnerabilities and unauthorized access.

### Implemented Security Features

1. **Authentication & Authorization**
   - JWT-based authentication for admin access
   - Password hashing using PBKDF2-SHA256
   - Session management with automatic expiration (24 hours)
   - Rate limiting on login attempts (5 attempts per 15 minutes)

2. **Access Control**
   - Secret, non-discoverable admin URL
   - All admin endpoints require authentication
   - Token verification on every request
   - Automatic session timeout and re-authentication

3. **Input Validation & Sanitization**
   - File upload validation (magic byte checking)
   - URL validation to prevent SSRF attacks
   - SQL injection prevention through parameterized queries
   - Input length limits and dangerous character filtering

4. **Security Headers**
   - Content Security Policy (CSP)
   - X-Frame-Options (clickjacking protection)
   - X-Content-Type-Options (MIME sniffing protection)
   - X-XSS-Protection
   - Referrer-Policy
   - Permissions-Policy

5. **Rate Limiting**
   - Login attempt limiting
   - IP-based tracking
   - Automatic lockout after failed attempts

6. **Secure Communication**
   - HTTPS enforcement in production
   - Secure cookie settings
   - CORS configuration

## 🚀 Setup Instructions

### 1. Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set the following **required** variables:

```bash
# Generate a secure secret key
SECRET_KEY=<generate-with-python-secrets>

# Set admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<your-secure-password>

# Cloudinary credentials (for production)
CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-api-key>
CLOUDINARY_API_SECRET=<your-api-secret>
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Admin Password Requirements

- Minimum 8 characters
- Use a strong, unique password
- Store securely (password manager recommended)
- Change default password immediately in production

### 3. First-Time Setup

On first run, if `ADMIN_PASSWORD` is not set in environment variables, the system will:
1. Generate a random password
2. Display it in the console logs
3. **Save this password immediately!**

## 🔑 Authentication Flow

### Admin Login

1. Navigate to the secret admin URL:
   ```
   https://your-domain.com/internal/uni-pyq-control-83F9/login
   ```

2. Enter admin credentials

3. On successful login:
   - JWT token is generated (valid for 24 hours)
   - Token stored in sessionStorage (not localStorage for security)
   - Redirected to admin dashboard

4. Token is automatically included in all admin API requests

### Session Management

- **Token Expiration:** 24 hours from login
- **Auto-Verification:** Token verified every 5 minutes
- **Session Timeout:** Automatic logout on token expiration
- **Logout:** Clears token and redirects to login

## 🛡️ Security Best Practices

### For Development

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use different passwords** for development and production
3. **Don't share admin credentials** via insecure channels
4. **Test security features** before deploying

### For Production

1. **Use HTTPS only** - Configure SSL/TLS certificates
2. **Set strong SECRET_KEY** - Use the generated random key
3. **Use strong admin password** - At least 12 characters, mixed case, numbers, symbols
4. **Keep secret URL secret** - Don't share publicly
5. **Monitor login attempts** - Check logs for suspicious activity
6. **Update dependencies** regularly for security patches
7. **Backup database** regularly
8. **Use environment variables** - Never hardcode credentials

### Railway Deployment

Set environment variables in Railway dashboard:

1. Go to your project → Variables
2. Add each variable from `.env.example`
3. Use strong, unique values for production
4. Verify all variables are set before deployment

## 🚨 Security Incident Response

### If Admin Credentials Are Compromised

1. **Immediately change admin password:**
   ```bash
   # Use the change password endpoint
   POST /api/auth/change-password
   ```

2. **Regenerate SECRET_KEY:**
   - Generate new key
   - Update environment variable
   - Restart application (invalidates all existing tokens)

3. **Review logs** for unauthorized access

4. **Check database** for unauthorized changes

### If Secret URL Is Exposed

1. **Change the secret URL** in code:
   - Update routes in `backend/app.py`
   - Update URLs in `frontend/auth.js` and `frontend/admin_login.html`
   - Redeploy application

2. **Monitor access logs** for suspicious activity

## 📊 Security Monitoring

### What to Monitor

1. **Failed login attempts** - Multiple failures from same IP
2. **Unusual access patterns** - Access at odd hours
3. **API errors** - Repeated 401/403 errors
4. **File upload activity** - Large or suspicious uploads

### Logging

The application logs:
- All authentication attempts (success/failure)
- Admin actions (uploads, processing)
- Security events (rate limiting, token expiration)
- Errors and exceptions

Check logs regularly:
```bash
# Railway
railway logs

# Local
Check console output
```

## 🔒 API Security

### Protected Endpoints

All admin endpoints require authentication:
- `/api/admin/upload`
- `/api/admin/fetch-zip`
- `/api/admin/process-batch/<job_id>`
- `/api/admin/recent-job`
- `/api/admin/job-status/<job_id>`
- `/api/admin/jobs`

### Public Endpoints

These endpoints are public (no authentication required):
- `/api/sessions`
- `/api/branches`
- `/api/subjects`
- `/api/paper`
- `/api/pdf/view/<file_id>`
- `/api/pdf/download/<file_id>`
- `/api/health`

## 🐛 Reporting Security Vulnerabilities

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. **Do NOT** share details publicly
3. **Contact** the maintainer directly
4. **Provide** detailed information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Railway Security](https://docs.railway.app/reference/security)

## ✅ Security Checklist

Before deploying to production:

- [ ] Strong SECRET_KEY set in environment
- [ ] Strong admin password set
- [ ] All environment variables configured
- [ ] HTTPS enabled
- [ ] Secret admin URL not publicly shared
- [ ] `.env` file not committed to git
- [ ] Dependencies updated to latest secure versions
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Authentication flow tested
- [ ] Session timeout tested
- [ ] Logs monitored
- [ ] Backup strategy in place

---

**Last Updated:** 2026-01-09
**Security Version:** 1.0
