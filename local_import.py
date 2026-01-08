"""
Local ZIP Processor - Generate SQL for Railway Database Import
This script processes the ZIP file locally and generates SQL statements
that can be imported directly into Railway database (no timeout limits)
"""
import zipfile
import os
import re
import sys

# Import the existing processor logic
sys.path.insert(0, 'backend')
from zip_processor import ZIPProcessor

def generate_sql_import(zip_path, exam_type, exam_year, output_sql='import_papers.sql'):
    """
    Process ZIP locally and generate SQL insert statements
    """
    print(f"Processing {zip_path} locally...")
    print("This will take a few minutes but has NO timeout limits!\n")
    
    # Process ZIP
    processor = ZIPProcessor(zip_path, exam_type, exam_year)
    
    # Process with progress callback
    def show_progress(current, total):
        percent = int((current / total) * 100)
        print(f"Progress: {current}/{total} ({percent}%)", end='\r')
    
    result = processor.process(progress_callback=show_progress)
    
    print("\n")
    
    if not result['success']:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return False
    
    # Generate SQL file
    print(f"Generating SQL file: {output_sql}")
    
    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write("-- SQL Import for PYQ Papers\n")
        f.write(f"-- Generated from: {os.path.basename(zip_path)}\n")
        f.write(f"-- Total papers: {len(result['papers'])}\n\n")
        
        for paper in result['papers']:
            # Escape single quotes in strings
            subject_name = paper['subject_name'].replace("'", "''")
            file_path = paper['file_path'].replace("'", "''")
            degree = paper['degree'].replace("'", "''")
            
            sql = f"""INSERT INTO pyq_files (exam_type, exam_year, branch, semester, subject_code, subject_name, file_path, degree)
VALUES ('{paper['exam_type']}', {paper['exam_year']}, '{paper['branch']}', {paper['semester']}, '{paper['subject_code']}', '{subject_name}', '{file_path}', '{degree}');
"""
            f.write(sql)
    
    print(f"\n✅ Success!")
    print(f"   Processed: {result['total_pdfs']} PDFs")
    print(f"   Valid papers: {result['valid_papers']}")
    print(f"   SQL file: {output_sql}")
    print(f"\nNext steps:")
    print(f"1. Import SQL to Railway:")
    print(f"   railway run sqlite3 backend/pyq_system.db < {output_sql}")
    print(f"2. Upload PDFs folder to Railway (if needed)")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python local_import.py <zip_file> <exam_type> <exam_year>")
        print("\nExample:")
        print('  python local_import.py "C:\\Users\\ADMIN\\Downloads\\ScienceTechnology_S25.zip" Summer 2025')
        sys.exit(1)
    
    zip_file = sys.argv[1]
    exam_type = sys.argv[2]
    exam_year = sys.argv[3]
    
    if not os.path.exists(zip_file):
        print(f"Error: File not found: {zip_file}")
        sys.exit(1)
    
    generate_sql_import(zip_file, exam_type, exam_year)
