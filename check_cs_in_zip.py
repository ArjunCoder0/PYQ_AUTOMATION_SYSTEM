import zipfile
import os

zip_path = 'uploads/temp/Summer_2025.zip'

if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        all_pdfs = [f for f in z.namelist() if f.endswith('.pdf')]
        
        print(f"Total PDFs in ZIP: {len(all_pdfs)}\n")
        
        # Find Computer Science papers
        cs_papers = [f for f in all_pdfs if 'Computer' in f and 'Science' in f]
        print(f"Files with 'Computer Science': {len(cs_papers)}\n")
        
        # Group by semester
        for sem_num in ['III', 'IV', 'V', 'VI', 'VII', 'VIII']:
            sem_papers = [f for f in cs_papers if f'Semester-{sem_num}' in f]
            print(f"Semester-{sem_num}: {len(sem_papers)} papers")
            if sem_papers:
                print(f"  Sample: {os.path.basename(sem_papers[0])[:100]}")
        
        print("\n=== First 5 Computer Science Semester-III papers ===")
        cs_sem3 = [f for f in cs_papers if 'Semester-III' in f][:5]
        for f in cs_sem3:
            print(f"  {os.path.basename(f)}")
else:
    print(f"ZIP file not found at: {zip_path}")
