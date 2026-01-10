"""
Configuration settings for PYQ Management System
Supports both local development and Railway deployment with persistent storage
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Check if running on Railway with volume
RAILWAY_VOLUME = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH')

if RAILWAY_VOLUME:
    # Production: Use Railway volume for persistent storage
    print(f"✓ Using Railway volume: {RAILWAY_VOLUME}")
    UPLOAD_FOLDER = os.path.join(RAILWAY_VOLUME, 'uploads', 'temp')
    PDF_STORAGE_PATH = os.path.join(RAILWAY_VOLUME, 'uploads', 'pdfs')
    DATABASE_PATH = os.path.join(RAILWAY_VOLUME, 'pyq_system.db')
else:
    # Development: Use local paths
    print("✓ Using local storage paths")
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads', 'temp')
    PDF_STORAGE_PATH = os.path.join(PROJECT_ROOT, 'uploads', 'pdfs')
    DATABASE_PATH = os.path.join(BASE_DIR, 'pyq_system.db')

# Cloudinary Configuration (for PDF storage)
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

# File upload settings
ALLOWED_EXTENSIONS = {'zip'}
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

# Supported branches
BRANCHES = ['CSE', 'IT', 'ME', 'CE', 'EE', 'ECE']

# Semester mapping (Roman to numeric)
SEMESTER_MAPPING = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4,
    'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8
}

def ensure_directories():
    """Create necessary directories if they don't exist"""
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
        print(f"✓ Created directories: {UPLOAD_FOLDER}, {PDF_STORAGE_PATH}")
    except Exception as e:
        print(f"⚠️ Could not create directories: {e}")
