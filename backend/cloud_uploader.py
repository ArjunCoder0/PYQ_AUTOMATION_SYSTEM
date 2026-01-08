import os
import cloudinary
import cloudinary.uploader
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

class CloudUploader:
    """Handles file uploads to Cloudinary"""
    
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
        print(f"✓ Cloudinary configured: {CLOUDINARY_CLOUD_NAME}")
    
    def upload_file(self, file_path, filename, folder_id=None):
        """
        Upload a file to Cloudinary
        Returns: secure_url for both view and download
        """
        try:
            # Remove .pdf extension from filename for public_id
            public_id = filename.replace('.pdf', '')
            
            # Upload to Cloudinary as raw file (for PDFs)
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="raw",  # PDFs must use 'raw' type
                public_id=public_id,
                folder="pyq_pdfs",
                overwrite=True,
                timeout=60  # 60 second timeout per file
            )
            
            print(f"✓ Uploaded to Cloudinary: {result['secure_url']}")
            
            return {
                'file_id': result['public_id'],
                'view_link': result['secure_url'],
                'download_link': result['secure_url']
            }
        except Exception as e:
            print(f"ERROR uploading to Cloudinary: {e}")
            raise
