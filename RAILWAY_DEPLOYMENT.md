# Railway Deployment Guide for PYQ Automation System

## 🚀 Quick Deploy to Railway

### Method 1: Deploy from GitHub (Recommended)

1. **Go to Railway Dashboard**
   - Visit: https://railway.app/
   - Click "Login" and sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `ArjunCoder0/PYQ_AUTOMATION_SYSTEM`
   - Click "Deploy Now"

3. **Railway will automatically:**
   - ✅ Detect Python project
   - ✅ Install dependencies from `requirements.txt`
   - ✅ Run the app using the `Procfile`
   - ✅ Provide a public URL

4. **Configure Environment Variables** (Optional)
   - Go to your project → Variables
   - Add any needed variables (currently none required)

5. **Access Your App**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Frontend: `https://your-app.railway.app/`
   - Admin: `https://your-app.railway.app/admin.html`
   - API: `https://your-app.railway.app/api/health`

### Method 2: Deploy using Railway CLI

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login to Railway**
```bash
railway login
```

3. **Initialize Project**
```bash
cd c:\My_Projects\PYQ_AUTOMATION_SYSTEM
railway init
```

4. **Link to GitHub Repo** (if not already linked)
```bash
railway link
```

5. **Deploy**
```bash
railway up
```

6. **Generate Domain**
```bash
railway domain
```

## 📁 Project Structure for Railway

```
PYQ_AUTOMATION_SYSTEM/
├── backend/
│   ├── app.py              # Main Flask app
│   ├── requirements.txt    # Python dependencies
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   └── zip_processor.py
├── frontend/
│   ├── index.html          # Student portal
│   ├── admin.html          # Admin panel
│   ├── styles.css
│   └── *.js
├── Procfile                # Railway start command
├── runtime.txt             # Python version
├── railway.json            # Railway configuration
└── README.md
```

## ⚙️ Configuration Files Created

### 1. `Procfile`
Tells Railway how to start your app:
```
web: gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT
```

### 2. `runtime.txt`
Specifies Python version:
```
python-3.11.0
```

### 3. `railway.json`
Railway-specific configuration

### 4. `requirements.txt` (Updated)
Added `gunicorn` for production server

## 🔧 Important Notes

### File Storage
- ✅ Railway provides persistent disk storage
- ✅ Uploaded PDFs will persist across deployments
- ✅ SQLite database will be preserved

### Database
- ✅ SQLite works perfectly on Railway
- ✅ Database file stored in `backend/pyq_system.db`
- ✅ Automatic backups available in paid plans

### File Upload Limits
- ✅ Default: 100MB per request
- ✅ Can be increased in Railway settings
- ✅ Your 500MB ZIP limit will work fine

### Environment Variables (if needed later)
```bash
# Set via CLI
railway variables set FLASK_ENV=production

# Or via Railway Dashboard
# Project → Variables → Add Variable
```

## 🌐 Accessing Your Deployed App

After deployment, you'll get a URL like:
```
https://pyq-automation-system-production.up.railway.app
```

### Endpoints:
- **Student Portal:** `/` or `/index.html`
- **Admin Panel:** `/admin.html`
- **API Health Check:** `/api/health`
- **Upload ZIP:** `/api/admin/upload` (POST)
- **Get Sessions:** `/api/sessions` (GET)
- **Get Branches:** `/api/branches` (GET)

## 📊 Monitoring

1. **View Logs**
   - Railway Dashboard → Your Project → Deployments → View Logs
   - Or via CLI: `railway logs`

2. **Check Metrics**
   - CPU usage
   - Memory usage
   - Request count
   - Response times

## 💰 Pricing

- **Free Tier:**
  - $5 free credit per month
  - 500 hours of usage
  - Perfect for development and small projects

- **Paid Plans:**
  - Start at $5/month
  - More resources and features
  - Custom domains

## 🔄 Updating Your Deployment

### Automatic Deployments (GitHub)
Railway automatically redeploys when you push to GitHub:
```bash
git add .
git commit -m "Update app"
git push origin main
```

### Manual Deployment (CLI)
```bash
railway up
```

## 🐛 Troubleshooting

### App not starting?
1. Check logs: `railway logs`
2. Verify `Procfile` is correct
3. Ensure all dependencies in `requirements.txt`

### Database issues?
1. Check if `backend/pyq_system.db` exists
2. Verify file permissions
3. Check Railway volume settings

### File upload failing?
1. Increase request size limit in Railway settings
2. Check disk space in Railway dashboard
3. Verify `uploads/` directory exists

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Python Guide](https://docs.railway.app/guides/python)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)

## ✅ Next Steps After Deployment

1. **Test the deployment:**
   - Visit your Railway URL
   - Upload a test ZIP file
   - Verify PDF download works

2. **Set up custom domain** (optional):
   - Railway Dashboard → Settings → Domains
   - Add your custom domain

3. **Enable automatic backups** (optional):
   - Upgrade to paid plan
   - Enable database backups

4. **Monitor usage:**
   - Check Railway dashboard regularly
   - Monitor free tier credits

---

**Your app is now ready to deploy to Railway! 🚀**
