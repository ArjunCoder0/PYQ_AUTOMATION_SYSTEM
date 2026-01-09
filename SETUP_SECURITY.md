# Quick Security Setup Guide

## 🚀 Getting Started with Secure Admin Access

### Step 1: Install Dependencies

```bash
cd c:\My_Projects\PYQ_AUTOMATION_SYSTEM
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

1. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

2. **Generate a secure SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Edit `.env` file** and set:
   ```bash
   SECRET_KEY=<paste-generated-key-here>
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<your-secure-password>
   
   # Cloudinary (if using cloud storage)
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

### Step 3: Run the Application

```bash
cd backend
python app.py
```

The application will:
- Initialize the database
- Create the admin user
- Start on `http://localhost:5000`

### Step 4: Access Admin Panel

1. **Open your browser** and navigate to:
   ```
   http://localhost:5000/internal/uni-pyq-control-83F9/login
   ```

2. **Login** with your credentials:
   - Username: `admin` (or what you set in `.env`)
   - Password: (what you set in `.env`)

3. **You're in!** The admin dashboard will load.

### Step 5: Test the Security

✅ **Try accessing without login:**
- Go to `http://localhost:5000/internal/uni-pyq-control-83F9/dashboard`
- You should be redirected to login

✅ **Test rate limiting:**
- Try logging in with wrong password 5 times
- You should be locked out temporarily

✅ **Test session timeout:**
- Login successfully
- Wait 24 hours (or modify JWT_EXPIRATION_HOURS in security.py for testing)
- Try to use admin functions - should redirect to login

## 🌐 Deploying to Railway

### Step 1: Set Environment Variables in Railway

1. Go to your Railway project
2. Click on **Variables**
3. Add each variable from your `.env` file:
   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

### Step 2: Deploy

```bash
git add .
git commit -m "Add secure authentication system"
git push origin main
```

Railway will automatically deploy.

### Step 3: Access Your Production Admin

```
https://your-app.railway.app/internal/uni-pyq-control-83F9/login
```

## 🔒 Important Security Notes

### DO:
✅ Use a strong, unique SECRET_KEY in production
✅ Use a strong admin password (12+ characters)
✅ Keep the secret URL private
✅ Use HTTPS in production (Railway provides this automatically)
✅ Monitor login attempts in logs
✅ Change default passwords immediately

### DON'T:
❌ Commit `.env` file to git (it's in `.gitignore`)
❌ Share admin credentials via email/chat
❌ Use simple passwords like "admin123"
❌ Share the secret admin URL publicly
❌ Reuse passwords from other services

## 🆘 Troubleshooting

### "Admin user initialization error"
- Make sure `ADMIN_PASSWORD` is set in `.env`
- Check that the database file can be created

### "Invalid credentials" when logging in
- Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`
- Check console logs for the generated password if not set

### "Session expired" immediately after login
- Check that `SECRET_KEY` is set and consistent
- Verify system time is correct

### Can't access admin dashboard
- Make sure you're using the correct secret URL
- Check that you're logged in (token in sessionStorage)
- Look for errors in browser console (F12)

## 📚 Next Steps

1. Read [SECURITY.md](SECURITY.md) for comprehensive security documentation
2. Test all security features locally
3. Deploy to Railway with proper environment variables
4. Monitor logs for security events
5. Set up regular backups

## 🎯 Quick Reference

### Secret URLs
- **Login:** `/internal/uni-pyq-control-83F9/login`
- **Dashboard:** `/internal/uni-pyq-control-83F9/dashboard`

### API Endpoints (Require Authentication)
- `POST /api/auth/login` - Login
- `GET /api/auth/verify` - Verify token
- `POST /api/auth/logout` - Logout
- `POST /api/auth/change-password` - Change password
- `POST /api/admin/upload` - Upload ZIP
- `POST /api/admin/fetch-zip` - Fetch ZIP from URL
- `POST /api/admin/process-batch/<job_id>` - Process batch
- `GET /api/admin/job-status/<job_id>` - Get job status
- `GET /api/admin/jobs` - Get all jobs

### Environment Variables
```bash
SECRET_KEY=<random-hex-string>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<secure-password>
CLOUDINARY_CLOUD_NAME=<your-cloud>
CLOUDINARY_API_KEY=<your-key>
CLOUDINARY_API_SECRET=<your-secret>
```

---

**Need help?** Check [SECURITY.md](SECURITY.md) for detailed documentation.
