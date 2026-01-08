"""
Configuration settings for PYQ Management System
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Upload and storage paths
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads', 'temp')
PDF_STORAGE_PATH = os.path.join(PROJECT_ROOT, 'uploads', 'pdfs')
DATABASE_PATH = os.path.join(BASE_DIR, 'pyq_system.db')

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

# File upload settings
ALLOWED_EXTENSIONS = {'zip'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_STORAGE_PATH, exist_ok=True)

# Supported branches
BRANCHES = ['CSE', 'IT', 'ME', 'CE', 'EE', 'ECE']

# Semester mapping (Roman to numeric)
SEMESTER_MAPPING = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4,
    'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8
}
