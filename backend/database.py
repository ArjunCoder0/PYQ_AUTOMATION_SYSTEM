"""
Database initialization and helper functions
"""
import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_database():
    """Initialize database and create tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create pyq_files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pyq_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            degree TEXT NOT NULL,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            exam_year INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create upload_jobs table for chunked processing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            zip_path TEXT NOT NULL,
            zip_url TEXT,
            extract_path TEXT,
            exam_type TEXT NOT NULL,
            exam_year INTEGER NOT NULL,
            total_pdfs INTEGER DEFAULT 0,
            processed_pdfs INTEGER DEFAULT 0,
            status TEXT DEFAULT 'UPLOADED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migration: Add zip_url column if it doesn't exist in existing databases
    try:
        cursor.execute("PRAGMA table_info(upload_jobs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'zip_url' not in columns:
            print("Running migration: Adding zip_url column to upload_jobs...")
            cursor.execute('ALTER TABLE upload_jobs ADD COLUMN zip_url TEXT')
            print("✓ Migration complete: zip_url column added")
    except Exception as e:
        print(f"Migration check error (this is normal for new databases): {e}")
    
    # Create indexes for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_exam_session 
        ON pyq_files(exam_type, exam_year)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_branch_semester 
        ON pyq_files(branch, semester)
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def insert_pyq_file(data):
    """Insert a new PYQ file record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO pyq_files 
        (degree, branch, semester, subject_code, subject_name, exam_type, exam_year, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['degree'],
        data['branch'],
        data['semester'],
        data['subject_code'],
        data['subject_name'],
        data['exam_type'],
        data['exam_year'],
        data['file_path']
    ))
    
    conn.commit()
    file_id = cursor.lastrowid
    conn.close()
    return file_id

def get_exam_sessions():
    """Get all unique exam sessions (type + year)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT exam_type, exam_year 
        FROM pyq_files 
        ORDER BY exam_year DESC, exam_type
    ''')
    
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def get_branches_by_session(exam_type, exam_year):
    """Get all branches for a specific exam session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT branch 
        FROM pyq_files 
        WHERE exam_type = ? AND exam_year = ?
        ORDER BY branch
    ''', (exam_type, exam_year))
    
    branches = [row['branch'] for row in cursor.fetchall()]
    conn.close()
    return branches

def get_subjects(exam_type, exam_year, branch, semester):
    """Get all subjects for specific filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT subject_code, subject_name 
        FROM pyq_files 
        WHERE exam_type = ? AND exam_year = ? AND branch = ? AND semester = ?
        ORDER BY subject_code
    ''', (exam_type, exam_year, branch, semester))
    
    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return subjects

def get_paper_details(exam_type, exam_year, branch, semester, subject_code):
    """Get paper details for specific subject"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM pyq_files 
        WHERE exam_type = ? AND exam_year = ? AND branch = ? 
        AND semester = ? AND subject_code = ?
        LIMIT 1
    ''', (exam_type, exam_year, branch, semester, subject_code))
    
    paper = cursor.fetchone()
    conn.close()
    return dict(paper) if paper else None

def get_file_by_id(file_id):
    """Get file details by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pyq_files WHERE id = ?', (file_id,))
    file_data = cursor.fetchone()
    conn.close()
    return dict(file_data) if file_data else None

# ==================== UPLOAD JOBS FUNCTIONS ====================

def create_upload_job(filename, zip_path, exam_type, exam_year, total_pdfs, zip_url=None):
    """Create a new upload job record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO upload_jobs 
        (filename, zip_path, zip_url, exam_type, exam_year, total_pdfs, status)
        VALUES (?, ?, ?, ?, ?, ?, 'UPLOADED')
    ''', (filename, zip_path, zip_url, exam_type, exam_year, total_pdfs))
    
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id

def get_upload_job(job_id):
    """Get upload job details by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM upload_jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    return dict(job) if job else None

def update_job_progress(job_id, processed_pdfs, status='PROCESSING'):
    """Update job progress"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE upload_jobs 
        SET processed_pdfs = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (processed_pdfs, status, job_id))
    
    conn.commit()
    conn.close()

def update_job_extract_path(job_id, extract_path):
    """Update job extract path"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE upload_jobs 
        SET extract_path = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (extract_path, job_id))
    
    conn.commit()
    conn.close()

def get_all_upload_jobs():
    """Get all upload jobs ordered by creation date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM upload_jobs 
        ORDER BY created_at DESC
    ''')
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs

if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
