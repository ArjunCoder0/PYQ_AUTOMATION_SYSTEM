"""
ZIP Fetcher - Downloads ZIP files from URLs server-side
Bypasses browser upload limitations by using server-to-server downloads
"""
import requests
import os
from config import UPLOAD_FOLDER

def fetch_zip_from_url(url, filename, timeout=300):
    """
    Download ZIP file from URL with streaming
    
    Args:
        url: Direct download URL for ZIP file
        filename: Name to save the file as
        timeout: Request timeout in seconds (default: 5 minutes)
    
    Returns:
        tuple: (zip_path, file_size)
    
    Raises:
        requests.RequestException: If download fails
    """
    try:
        # Make streaming request
        response = requests.get(url, stream=True, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Prepare file path
        zip_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Download with streaming (memory efficient)
        total_size = 0
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
        
        file_size = os.path.getsize(zip_path)
        print(f"✓ Downloaded {filename}: {file_size / (1024*1024):.2f} MB")
        
        return zip_path, file_size
        
    except requests.Timeout:
        raise Exception(f"Download timeout after {timeout} seconds")
    except requests.RequestException as e:
        raise Exception(f"Download failed: {str(e)}")
    except Exception as e:
        # Clean up partial download
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise Exception(f"Error saving file: {str(e)}")


def validate_zip_url(url):
    """
    Validate that URL is a direct download link
    
    Args:
        url: URL to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
    
    # Must be HTTP/HTTPS
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Should end with .zip (optional but recommended)
    # Some URLs might have query params, so this is lenient
    
    return True
