import os
import re

# Search for all Mechanical Engineering PDFs
pdf_dir = 'uploads/pdfs'
me_files = []

if os.path.exists(pdf_dir):
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            # Check if it's a Mechanical Engineering file
            if 'Mechanical' in filename or 'MECH' in filename.upper():
                me_files.append(filename)

print(f"=== FOUND {len(me_files)} MECHANICAL ENGINEERING PDFs ===\n")

# Extract subject codes and prefixes
subject_codes = []
code_pattern = r'\b([A-Z]{2,6}[-]?[A-Z0-9]{1,8})\b'

for filename in me_files[:30]:  # Show first 30
    # Extract semester
    sem_match = re.search(r'Semester[- ]?(I{1,3}|IV|V|VI{1,2}|VIII?)', filename, re.IGNORECASE)
    semester = sem_match.group(1) if sem_match else '?'
    
    # Extract subject code
    matches = re.findall(code_pattern, filename)
    
    # Find the subject code (usually after "Subject")
    subject_idx = filename.find('Subject')
    if subject_idx > 0:
        after_subject = filename[subject_idx:]
        codes_after = re.findall(code_pattern, after_subject)
        if codes_after:
            code = codes_after[0]
            # Extract prefix
            prefix_match = re.match(r'^([A-Z]+)', code)
            if prefix_match:
                prefix = prefix_match.group(1)
                subject_codes.append((semester, code, prefix))
                print(f"Sem {semester:4s}: {code:15s} → Prefix: {prefix}")

# Get unique prefixes
unique_prefixes = set(item[2] for item in subject_codes)
print(f"\n=== UNIQUE PREFIXES FOUND IN ME FILES ===")
print(sorted(unique_prefixes))

# Check which might be missing from valid list
valid_prefixes = ['BSC', 'ESC', 'PCC', 'HSMC', 'MC', 'OEC', 'PEC', 'ST', 'SE', 'TEE', 'BE', 'UB', 'PS', 'US', 'MMCS', 'STUG', 'STPG', 'BP', 'MPG', 'MPH', 'MED', 'IN', 'ET', 'PSES', 'PEPS', 'PECS', 'PCSS']

missing = []
for prefix in unique_prefixes:
    found = False
    for valid in valid_prefixes:
        if prefix.startswith(valid):
            found = True
            break
    if not found:
        missing.append(prefix)

if missing:
    print(f"\n⚠️  MISSING PREFIXES (not in valid list): {sorted(missing)}")
else:
    print(f"\n✅ All prefixes are covered!")
