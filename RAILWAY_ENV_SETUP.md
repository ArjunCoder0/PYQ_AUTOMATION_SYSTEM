# Railway Environment Variable Setup

## Problem
GitHub blocks pushing the `google-credentials.json` file because it contains a private key. We need to add it as an environment variable in Railway instead.

## Solution: Add GOOGLE_CREDENTIALS to Railway

### Step 1: Copy the Credentials JSON

Open the file `backend/google-credentials.json` in your project and **copy the entire contents**.

It should look like this (but with your actual values):
```json
{
  "type": "service_account",
  "project_id": "ar-racing-game-8e2d4",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "gug-pyq@ar-racing-game-8e2d4.iam.gserviceaccount.com",
  ...
}
```

### Step 2: Add to Railway Dashboard

1. Go to your Railway project: https://railway.com/project/1b91ebaa-8658-4697-aaa0-046ef7082d3d

2. Click on the **"web"** service

3. Go to the **"Variables"** tab

4. Click **"+ New Variable"**

5. Set:
   - **Variable Name:** `GOOGLE_CREDENTIALS`
   - **Value:** Paste the ENTIRE JSON content you copied (all of it, including the curly braces)

6. Click **"Add"**

### Step 3: Redeploy

Railway will automatically redeploy with the new environment variable.

Wait 2-3 minutes for the deployment to complete.

### Step 4: Test

1. Go to your admin panel: https://unigug-pyq.up.railway.app/admin.html
2. Upload a small test ZIP file
3. You should see:
   - Actual numbers instead of "undefined"
   - Files appearing in your Google Drive folder
   - Success message with correct counts

## Troubleshooting

If it still doesn't work:
- Make sure you copied the ENTIRE JSON (including `{` and `}`)
- Verify the variable name is exactly `GOOGLE_CREDENTIALS` (case-sensitive)
- Check that the Drive folder is shared with `gug-pyq@ar-racing-game-8e2d4.iam.gserviceaccount.com`
- Verify Google Drive API is enabled in Google Cloud Console
