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
        if os.path.exists(GOOGLE_CREDENTIALS_PATH):
            self.creds = service_account.Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_PATH, scopes=self.SCOPES)
        self.service = build('drive', 'v3', credentials=self.creds)
        
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
            fields='id, webViewLink, webContentLink'
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
