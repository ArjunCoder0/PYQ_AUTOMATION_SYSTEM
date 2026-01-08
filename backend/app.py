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

# Configure Flask to serve frontend files
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# Global task storage
upload_tasks = {}

# Initialize database on startup
init_database()

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
def admin_upload():
    """
    Admin endpoint to upload ZIP file
    Expects: ZIP file, exam_type (Summer/Winter), exam_year
    Returns: task_id for tracking progress
    """
    try:
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
            return jsonify({'success': False, 'error': 'File too large (max 500MB)'}), 400
        
        # Create background task
        task_id = str(uuid.uuid4())
        upload_tasks[task_id] = {
            'status': 'processing',
            'processed': 0,
            'total': 0,
            'percent': 0
        }
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_zip_background,
            args=(task_id, zip_path, exam_type, exam_year)
        )
        thread.start()
        
        return jsonify({
            'success': True, 
            'task_id': task_id,
            'message': 'File uploaded, processing started in background'
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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

@app.route('/admin.html')
def admin():
    """Serve admin panel"""
    return send_file('../frontend/admin.html')

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'PYQ Management System API is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
