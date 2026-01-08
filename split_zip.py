                                                            """
Split large ZIP file into smaller ZIPs by branch
This helps avoid Railway's upload size limits
"""
import zipfile
import os
from collections import defaultdict

def split_zip_by_branch(input_zip_path, output_dir='split_zips'):
    """Split ZIP file into separate ZIPs per branch"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store files by branch
    branch_files = defaultdict(list)
    
    print(f"Reading {input_zip_path}...")
    
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        # Group files by branch
        for file_info in zip_ref.filelist:
            if file_info.filename.endswith('.pdf'):
                # Extract branch from filename
                # Example: "13803 - Year - B.E. - B.Tech. Computer Science and Engineering..."
                filename = file_info.filename
                
                # Determine branch based on keywords
                if 'Computer Science' in filename or 'CSE' in filename:
                    branch = 'CSE'
                elif 'Electronics' in filename or 'ECE' in filename:
                    branch = 'ECE'
                elif 'Mechanical' in filename or 'ME' in filename:
                    branch = 'ME'
                elif 'Civil' in filename or 'CE' in filename:
                    branch = 'CE'
                elif 'Electrical' in filename or 'EE' in filename:
                    branch = 'EE'
                else:
                    branch = 'OTHER'
                
                branch_files[branch].append(file_info.filename)
        
        # Create separate ZIP for each branch
        for branch, files in branch_files.items():
            output_zip = os.path.join(output_dir, f'{branch}.zip')
            print(f"\nCreating {output_zip} with {len(files)} files...")
            
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for filename in files:
                    # Read file from original ZIP
                    file_data = zip_ref.read(filename)
                    # Write to new ZIP
                    out_zip.writestr(filename, file_data)
            
            # Get size
            size_mb = os.path.getsize(output_zip) / (1024 * 1024)
            print(f"  ✓ {output_zip} created ({size_mb:.2f} MB)")
    
    print(f"\n✅ Done! Created {len(branch_files)} ZIP files in '{output_dir}' folder")
    print("\nNow upload each ZIP file separately to the admin panel:")
    for branch in sorted(branch_files.keys()):
        output_zip = os.path.join(output_dir, f'{branch}.zip')
        size_mb = os.path.getsize(output_zip) / (1024 * 1024)
        print(f"  - {branch}.zip ({size_mb:.2f} MB, {len(branch_files[branch])} papers)")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python split_zip.py <path_to_large_zip_file>")
        print("\nExample:")
        print("  python split_zip.py ScienceTechnology_S25.zip")
        sys.exit(1)
    
    input_zip = sys.argv[1]
    
    if not os.path.exists(input_zip):
        print(f"Error: File '{input_zip}' not found!")
        sys.exit(1)
    
    split_zip_by_branch(input_zip)
