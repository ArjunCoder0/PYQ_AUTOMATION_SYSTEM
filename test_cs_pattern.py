import re

# Test filename - typical Computer Science Semester 3+ pattern
test_filenames = [
    "13165 - Year - B.Tech. Computer Science Engineering (Model Curriculum) Semester-III Subject - PCC-CS301 - Data Structures.pdf",
    "13166 - Year - B.E. Computer Science (Model Curriculum) Semester-IV Subject - PCC-CS401 - Database Management.pdf",
    "13167 - Year - B.Tech Computer Science Semester-V Subject - PCC-CS501 - Operating Systems.pdf"
]

branch_patterns = {
    'CSE': [
        r'Computer\s+Science\s+(?:and\s+)?Engineering',
        r'\bComputer\s+Science\b',
        r'\bCSE\b',
        r'\bCS\b'
    ]
}

for filename in test_filenames:
    print(f"\n=== Testing: {filename[:80]}...")
    
    for br, patterns in branch_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                print(f"  ✓ Pattern '{pattern}' matched: '{match.group()}' at position {match.start()}")
                
                # Check for "Engineering" keyword
                context = filename[match.start():]
                eng_match = re.search(r'\bEngineering\b', context, re.IGNORECASE)
                sem_match = re.search(r'\bSemester\b', context, re.IGNORECASE)
                
                if eng_match:
                    print(f"    → 'Engineering' found at distance {eng_match.start()}")
                if sem_match:
                    print(f"    → 'Semester' found at distance {sem_match.start()}")
