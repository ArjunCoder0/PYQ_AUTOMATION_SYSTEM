"""
Split OTHER.zip into smaller ZIPs by semester
"""
import zipfile
import os
import re
from collections import defaultdict

def split_by_semester(input_zip_path, output_dir='split_zips'):
    """Split ZIP file into separate ZIPs per semester"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    semester_files = defaultdict(list)
    
    print(f"Reading {input_zip_path}...")
    
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            if file_info.filename.endswith('.pdf'):
                filename = file_info.filename
                
                # Try to extract semester from filename
                # Look for patterns like "Semester-I", "Semester-II", etc.
                semester_match = re.search(r'Semester[- ]([IVX]+|[1-8])', filename, re.IGNORECASE)
                
                if semester_match:
                    sem = semester_match.group(1).upper()
                    # Convert Roman numerals to numbers if needed
                    roman_to_num = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 
                                   'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8'}
                    semester = roman_to_num.get(sem, sem)
                else:
                    semester = 'UNKNOWN'
                
                semester_files[semester].append(file_info.filename)
        
        # Create separate ZIP for each semester
        for semester, files in sorted(semester_files.items()):
            output_zip = os.path.join(output_dir, f'OTHER_Sem{semester}.zip')
            print(f"\nCreating {output_zip} with {len(files)} files...")
            
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as out_zip:
                for filename in files:
                    file_data = zip_ref.read(filename)
                    out_zip.writestr(filename, file_data)
            
            size_mb = os.path.getsize(output_zip) / (1024 * 1024)
            print(f"  ✓ {output_zip} created ({size_mb:.2f} MB)")
    
    print(f"\n✅ Done! Created {len(semester_files)} ZIP files")
    for semester in sorted(semester_files.keys()):
        output_zip = os.path.join(output_dir, f'OTHER_Sem{semester}.zip')
        size_mb = os.path.getsize(output_zip) / (1024 * 1024)
        print(f"  - OTHER_Sem{semester}.zip ({size_mb:.2f} MB, {len(semester_files[semester])} papers)")

if __name__ == '__main__':
    split_by_semester('split_zips/OTHER.zip')
