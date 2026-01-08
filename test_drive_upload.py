import os
import sys

# Add backend to path to import modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.drive_uploader import DriveUploader
    from backend.config import DRIVE_FOLDER_ID
except ImportError:
    # If running from root
    sys.path.append('backend')
    from backend.drive_uploader import DriveUploader
    from backend.config import DRIVE_FOLDER_ID

def test_upload():
    print("=== Testing Google Drive Upload ===")
    print(f"Folder ID: {DRIVE_FOLDER_ID}")
    
    # Create a dummy PDF file
    test_filename = 'test_upload_debug.pdf'
    with open(test_filename, 'wb') as f:
        f.write(b'%PDF-1.4\n%Test PDF content')
    
    try:
        print("Initializing DriveUploader...")
        uploader = DriveUploader()
        
        print(f"Uploading {test_filename}...")
        result = uploader.upload_file(test_filename, test_filename)
        
        print("\n✅ Upload Successful!")
        print(f"File ID: {result['file_id']}")
        print(f"View Link: {result['view_link']}")
        print(f"Download Link: {result['download_link']}")
        
    except Exception as e:
        print(f"\n❌ Upload Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == '__main__':
    test_upload()
