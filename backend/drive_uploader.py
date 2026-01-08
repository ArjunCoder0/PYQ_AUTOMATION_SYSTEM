import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from config import GOOGLE_CREDENTIALS_PATH, DRIVE_FOLDER_ID

class DriveUploader:
    """Handles file uploads to Google Drive"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        self.creds = None
        
        # Try to load from environment variable first (for Railway)
        import json
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        
        if creds_json:
            # Load from environment variable
            try:
                print("Loading credentials from GOOGLE_CREDENTIALS environment variable...")
                creds_dict = json.loads(creds_json)
                print(f"Credentials loaded. Service account: {creds_dict.get('client_email', 'unknown')}")
                self.creds = service_account.Credentials.from_service_account_info(
                    creds_dict, scopes=self.SCOPES)
                print("✓ Credentials authenticated successfully")
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse GOOGLE_CREDENTIALS JSON: {e}")
                print("Make sure the environment variable contains valid JSON")
            except Exception as e:
                print(f"ERROR loading credentials from environment: {e}")
        elif os.path.exists(GOOGLE_CREDENTIALS_PATH):
            # Fall back to file (for local development)
            print(f"Loading credentials from file: {GOOGLE_CREDENTIALS_PATH}")
            self.creds = service_account.Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_PATH, scopes=self.SCOPES)
            print("✓ Credentials loaded from file")
        
        if not self.creds:
            error_msg = "Google credentials not found! Set GOOGLE_CREDENTIALS environment variable or provide google-credentials.json file."
            print(f"CRITICAL ERROR: {error_msg}")
            raise Exception(error_msg)
            
        self.service = build('drive', 'v3', credentials=self.creds)
        print("✓ Google Drive service initialized")
        
    def upload_file(self, file_path, filename, folder_id=None):
        """
        Upload a file to Google Drive
        Returns: webViewLink (view) and webContentLink (download)
        """
        if not folder_id:
            folder_id = DRIVE_FOLDER_ID
            
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(
            io.FileIO(file_path, 'rb'), 
            mimetype='application/pdf',
            resumable=True
        )
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink',
            supportsAllDrives=True
        ).execute()
        
        # Make file public (optional, but good for easy access without auth issues for students)
        self._make_file_public(file.get('id'))
        
        return {
            'file_id': file.get('id'),
            'view_link': file.get('webViewLink'),
            'download_link': file.get('webContentLink')
        }
    
    def _make_file_public(self, file_id):
        """Make the file publicly readable"""
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader',
            }
            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id',
            ).execute()
        except Exception as e:
            print(f"Error making file public: {e}")
