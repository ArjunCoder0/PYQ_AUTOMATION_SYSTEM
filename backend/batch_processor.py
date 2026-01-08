"""
Batch Processor - Handles chunked processing of PDFs from uploaded ZIPs
"""
import os
import zipfile
from zip_processor import ZIPProcessor
from database import update_job_progress, update_job_extract_path, get_upload_job, insert_pyq_file
from config import UPLOAD_FOLDER

class BatchProcessor:
    """Processes PDFs in batches to avoid timeouts"""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.job = get_upload_job(job_id)
        
        if not self.job:
            raise ValueError(f"Job {job_id} not found")
        
        self.processor = ZIPProcessor(
            self.job['zip_path'],
            self.job['exam_type'],
            self.job['exam_year']
        )
    
    def extract_zip_if_needed(self):
        """Extract ZIP if not already extracted"""
        if self.job['extract_path'] and os.path.exists(self.job['extract_path']):
            return self.job['extract_path']
        
        # Extract ZIP
        extract_path = self.processor._extract_zip()
        
        # Count total PDFs
        pdf_files = self.processor._find_pdfs(extract_path)
        total_pdfs = len(pdf_files)
        
        # Update job with extract path and total
        update_job_extract_path(self.job_id, extract_path)
        update_job_progress(self.job_id, 0, 'UPLOADED')
        
        # Update job data
        self.job['extract_path'] = extract_path
        self.job['total_pdfs'] = total_pdfs
        
        return extract_path
    
    def process_batch(self, batch_size=15):
        """
        Process next batch of PDFs
        Returns: dict with progress info
        """
        # Ensure ZIP is extracted
        extract_path = self.extract_zip_if_needed()
        
        # Get all PDFs
        all_pdfs = self.processor._find_pdfs(extract_path)
        
        # Get already processed count
        processed_count = self.job['processed_pdfs']
        total_count = len(all_pdfs)
        
        # Check if already completed
        if processed_count >= total_count:
            return {
                'success': True,
                'job_id': self.job_id,
                'processed': processed_count,
                'total': total_count,
                'percentage': 100,
                'status': 'COMPLETED',
                'message': 'All PDFs already processed'
            }
        
        # Get next batch of PDFs to process
        batch_pdfs = all_pdfs[processed_count:processed_count + batch_size]
        
        # Process each PDF in batch
        successfully_processed = 0
        for pdf_path in batch_pdfs:
            try:
                # Parse metadata
                metadata = self.processor._parse_filename(os.path.basename(pdf_path))
                
                if metadata:
                    # Copy to storage
                    new_path = self.processor._copy_to_storage(pdf_path, metadata)
                    
                    if new_path:
                        metadata['file_path'] = new_path
                        
                        # Insert to database
                        insert_pyq_file(metadata)
                        successfully_processed += 1
                        
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
                continue
        
        # Update progress
        new_processed_count = processed_count + successfully_processed
        new_status = 'COMPLETED' if new_processed_count >= total_count else 'PROCESSING'
        
        update_job_progress(self.job_id, new_processed_count, new_status)
        
        # Calculate percentage
        percentage = int((new_processed_count / total_count) * 100) if total_count > 0 else 0
        
        return {
            'success': True,
            'job_id': self.job_id,
            'processed': new_processed_count,
            'total': total_count,
            'percentage': percentage,
            'status': new_status,
            'batch_processed': successfully_processed
        }
