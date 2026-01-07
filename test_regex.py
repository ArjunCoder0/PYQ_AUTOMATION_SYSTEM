import re

# Test the new regex pattern
test_filenames = [
    "13801 - Year - B.E. - B.Tech. Computer Science and Engineering (Model Curriculum) Semester-III Subject - SE1BECS - Applied Mathematics-III.pdf",
    "13802 - Year - B.E. - B.Tech. Computer Science and Engineering (Model Curriculum) Semester-III Subject - SE2BECS - Data Structure and Algorithms.pdf",
    "13165 - Year - B.Tech. (Model Curriculum) Semester-I and II Subject - BSC101 - Physics.pdf",
    "13756 - Year - M.Sc. Second Year (Mathematics) (New CBCS Pattern) Semester-III Subject - PSCMTH2 - Functional Analysis.pdf"
]

# Old pattern
old_pattern = r'\b([A-Z]{2,6}[-]?[A-Z]{0,4}\d{3,4}[A-Z]?)\b'

# New pattern  
new_pattern = r'\b([A-Z]{2,6}[-]?[A-Z0-9]{1,8})\b'

valid_prefixes = ['BSC', 'ESC', 'PCC', 'HSMC', 'MC', 'OEC', 'PEC', 'ST', 'SE', 'UB', 'PS', 'US', 'MMCS', 'STUG', 'STPG', 'BP', 'MPG', 'MPH', 'MED', 'IN', 'ET', 'PSES', 'PEPS', 'PECS', 'PCSS']

for filename in test_filenames:
    print(f"\n{'='*80}")
    print(f"File: {filename[:80]}...")
    
    print(f"\nOLD PATTERN:")
    old_matches = re.findall(old_pattern, filename)
    for match in old_matches:
        for prefix in valid_prefixes:
            if match.upper().startswith(prefix):
                print(f"  ✓ {match}")
                break
    
    print(f"\nNEW PATTERN:")
    new_matches = re.findall(new_pattern, filename)
    for match in new_matches:
        for prefix in valid_prefixes:
            if match.upper().startswith(prefix):
                print(f"  ✓ {match}")
                break
