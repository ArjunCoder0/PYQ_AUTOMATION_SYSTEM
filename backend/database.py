"""
Database initialization and helper functions using SQLAlchemy
Supports both PostgreSQL (production) and SQLite (development)
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

# Detect database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production: PostgreSQL on Railway
    # Normalize postgres:// to postgresql:// for SQLAlchemy compatibility
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    print(f"✓ Using PostgreSQL (production)")
else:
    # Development: SQLite locally
    from config import DATABASE_PATH
    DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
    print(f"✓ Using SQLite (local development)")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
Session = scoped_session(sessionmaker(bind=engine))

# Base class for all models
Base = declarative_base()

# ==================== MODELS ====================

class PyqFile(Base):
    """Model for PYQ file metadata"""
    __tablename__ = 'pyq_files'
    
    id = Column(Integer, primary_key=True)
    degree = Column(String(50), nullable=False)
    branch = Column(String(50), nullable=False)
    semester = Column(Integer, nullable=False)
    subject_code = Column(String(50), nullable=False)
    subject_name = Column(String(255), nullable=False)
    exam_type = Column(String(50), nullable=False)
    exam_year = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Indexes for faster queries
    __table_args__ = (
        Index('idx_exam_session', 'exam_type', 'exam_year'),
        Index('idx_branch_semester', 'branch', 'semester'),
    )

class UploadJob(Base):
    """Model for upload job tracking"""
    __tablename__ = 'upload_jobs'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    zip_path = Column(Text, nullable=False)
    zip_url = Column(Text, nullable=True)
    extract_path = Column(Text, nullable=True)
    exam_type = Column(String(50), nullable=False)
    exam_year = Column(Integer, nullable=False)
    total_pdfs = Column(Integer, default=0)
    processed_pdfs = Column(Integer, default=0)
    status = Column(String(50), default='UPLOADED')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AdminUser(Base):
    """Model for admin user authentication"""
    __tablename__ = 'admin_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)


# ==================== INITIALIZATION ====================

def init_database():
    """Initialize database and create all tables"""
    try:
        Base.metadata.create_all(engine)
        print("✓ Database tables created/verified successfully")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        raise

# ==================== HELPER FUNCTIONS ====================

def get_db_connection():
    """
    Get database session (for backward compatibility)
    Returns a SQLAlchemy session instead of raw connection
    """
    return Session()

# ==================== PYQ FILE FUNCTIONS ====================

def insert_pyq_file(data):
    """Insert a new PYQ file record"""
    session = Session()
    try:
        pyq_file = PyqFile(
            degree=data['degree'],
            branch=data['branch'],
            semester=data['semester'],
            subject_code=data['subject_code'],
            subject_name=data['subject_name'],
            exam_type=data['exam_type'],
            exam_year=data['exam_year'],
            file_path=data['file_path']
        )
        session.add(pyq_file)
        session.commit()
        file_id = pyq_file.id
        return file_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_exam_sessions():
    """Get all unique exam sessions (type + year)"""
    session = Session()
    try:
        results = session.query(
            PyqFile.exam_type,
            PyqFile.exam_year
        ).distinct().order_by(
            PyqFile.exam_year.desc(),
            PyqFile.exam_type
        ).all()
        
        return [{'exam_type': r.exam_type, 'exam_year': r.exam_year} for r in results]
    finally:
        session.close()

def get_branches_by_session(exam_type, exam_year):
    """Get all branches for a specific exam session"""
    session = Session()
    try:
        results = session.query(PyqFile.branch).filter(
            PyqFile.exam_type == exam_type,
            PyqFile.exam_year == exam_year
        ).distinct().order_by(PyqFile.branch).all()
        
        return [r.branch for r in results]
    finally:
        session.close()

def get_subjects(exam_type, exam_year, branch, semester):
    """Get all subjects for specific filters"""
    session = Session()
    try:
        results = session.query(
            PyqFile.subject_code,
            PyqFile.subject_name
        ).filter(
            PyqFile.exam_type == exam_type,
            PyqFile.exam_year == exam_year,
            PyqFile.branch == branch,
            PyqFile.semester == semester
        ).distinct().order_by(PyqFile.subject_code).all()
        
        return [{'subject_code': r.subject_code, 'subject_name': r.subject_name} for r in results]
    finally:
        session.close()

def get_paper_details(exam_type, exam_year, branch, semester, subject_code):
    """Get paper details for specific subject"""
    session = Session()
    try:
        paper = session.query(PyqFile).filter(
            PyqFile.exam_type == exam_type,
            PyqFile.exam_year == exam_year,
            PyqFile.branch == branch,
            PyqFile.semester == semester,
            PyqFile.subject_code == subject_code
        ).first()
        
        if paper:
            return {
                'id': paper.id,
                'degree': paper.degree,
                'branch': paper.branch,
                'semester': paper.semester,
                'subject_code': paper.subject_code,
                'subject_name': paper.subject_name,
                'exam_type': paper.exam_type,
                'exam_year': paper.exam_year,
                'file_path': paper.file_path,
                'created_at': paper.created_at
            }
        return None
    finally:
        session.close()

def get_file_by_id(file_id):
    """Get file details by ID"""
    session = Session()
    try:
        file_data = session.query(PyqFile).filter(PyqFile.id == file_id).first()
        
        if file_data:
            return {
                'id': file_data.id,
                'degree': file_data.degree,
                'branch': file_data.branch,
                'semester': file_data.semester,
                'subject_code': file_data.subject_code,
                'subject_name': file_data.subject_name,
                'exam_type': file_data.exam_type,
                'exam_year': file_data.exam_year,
                'file_path': file_data.file_path,
                'created_at': file_data.created_at
            }
        return None
    finally:
        session.close()

# ==================== UPLOAD JOBS FUNCTIONS ====================

def create_upload_job(filename, zip_path, exam_type, exam_year, total_pdfs, zip_url=None):
    """Create a new upload job record"""
    session = Session()
    try:
        job = UploadJob(
            filename=filename,
            zip_path=zip_path,
            zip_url=zip_url,
            exam_type=exam_type,
            exam_year=exam_year,
            total_pdfs=total_pdfs,
            status='UPLOADED'
        )
        session.add(job)
        session.commit()
        job_id = job.id
        return job_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_upload_job(job_id):
    """Get upload job details by ID"""
    session = Session()
    try:
        job = session.query(UploadJob).filter(UploadJob.id == job_id).first()
        
        if job:
            return {
                'id': job.id,
                'filename': job.filename,
                'zip_path': job.zip_path,
                'zip_url': job.zip_url,
                'extract_path': job.extract_path,
                'exam_type': job.exam_type,
                'exam_year': job.exam_year,
                'total_pdfs': job.total_pdfs,
                'processed_pdfs': job.processed_pdfs,
                'status': job.status,
                'created_at': job.created_at,
                'updated_at': job.updated_at
            }
        return None
    finally:
        session.close()

def update_job_progress(job_id, processed_pdfs, status='PROCESSING'):
    """Update job progress"""
    session = Session()
    try:
        job = session.query(UploadJob).filter(UploadJob.id == job_id).first()
        if job:
            job.processed_pdfs = processed_pdfs
            job.status = status
            job.updated_at = func.now()
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_job_extract_path(job_id, extract_path):
    """Update job extract path"""
    session = Session()
    try:
        job = session.query(UploadJob).filter(UploadJob.id == job_id).first()
        if job:
            job.extract_path = extract_path
            job.updated_at = func.now()
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_all_upload_jobs():
    """Get all upload jobs ordered by creation date"""
    session = Session()
    try:
        jobs = session.query(UploadJob).order_by(UploadJob.created_at.desc()).all()
        
        return [{
            'id': job.id,
            'filename': job.filename,
            'zip_path': job.zip_path,
            'zip_url': job.zip_url,
            'extract_path': job.extract_path,
            'exam_type': job.exam_type,
            'exam_year': job.exam_year,
            'total_pdfs': job.total_pdfs,
            'processed_pdfs': job.processed_pdfs,
            'status': job.status,
            'created_at': job.created_at,
            'updated_at': job.updated_at
        } for job in jobs]
    finally:
        session.close()

if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
