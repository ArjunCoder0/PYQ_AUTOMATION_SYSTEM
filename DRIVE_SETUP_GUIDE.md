# Google Drive Setup Guide

## Current Issue
Files are not being uploaded to Google Drive. The upload completes but shows "0 papers processed".

## Required Steps to Fix

### 1. Enable Google Drive API ✅ (You've done this)
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Select project: `ar-racing-game-8e2d4`
- Navigate to "APIs & Services" → "Library"
- Search for "Google Drive API"
- Click "Enable"

### 2. Share Drive Folder with Service Account ⚠️ **CRITICAL STEP**

The Service Account email is:
```
gug-pyq@ar-racing-game-8e2d4.iam.gserviceaccount.com
```

**Steps:**
1. Open your Google Drive folder: https://drive.google.com/drive/folders/17FRtcjvUMBI5HGm2xyvOC0DqwLydZr8i
2. Right-click the folder → Click "Share"
3. In the "Add people and groups" field, paste:
   ```
   gug-pyq@ar-racing-game-8e2d4.iam.gserviceaccount.com
   ```
4. Set permission to **"Editor"** (not Viewer!)
5. **UNCHECK** "Notify people" (it's a robot account)
6. Click "Share"

### 3. Verify Permissions

After sharing, the Service Account should appear in the folder's "Shared with" list.

## Testing

Once you've shared the folder:
1. Go to Railway admin panel
2. Upload a small test ZIP (0.03 MB)
3. Check if files appear in the Drive folder
4. The success message should show actual numbers instead of "undefined"

## Troubleshooting

If it still doesn't work:
- Make sure the folder ID is correct: `17FRtcjvUMBI5HGm2xyvOC0DqwLydZr8i`
- Verify the Service Account has "Editor" permissions (not just "Viewer")
- Check Railway logs for specific error messages
