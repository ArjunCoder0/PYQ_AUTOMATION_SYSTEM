"""
Test script to verify Google Drive credentials are working
Run this locally to test the Drive upload functionality
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

def test_credentials():
    print("=== Testing Google Drive Credentials ===\n")
    
    try:
        from drive_uploader import DriveUploader
        print("✓ DriveUploader imported successfully")
        
        # Try to initialize
        uploader = DriveUploader()
        print("✓ DriveUploader initialized (credentials loaded)")
        
        # Create a test file
        test_file = "test_upload.txt"
        with open(test_file, 'w') as f:
            f.write("Test file for Drive upload verification")
        
        print(f"✓ Created test file: {test_file}")
        
        # Try to upload
        print("\nAttempting upload to Google Drive...")
        result = uploader.upload_file(test_file, "TEST_UPLOAD.txt")
        
        print("\n✅ SUCCESS! Upload completed:")
        print(f"   File ID: {result['file_id']}")
        print(f"   View Link: {result['view_link']}")
        print(f"   Download Link: {result['download_link']}")
        
        # Cleanup
        os.remove(test_file)
        print(f"\n✓ Cleaned up test file")
        
        print("\n🎉 All tests passed! Drive integration is working correctly.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nPossible issues:")
        print("1. Google Drive API not enabled")
        print("2. Service Account doesn't have access to the folder")
        print("3. Credentials file is missing or malformed")
        print("4. GOOGLE_CREDENTIALS environment variable not set correctly")

if __name__ == '__main__':
    test_credentials()
