# Deploying PYQ Automation System to Vercel

## ⚠️ Important Limitations

**Vercel has significant limitations for this project:**

1. **File Storage**: Vercel's serverless functions are stateless - uploaded PDFs won't persist
2. **SQLite Database**: Not recommended for production on Vercel (use PostgreSQL instead)
3. **File Size Limits**: 
   - Max function size: 50MB
   - Max request body: 4.5MB (your ZIP files are likely larger)
4. **Execution Time**: 10-second timeout for Hobby plan

## 🚨 Recommended Alternative: Railway or Render

For a Flask app with file uploads and SQLite, consider:
- **Railway.app** - Better for Python apps with persistent storage
- **Render.com** - Free tier with persistent disk
- **PythonAnywhere** - Designed for Python web apps
- **Heroku** - Classic choice for Flask apps

## 📝 If You Still Want to Deploy on Vercel

### Prerequisites
1. Vercel account (sign up at vercel.com)
2. Vercel CLI installed: `npm install -g vercel`
3. GitHub repository connected

### Steps

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy**
```bash
cd c:\My_Projects\PYQ_AUTOMATION_SYSTEM
vercel
```

4. **Follow the prompts:**
   - Set up and deploy? Yes
   - Which scope? (Select your account)
   - Link to existing project? No
   - Project name? PYQ_AUTOMATION_SYSTEM
   - Directory? ./
   - Override settings? No

### Required Changes for Vercel

1. **Replace SQLite with PostgreSQL** (Vercel doesn't support persistent SQLite)
2. **Use Vercel Blob Storage** for PDF files instead of local filesystem
3. **Reduce ZIP file size limit** to under 4.5MB or use chunked uploads
4. **Add environment variables** in Vercel dashboard

### Environment Variables (Set in Vercel Dashboard)
```
DATABASE_URL=postgresql://...
BLOB_READ_WRITE_TOKEN=...
```

## 🎯 Recommended: Deploy to Railway Instead

Railway is much better suited for this project:

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login**
```bash
railway login
```

3. **Initialize**
```bash
railway init
```

4. **Deploy**
```bash
railway up
```

Railway will:
- ✅ Support SQLite database with persistent storage
- ✅ Handle large file uploads
- ✅ No execution time limits
- ✅ Free tier available

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
