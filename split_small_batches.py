"""
Split ZIP files into very small batches (max 20 PDFs per ZIP)
This ensures Railway can process them within timeout limits
"""
import zipfile
import os

def split_into_small_batches(input_zip_path, output_dir='small_batches', max_pdfs_per_zip=20):
    """Split ZIP into small batches of max 20 PDFs each"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {input_zip_path}...")
    
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        # Get all PDF files
        pdf_files = [f for f in zip_ref.filelist if f.filename.endswith('.pdf')]
        total_pdfs = len(pdf_files)
        
        print(f"Found {total_pdfs} PDFs")
        print(f"Creating batches of {max_pdfs_per_zip} PDFs each...\n")
        
        # Split into batches
        batch_num = 1
        for i in range(0, total_pdfs, max_pdfs_per_zip):
            batch_files = pdf_files[i:i + max_pdfs_per_zip]
            
            # Create batch ZIP
            batch_name = f"batch_{batch_num:03d}.zip"
            output_zip = os.path.join(output_dir, batch_name)
            
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for file_info in batch_files:
                    file_data = zip_ref.read(file_info.filename)
                    out_zip.writestr(file_info.filename, file_data)
            
            size_mb = os.path.getsize(output_zip) / (1024 * 1024)
            print(f"✓ {batch_name}: {len(batch_files)} PDFs ({size_mb:.2f} MB)")
            
            batch_num += 1
        
        print(f"\n✅ Created {batch_num - 1} batch files in '{output_dir}' folder")
        print(f"Upload each batch separately - they're small enough to process quickly!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python split_small_batches.py <zip_file>")
        print("\nExample:")
        print("  python split_small_batches.py split_zips/CSE.zip")
        sys.exit(1)
    
    input_zip = sys.argv[1]
    
    if not os.path.exists(input_zip):
        print(f"Error: File '{input_zip}' not found!")
        sys.exit(1)
    
    split_into_small_batches(input_zip, max_pdfs_per_zip=20)
