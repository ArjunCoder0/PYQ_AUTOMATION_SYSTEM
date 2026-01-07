"""
Comprehensive Subject Code Prefix Analyzer
Analyzes the ZIP file to find ALL subject code prefixes for each branch
"""
import re

# Simulate analyzing a sample of filenames from your screenshots
# In reality, this would scan the actual ZIP file

sample_filenames = [
    # CSE Papers
    "13801 - Year - B.E. - B.Tech. Computer Science and Engineering (Model Curriculum) Semester-III Subject - SE1BECS - Applied Mathematics-III.pdf",
    "13810 - Year - B.E. - B.Tech. Computer Science and Engineering (Model Curriculum) Semester-IV Subject - SE2BECS - Finance and Accounting.pdf",
    "13811 - Year - B.E. - B.Tech. Computer Science and Engineering (Model Curriculum) Semester-V Subject - TEE101CS - Signals and Systems.pdf",
    "14231 - Year - B.E. Computer Science and Engineering (Model Curriculum) Semester-VII Subject - BE101CS - TCP-IP and Internet.pdf",
    "14339 - Year - B.E. Computer Science and Engineering (Model Curriculum) Semester-VIII Subject - BE201CS - Computer System Security.pdf",
    
    # ME Papers (from database analysis)
    "13xxx - Year - B.E. Mechanical Engineering Semester-III Subject - PCCME301 - Heat Transfer.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-III Subject - HSMC3012 - Production Technology.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-IV Subject - PCC-ME302 - Design of Machine Elements.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-V Subject - PCCME303 - Manufacturing Processes.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-VI Subject - PCC-ME201 - Thermodynamics.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-VI Subject - OEC-4011 - Elective Course.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-VII Subject - PEC-MEL - Professional Elective.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-II Subject - ESC-201 - Engineering Mechanics.pdf",
    "13xxx - Year - B.E. Mechanical Engineering Semester-II Subject - STPCCMEC104 - Thermodynamics.pdf",
    
    # Common courses
    "13165 - Year - B.Tech. (Model Curriculum) Semester-I Subject - BSC101 - Physics.pdf",
    "13166 - Year - B.Tech. (Model Curriculum) Semester-I Subject - ESC102 - Engineering Graphics.pdf",
    "13167 - Year - B.Tech. (Model Curriculum) Semester-II Subject - STBSC201 - Mathematics II.pdf",
]

# Extract subject codes
code_pattern = r'Subject\s*-\s*([A-Z]{2,6}[-]?[A-Z0-9]{1,8})'

branch_prefixes = {
    'CSE': set(),
    'ME': set(),
    'CE': set(),
    'EE': set(),
    'ECE': set(),
    'Common': set()
}

for filename in sample_filenames:
    # Determine branch
    if 'Computer Science' in filename:
        branch = 'CSE'
    elif 'Mechanical' in filename:
        branch = 'ME'
    elif 'Civil' in filename:
        branch = 'CE'
    elif 'Electrical' in filename and 'Electronics' not in filename:
        branch = 'EE'
    elif 'Electronics' in filename or 'Telecommunication' in filename:
        branch = 'ECE'
    else:
        branch = 'Common'
    
    # Extract subject code
    match = re.search(code_pattern, filename)
    if match:
        code = match.group(1)
        # Extract prefix (letters before first digit or hyphen)
        prefix_match = re.match(r'^([A-Z]+)', code)
        if prefix_match:
            prefix = prefix_match.group(1)
            branch_prefixes[branch].add(prefix)

print("=" * 80)
print("SUBJECT CODE PREFIXES BY BRANCH")
print("=" * 80)

for branch, prefixes in sorted(branch_prefixes.items()):
    if prefixes:
        print(f"\n{branch}:")
        print(f"  Prefixes: {sorted(prefixes)}")
        print(f"  Count: {len(prefixes)}")

# All unique prefixes
all_prefixes = set()
for prefixes in branch_prefixes.values():
    all_prefixes.update(prefixes)

print(f"\n{'=' * 80}")
print(f"ALL UNIQUE PREFIXES: {sorted(all_prefixes)}")
print(f"Total: {len(all_prefixes)}")

# Current valid prefixes in system
current_valid = ['BSC', 'ESC', 'PCC', 'HSMC', 'MC', 'OEC', 'PEC', 'ST', 'SE', 'TEE', 'BE', 'UB', 'PS', 'US', 'MMCS', 'STUG', 'STPG', 'BP', 'MPG', 'MPH', 'MED', 'IN', 'ET', 'PSES', 'PEPS', 'PECS', 'PCSS']

print(f"\n{'=' * 80}")
print("COVERAGE CHECK")
print("=" * 80)

missing = []
for prefix in all_prefixes:
    if prefix not in current_valid:
        # Check if it starts with any valid prefix
        covered = any(prefix.startswith(v) for v in current_valid)
        if not covered:
            missing.append(prefix)

if missing:
    print(f"\n⚠️  MISSING PREFIXES: {sorted(missing)}")
    print(f"   These should be added to valid_prefixes list!")
else:
    print(f"\n✅ All prefixes are covered by current valid_prefixes list!")

print(f"\n{'=' * 80}")
print("MECHANICAL ENGINEERING SPECIFIC PREFIXES")
print("=" * 80)
print(f"ME Prefixes: {sorted(branch_prefixes['ME'])}")
print(f"\nThese are the prefixes needed for Mechanical Engineering papers:")
for prefix in sorted(branch_prefixes['ME']):
    print(f"  - {prefix}")
