"""
Flask application for PYQ Management System
Main API endpoints for admin upload and user filtering
"""
from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER, PDF_STORAGE_PATH, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from database import (
    init_database, insert_pyq_file, get_exam_sessions, 
    get_branches_by_session, get_subjects, get_paper_details, get_file_by_id
)
from zip_processor import ZIPProcessor
from security import require_auth, add_security_headers, validate_file_upload
from auth import auth_bp, init_admin_user

# Configure Flask to serve frontend files
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# Register authentication blueprint
app.register_blueprint(auth_bp)

# Global task storage
upload_tasks = {}

# Initialize database on startup
try:
    init_database()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization error: {e}")
    print("Continuing without database initialization...")

# Create directories after database init
from config import ensure_directories
ensure_directories()

# Initialize admin user
try:
    init_admin_user()
except Exception as e:
    print(f"⚠️ Admin user initialization error: {e}")

# Add security headers to all responses
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== ADMIN ENDPOINTS ====================

def process_zip_background(task_id, zip_path, exam_type, exam_year):
    """Background task to process ZIP file and upload to Cloudinary"""
    try:
        upload_tasks[task_id]['status'] = 'processing'
        
        # Initialize processor
        processor = ZIPProcessor(zip_path, exam_type, int(exam_year)) # Keep int(exam_year) as per original
        
        # Process ZIP - this now uploads to Cloudinary incrementally
        result = processor.process(progress_callback=lambda current, total: 
            upload_tasks[task_id].update({
                'progress': {
                    'current': current,
                    'total': total,
                    'percentage': int((current / total) * 100) if total > 0 else 0
                }
            })
        )
        
        if result['success']:
            # Insert valid papers into database
            inserted_count = 0
            for paper in result['papers']:
                try:
                    insert_pyq_file(paper)
                    inserted_count += 1
                except Exception as e:
                    print(f"Error inserting paper: {e}")
            
            upload_tasks[task_id].update({
                'status': 'completed',
                'result': {
                    'success': True,
                    'message': f'Successfully processed {inserted_count} papers',
                    'total_pdfs': result['total_pdfs'],
                    'valid_papers': result['valid_papers'],
                    'inserted': inserted_count
                }
            })
        else:
             upload_tasks[task_id].update({
                'status': 'failed',
                'error': result.get('error', 'Unknown error during processing')
            })
            
    except Exception as e:
        upload_tasks[task_id].update({
            'status': 'failed',
            'error': str(e)
        })

@app.route('/api/admin/upload', methods=['POST'])
@require_auth
def admin_upload():
    """
    NEW: Upload ZIP and create job (no extraction, no processing)
    Returns: job_id for batch processing
    """
    try:
        from database import create_upload_job
        
        # Validate request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        exam_type = request.form.get('exam_type')
        exam_year = request.form.get('exam_year')
        
        if not exam_type or not exam_year:
            return jsonify({'success': False, 'error': 'Exam type and year required'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only ZIP files allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        zip_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(zip_path)
        
        # Check file size
        if os.path.getsize(zip_path) > MAX_FILE_SIZE:
            os.remove(zip_path)
            return jsonify({'success': False, 'error': 'File too large (max 1GB)'}), 400
        
        # Create job record (extraction will happen on first batch process)
        job_id = create_upload_job(filename, zip_path, exam_type, int(exam_year), 0)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'filename': filename,
            'total_pdfs': 0,  # Will be counted on first batch
            'status': 'UPLOADED',
            'message': f'Upload complete! Click "Process Next Batch" to start.'
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/fetch-zip', methods=['POST'])
@require_auth
def fetch_zip():
    """
    NEW: Fetch ZIP from URL (server-side download)
    Downloads asynchronously to avoid worker timeout
    Returns: job_id immediately
    """
    try:
        from database import create_upload_job
        from zip_fetcher import fetch_zip_from_url, validate_zip_url
        import threading
        
        # Get request data
        data = request.get_json()
        zip_url = data.get('url')
        exam_type = data.get('exam_type')
        exam_year = data.get('exam_year')
        
        # Validate inputs
        if not zip_url or not exam_type or not exam_year:
            return jsonify({'success': False, 'error': 'URL, exam type, and year required'}), 400
        
        if not validate_zip_url(zip_url):
            return jsonify({'success': False, 'error': 'Invalid URL format'}), 400
        
        # Generate filename
        filename = f"{exam_type}_{exam_year}.zip"
        
        # Create job record immediately with status FETCHING
        job_id = create_upload_job(filename, '', exam_type, int(exam_year), 0, zip_url=zip_url, status='FETCHING')
        
        # Download ZIP in background thread
        def download_in_background():
            try:
                print(f"Background download starting for job {job_id}: {zip_url}")
                zip_path, file_size = fetch_zip_from_url(zip_url, filename)
                
                # Check file size
                if file_size > MAX_FILE_SIZE:
                    os.remove(zip_path)
                    # Update job status to FAILED
                    update_job_progress(job_id, 0, 'FAILED')
                    print(f"Job {job_id} failed: File too large")
                    return
                
                # Update job with zip_path and status UPLOADED
                from database import Session, UploadJob
                session = Session()
                try:
                    job = session.query(UploadJob).filter(UploadJob.id == job_id).first()
                    if job:
                        job.zip_path = zip_path
                        job.status = 'UPLOADED'
                        session.commit()
                finally:
                    session.close()
                print(f"Job {job_id} download complete: {file_size / (1024*1024):.2f} MB")
                
            except Exception as e:
                print(f"Background download failed for job {job_id}: {e}")
                # Update job status to FAILED
                update_job_progress(job_id, 0, 'FAILED')
        
        # Start background thread
        thread = threading.Thread(target=download_in_background)
        thread.daemon = True
        thread.start()
        
        # Return immediately
        return jsonify({
            'success': True,
            'job_id': job_id,
            'filename': filename,
            'status': 'FETCHING',
            'message': f'Download started! The server is fetching the ZIP file. Check status in a few moments.'
        }), 200
    
    except Exception as e:
        print(f"Error creating fetch job: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/process-batch/<int:job_id>', methods=['POST'])
@require_auth
def process_batch(job_id):
    """
    Process next batch of PDFs for a job
    Query params: batch_size (default: 15)
    """
    try:
        from batch_processor import BatchProcessor
        
        batch_size = request.args.get('batch_size', 15, type=int)
        
        processor = BatchProcessor(job_id)
        result = processor.process_batch(batch_size)
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/recent-job', methods=['GET'])
@require_auth
def get_recent_job():
    """Get the most recent upload job"""
    try:
        from database import Session, UploadJob
        session = Session()
        job = None
        try:
            job = session.query(UploadJob).order_by(UploadJob.created_at.desc()).first()
            if job:
                return jsonify({
                    'success': True,
                    'job': {
                        'id': job.id,
                        'filename': job.filename,
                        'status': job.status,
                        'total_pdfs': job.total_pdfs,
                        'processed_pdfs': job.processed_pdfs
                    }
                })
        finally:
            session.close()
        
        return jsonify({'success': False, 'message': 'No recent jobs'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/job-status/<int:job_id>', methods=['GET'])
@require_auth
def get_job_status(job_id):
    """Get current status of an upload job"""
    try:
        from database import get_upload_job
        
        job = get_upload_job(job_id)
        
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        percentage = int((job['processed_pdfs'] / job['total_pdfs']) * 100) if job['total_pdfs'] > 0 else 0
        
        return jsonify({
            'success': True,
            'job_id': job['id'],
            'filename': job['filename'],
            'processed': job['processed_pdfs'],
            'total': job['total_pdfs'],
            'percentage': percentage,
            'status': job['status'],
            'created_at': job['created_at'],
            'updated_at': job['updated_at']
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/jobs', methods=['GET'])
@require_auth
def get_all_jobs():
    """Get all upload jobs"""
    try:
        from database import get_all_upload_jobs
        
        jobs = get_all_upload_jobs()
        
        # Add percentage to each job
        for job in jobs:
            job['percentage'] = int((job['processed_pdfs'] / job['total_pdfs']) * 100) if job['total_pdfs'] > 0 else 0
        
        return jsonify({
            'success': True,
            'jobs': jobs
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Keep old task endpoint for backwards compatibility
@app.route('/api/admin/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of background task"""
    task = upload_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    return jsonify({'success': True, 'task': task}), 200

# ==================== USER FILTER ENDPOINTS ====================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all available exam sessions"""
    try:
        sessions = get_exam_sessions()
        # Format as "Summer 2025", "Winter 2024", etc.
        formatted = [
            {
                'label': f"{s['exam_type']} {s['exam_year']}",
                'exam_type': s['exam_type'],
                'exam_year': s['exam_year']
            }
            for s in sessions
        ]
        return jsonify({'success': True, 'sessions': formatted}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/branches', methods=['GET'])
def get_branches():
    """Get branches for selected session"""
    try:
        exam_type = request.args.get('exam_type')
        exam_year = request.args.get('exam_year')
        
        if not exam_type or not exam_year:
            return jsonify({'success': False, 'error': 'Session parameters required'}), 400
        
        branches = get_branches_by_session(exam_type, int(exam_year))
        return jsonify({'success': True, 'branches': branches}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subjects', methods=['GET'])
def get_subjects_list():
    """Get subjects for selected session, branch, and semester"""
    try:
        exam_type = request.args.get('exam_type')
        exam_year = request.args.get('exam_year')
        branch = request.args.get('branch')
        semester = request.args.get('semester')
        
        if not all([exam_type, exam_year, branch, semester]):
            return jsonify({'success': False, 'error': 'All filter parameters required'}), 400
        
        subjects = get_subjects(exam_type, int(exam_year), branch, int(semester))
        return jsonify({'success': True, 'subjects': subjects}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paper', methods=['GET'])
def get_paper():
    """Get paper details for selected subject"""
    try:
        exam_type = request.args.get('exam_type')
        exam_year = request.args.get('exam_year')
        branch = request.args.get('branch')
        semester = request.args.get('semester')
        subject_code = request.args.get('subject_code')
        
        if not all([exam_type, exam_year, branch, semester, subject_code]):
            return jsonify({'success': False, 'error': 'All parameters required'}), 400
        
        paper = get_paper_details(exam_type, int(exam_year), branch, int(semester), subject_code)
        
        if not paper:
            return jsonify({'success': False, 'error': 'Paper not found'}), 404
        
        return jsonify({'success': True, 'paper': paper}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PDF ENDPOINTS ====================

@app.route('/api/pdf/view/<int:file_id>', methods=['GET'])
def view_pdf(file_id):
    """View PDF in browser"""
    try:
        file_data = get_file_by_id(file_id)
        if not file_data:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # If it's a Cloudinary URL (starts with http), redirect to it
        if file_data['file_path'].startswith('http'):
            return redirect(file_data['file_path'])
        
        # Fallback for local files (legacy support)
        pdf_path = os.path.join(PDF_STORAGE_PATH, file_data['file_path'])
        
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'PDF file not found on server'}), 404
        
        return send_file(pdf_path, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pdf/download/<int:file_id>', methods=['GET'])
def download_pdf(file_id):
    """Download PDF file"""
    try:
        file_data = get_file_by_id(file_id)
        if not file_data:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # If it's a Cloudinary URL (starts with http), redirect to it
        if file_data['file_path'].startswith('http'):
            return redirect(file_data['file_path'])
        
        # Fallback for local files (legacy support)
        pdf_path = os.path.join(PDF_STORAGE_PATH, file_data['file_path'])
        
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'PDF file not found on server'}), 404
        
        # Generate download filename
        download_name = f"{file_data['subject_code']}_{file_data['subject_name'].replace(' ', '_')}.pdf"
        
        return send_file(pdf_path, as_attachment=True, download_name=download_name)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Serve student portal"""
    return send_file('../frontend/index.html')

# Secret admin routes (non-discoverable)
@app.route('/internal/uni-pyq-control-83F9/login')
def admin_login():
    """Serve admin login page (secret URL)"""
    return send_file('../frontend/admin_login.html')

@app.route('/internal/uni-pyq-control-83F9/dashboard')
def admin_dashboard():
    """Serve admin dashboard (requires authentication)"""
    return send_file('../frontend/admin.html')

# Legacy admin.html route - redirect to secret login
@app.route('/admin.html')
def admin_legacy():
    """Redirect old admin URL to secret login"""
    return redirect('/internal/uni-pyq-control-83F9/login')

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'PYQ Management System API is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
