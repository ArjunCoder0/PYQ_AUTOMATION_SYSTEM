# Railway Environment Variables - Cloudinary Setup

## Add These Variables to Railway

Go to Railway Dashboard → Your Project → "web" service → "Variables" tab

### Add the following 3 variables:

1. **Variable Name:** `CLOUDINARY_CLOUD_NAME`
   **Value:** `dm773kjwz`

2. **Variable Name:** `CLOUDINARY_API_KEY`
   **Value:** `687918188116863`

3. **Variable Name:** `CLOUDINARY_API_SECRET`
   **Value:** `PYI29_p4_AY0zMXCHfwEbagBnGw`

## After Adding

Railway will automatically redeploy (takes 2-3 minutes).

## Then Test

1. Go to admin panel: https://unigug-pyq.up.railway.app/admin.html
2. Upload your test ZIP file
3. Check Cloudinary dashboard: https://console.cloudinary.com/console/dm773kjwz/media_library
4. You should see files appearing in the `pyq_pdfs` folder!

## Cleanup (Optional)

You can now delete the old Google Drive environment variable:
- `GOOGLE_CREDENTIALS` (no longer needed)
