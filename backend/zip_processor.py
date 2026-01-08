"""
ZIP file processing and PDF metadata extraction
"""
import os
import re
import shutil
import zipfile
from config import UPLOAD_FOLDER, PDF_STORAGE_PATH, SEMESTER_MAPPING, BRANCHES

class ZIPProcessor:
    """
    Handles ZIP file extraction and PDF metadata parsing
    """
    
    def __init__(self, zip_path, exam_type, exam_year):
        self.zip_path = zip_path
        self.exam_type = exam_type
        self.exam_year = exam_year
        self.extracted_files = []
    
    def process(self, progress_callback=None):
        """
        Main processing method:
        1. Extract ZIP
        2. Find all PDFs
        3. Parse filenames
        4. Filter engineering papers only
        5. Copy valid PDFs to storage
        6. Return metadata list
        """
        try:
            # Extract ZIP file
            extract_path = self._extract_zip()
            
            # Find all PDF files
            pdf_files = self._find_pdfs(extract_path)
            
            # DEBUG: Print first 10 filenames
            print(f"\n=== DEBUG: Found {len(pdf_files)} PDFs ===")
            print("Sample filenames (first 10):")
            for i, pdf in enumerate(pdf_files[:10]):
                print(f"{i+1}. {os.path.basename(pdf)}")
            print("=" * 50)
            
            # Process each PDF
            valid_papers = []
            rejected_reasons = {'no_degree': 0, 'no_branch': 0, 'no_semester': 0, 'no_subject_code': 0}
            
            total_pdfs = len(pdf_files)
            
            total_pdfs = len(pdf_files)
            valid_papers = []
            upload_errors = [] # Track errors
            
            for i, pdf_path in enumerate(pdf_files):
                # Report progress
                if progress_callback and i % 10 == 0:
                    progress_callback(i, total_pdfs)
                
                metadata = self._parse_filename(pdf_path)
                if metadata:
                    # Copy PDF to permanent storage
                    new_path = self._copy_to_storage(pdf_path, metadata)
                    if new_path:
                        metadata['file_path'] = new_path
                        metadata['exam_type'] = self.exam_type
                        metadata['exam_year'] = self.exam_year
                        valid_papers.append(metadata)
                    else:
                        upload_errors.append(f"Failed to upload {os.path.basename(pdf_path)}")
            
            # Final progress update
            if progress_callback:
                progress_callback(total_pdfs, total_pdfs)
            
            # Check for total failure
            if not valid_papers and upload_errors:
                 return {
                    'success': False,
                    'error': f'All {total_pdfs} uploads failed. Most likely an authentication error with Google Drive. Check server logs.'
                }

            # Cleanup temporary files
            self._cleanup(extract_path)
            
            return {
                'success': True,
                'total_pdfs': len(pdf_files),
                'valid_papers': len(valid_papers),
                'papers': valid_papers
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_zip(self):
        """Extract ZIP file to temporary directory"""
        extract_path = os.path.join(UPLOAD_FOLDER, f'extract_{self.exam_type}_{self.exam_year}')
        
        # Remove if exists
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        return extract_path
    
    def _find_pdfs(self, directory):
        """Recursively find all PDF files in directory"""
        pdf_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files
    
    def _parse_filename(self, pdf_path):
        """
        Parse PDF filename to extract metadata
        
        University filename format:
        "10632S - Year - B.Sc. - B.Com. - B.Sc. (Information Technology) - B.C.A.- I  (CBCS Pattern) Semester-I Subject - UCA1C02..."
        "13165 - Year - B.E. - B.Tech.  (Model Curriculum) Semester-I and II Subject - BSC101 -  Physics.pdf"
        
        Required:
        - Must contain: "B.Tech" OR "B.E." (NOT B.Sc, B.Com, BCA, etc.)
        - Semester: Roman numerals I-VIII
        - Subject Code: BSC, ESC, PCC, HSMC, MC, etc.
        - Branch: CSE, IT, ME, CE, EE, ECE (Computer, Electrical, Mechanical, Civil, Electronics)
        """
        filename = os.path.basename(pdf_path)
        
        # CRITICAL: Check if it's B.Tech or B.E ONLY (reject B.Sc, B.Com, BCA, B.Pharm, M.Tech, M.Sc, etc.)
        has_btech = re.search(r'\bB\.Tech\b', filename, re.IGNORECASE)
        has_be = re.search(r'\bB\.E\.?\b', filename, re.IGNORECASE)
        has_model = re.search(r'Model\s+Curriculum', filename, re.IGNORECASE)
        
        # Reject if it's NOT B.Tech/B.E
        if not (has_btech or has_be or has_model):
            return None
        
        # Additional rejection: if it contains other degrees, reject
        if re.search(r'\b(B\.Sc|B\.Com|BCA|B\.C\.A|B\.Pharm|M\.Tech|M\.Sc|M\.Pharm|M\.C\.A)', filename, re.IGNORECASE):
            # Only accept if it ALSO has B.Tech or B.E in the same filename
            if not (has_btech or has_be):
                return None
        
        # Determine degree
        if has_btech:
            degree = 'B.Tech'
        elif has_be:
            degree = 'B.E'
        else:
            degree = 'B.Tech'  # Default for Model Curriculum
        
        # Extract semester (look for "Semester-I", "Semester-II", etc.)
        semester = None
        # Pattern: "Semester-I" or "Semester-III" or "Semester I" etc.
        semester_pattern = r'Semester[- ]?(I{1,3}|IV|V|VI{1,2}|VIII?)\b'
        semester_match = re.search(semester_pattern, filename, re.IGNORECASE)
        if semester_match:
            roman = semester_match.group(1).upper()
            semester = SEMESTER_MAPPING.get(roman)
        
        if not semester:
            return None  # Skip if semester not found
        
        # Extract subject code - more flexible pattern
        subject_code = None
        # Patterns: BSC101, ESC-201, PCC-CE304, STBSC101, SE1BECS, SE2BICS, etc.
        # Updated to handle codes with digits in the middle (SE1BECS) or at the end (BSC101)
        code_pattern = r'\b([A-Z]{2,6}[-]?[A-Z0-9]{1,8})\b'
        code_matches = re.findall(code_pattern, filename)
        
        # Filter to get valid subject codes (BSC, ESC, PCC, HSMC, MC, OEC, PEC, ST, SE, TEE, BE prefixes, etc.)
        valid_prefixes = ['BSC', 'ESC', 'PCC', 'HSMC', 'MC', 'OEC', 'PEC', 'ST', 'SE', 'TEE', 'BE', 'UB', 'PS', 'US', 'MMCS', 'STUG', 'STPG', 'BP', 'MPG', 'MPH', 'MED', 'IN', 'ET', 'PSES', 'PEPS', 'PECS', 'PCSS']
        
        for code in code_matches:
            # Check if code starts with any valid prefix
            for prefix in valid_prefixes:
                if code.upper().startswith(prefix):
                    subject_code = code.upper()
                    break
            if subject_code:
                break
        
        if not subject_code:
            return None  # Skip if subject code not found
        
        # Extract branch - look for engineering branches
        branch = None
        
        # IMPROVED: Look for branch name closest to "Engineering" keyword for better accuracy
        # This handles cases like "B.E. Mechanical Engineering (Model Curriculum) Semester-VII Subject - PCC-2 - Irrigation engineering"
        # where we want to extract the branch from "Civil Engineering" not just "Civil"
        
        branch_patterns = {
            'CSE': [
                r'Computer\s+Science\s+(?:and\s+)?Engineering',
                r'\bComputer\s+Science\b',
                r'\bCSE\b',
                r'\bCS\b'
            ],
            'IT': [
                r'Information\s+Technology',
                r'\bIT\b',
                r'\bI\.T\b'
            ],
            'ME': [
                r'Mechanical\s+Engineering',
                r'\bMechanical\b(?!\s*Engineering\s*\(Model)',  # Mechanical but not in "Mechanical Engineering (Model Curriculum)"
                r'\bME\b(?!\s*-)'  # ME but not ME-401 (subject code)
            ],
            'CE': [
                r'Civil\s+Engineering',
                r'\bCivil\b',
                r'\bCE\b(?![\d-])'  # CE but not CE-304 or CE701
            ],
            'EE': [
                r'Electrical\s+(?:Electronics\s+and\s+Power\s+)?Engineering',
                r'Electrical\s+Engineering',
                r'\bElectrical\b',
                r'\bEE\b',
                r'Electronics\s+and\s+Power'
            ],
            'ECE': [
                r'Electronics\s+and\s+(?:Communication|Telecommunication)',
                r'Telecommunication\s+Engineering',
                r'\bElectronics\b(?!\s+and\s+Power)',
                r'\bECE\b',
                r'Instrumentation\s+Engineering'
            ]
        }
        
        # Strategy: Find the branch name that appears closest to the word "Engineering" or "Semester"
        # This helps disambiguate when multiple branch names appear
        
        best_match = None
        best_position = len(filename)
        
        # DEBUG: Track all matches
        all_matches = []
        
        for br, patterns in branch_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    all_matches.append((br, pattern, match.group(), match.start()))
                    # Find position of this match
                    match_pos = match.start()
                    
                    # Prefer matches that are:
                    # 1. Closer to "Engineering" keyword
                    # 2. Closer to "Semester" keyword
                    # 3. Earlier in filename (as tiebreaker)
                    
                    # Look for "Engineering" or "Semester" after this match
                    context = filename[match_pos:]
                    eng_match = re.search(r'\bEngineering\b', context, re.IGNORECASE)
                    sem_match = re.search(r'\bSemester\b', context, re.IGNORECASE)
                    
                    if eng_match:
                        # Distance to "Engineering" keyword
                        distance = eng_match.start()
                    elif sem_match:
                        # Distance to "Semester" keyword
                        distance = sem_match.start()
                    else:
                        # No context keyword found, use position in filename
                        distance = match_pos
                    
                    # Prefer closer matches
                    if distance < best_position:
                        best_position = distance
                        best_match = br
                        branch = br
        
        # DEBUG: Print branch detection results
        if all_matches and not branch:
            print(f"  ⚠️  Found matches but no branch selected: {all_matches}")
        elif all_matches:
            print(f"  ✓ Branch: {branch}, All matches: {all_matches[:3]}")
        
        # If no branch found, try to infer from subject code or use default
        if not branch:
            # Try to infer from subject code prefix or context
            if 'CS' in subject_code or 'IT' in subject_code:
                branch = 'CSE'
            elif 'ME' in subject_code or 'MED' in subject_code:
                branch = 'ME'
            elif 'CE' in subject_code or 'CIV' in subject_code:
                branch = 'CE'
            elif 'EE' in subject_code or 'EL' in subject_code or 'EP' in subject_code:
                branch = 'EE'
            elif 'EC' in subject_code or 'ET' in subject_code or 'IN' in subject_code:
                branch = 'ECE'
            else:
                # Default to CSE if we can't determine
                branch = 'CSE'
        
        # Extract subject name - everything after "Subject -" or after subject code
        subject_name = "Unknown Subject"
        
        # Try pattern: "Subject - CODE - Name.pdf"
        name_pattern1 = rf'Subject\s*-\s*{re.escape(subject_code)}\s*-\s*(.+?)\.pdf'
        name_match = re.search(name_pattern1, filename, re.IGNORECASE)
        
        if name_match:
            subject_name = name_match.group(1)
        else:
            # Try pattern: "CODE - Name.pdf"
            name_pattern2 = rf'{re.escape(subject_code)}\s*-\s*(.+?)\.pdf'
            name_match = re.search(name_pattern2, filename, re.IGNORECASE)
            if name_match:
                subject_name = name_match.group(1)
        
        # Clean up subject name
        subject_name = re.sub(r'[_-]', ' ', subject_name)
        subject_name = re.sub(r'\s+', ' ', subject_name).strip()
        # Remove paper numbers like "Paper-I", "Paper-II"
        subject_name = re.sub(r'\bPaper[-\s]?[IVX]+\b', '', subject_name, flags=re.IGNORECASE)
        subject_name = re.sub(r'\s+', ' ', subject_name).strip()
        
        if subject_name and len(subject_name) > 3:
            subject_name = subject_name.title()
        else:
            subject_name = "Engineering Subject"
        
        return {
            'degree': degree,
            'branch': branch,
            'semester': semester,
            'subject_code': subject_code,
            'subject_name': subject_name
        }
    
    def _copy_to_storage(self, source_path, metadata):
        """
        Copy PDF to local storage on Railway
        Returns: relative file path
        """
        try:
            from config import PDF_STORAGE_PATH
            import shutil
            
            # Generate filename: SubjectCode_SubjectName.pdf
            filename = f"{metadata['subject_code']}_{metadata['subject_name'].replace(' ', '_')}.pdf"
            
            # Ensure storage directory exists
            os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
            
            # Copy to storage
            destination = os.path.join(PDF_STORAGE_PATH, filename)
            shutil.copy2(source_path, destination)
            
            print(f"✓ Copied to local storage: {filename}")
            
            # Return relative path (just the filename)
            return filename
            
        except Exception as e:
            print(f"ERROR copying file: {e}")
            return None
    
    def _cleanup(self, extract_path):
        """Remove temporary extraction directory"""
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        
        # Remove uploaded ZIP file
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
