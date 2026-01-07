"""
Search for ALL possible Mechanical Engineering subject code prefixes
Based on the pattern we found for CSE, ME should have similar patterns
"""

# Expected patterns based on CSE structure:
# CSE had: SE1BECS, SE2BECS (Sem 3-4), TEE101CS (Sem 5-6), BE101CS (Sem 7-8)
# ME should have: SE1BMES, SE2BMES (Sem 3-4), TEE101ME (Sem 5-6), BE101ME (Sem 7-8)

print("=" * 80)
print("EXPECTED MECHANICAL ENGINEERING SUBJECT CODE PREFIXES")
print("=" * 80)

me_prefixes_by_semester = {
    "Semesters 1-2 (Common)": [
        "BSC",      # Basic Science - Physics, Chemistry, Math
        "ESC",      # Engineering Science - Graphics, Programming
        "STBSC",    # ST + BSC
        "STESC",    # ST + ESC
    ],
    
    "Semesters 3-4": [
        "SE1BMES",  # Semester Engineering 1, B.E. Mechanical Engineering
        "SE2BMES",  # Semester Engineering 2, B.E. Mechanical Engineering
        "PCCME",    # Professional Core Course - Mechanical Engineering
        "PCC-ME",   # Professional Core Course - Mechanical Engineering (with hyphen)
        "HSMC",     # Humanities & Social Management Course
        "BSC-ME",   # Basic Science - Mechanical Engineering specific
    ],
    
    "Semesters 5-6": [
        "TEE101ME", # Technical Elective Engineering - Mechanical (if exists)
        "TEE102ME", # Technical Elective Engineering - Mechanical
        "TEEME",    # TEE + ME combined
        "PCCME",    # Professional Core Course - Mechanical Engineering
        "PCC-ME",   # Professional Core Course - Mechanical Engineering
        "OEC",      # Open Elective Course
        "PEC",      # Professional Elective Course
    ],
    
    "Semesters 7-8": [
        "BE101ME",  # Bachelor of Engineering - Mechanical (if exists)
        "BE201ME",  # Bachelor of Engineering - Mechanical
        "BEME",     # BE + ME combined
        "PEC-ME",   # Professional Elective - Mechanical
        "PECMEL",   # Professional Elective Course - Mechanical Elective
        "OEC",      # Open Elective Course
    ],
}

print("\nBased on CSE pattern analysis, ME should have these prefixes:\n")

all_me_prefixes = set()
for semester_range, prefixes in me_prefixes_by_semester.items():
    print(f"{semester_range}:")
    for prefix in prefixes:
        print(f"  - {prefix}")
        all_me_prefixes.add(prefix)
    print()

print("=" * 80)
print(f"ALL UNIQUE ME PREFIXES: {sorted(all_me_prefixes)}")
print(f"Total: {len(all_me_prefixes)}")

# Current valid prefixes
current_valid = ['BSC', 'ESC', 'PCC', 'HSMC', 'MC', 'OEC', 'PEC', 'ST', 'SE', 'TEE', 'BE', 'UB', 'PS', 'US', 'MMCS', 'STUG', 'STPG', 'BP', 'MPG', 'MPH', 'MED', 'IN', 'ET', 'PSES', 'PEPS', 'PECS', 'PCSS']

print("\n" + "=" * 80)
print("COVERAGE CHECK")
print("=" * 80)

covered = []
potentially_missing = []

for prefix in sorted(all_me_prefixes):
    if prefix in current_valid:
        covered.append(prefix)
        print(f"✅ {prefix:15s} - Already in valid_prefixes")
    else:
        # Check if it starts with any valid prefix
        is_covered = False
        for valid in current_valid:
            if prefix.startswith(valid):
                covered.append(prefix)
                print(f"✅ {prefix:15s} - Covered by '{valid}'")
                is_covered = True
                break
        if not is_covered:
            potentially_missing.append(prefix)
            print(f"⚠️  {prefix:15s} - NOT COVERED! Should add to valid_prefixes")

print("\n" + "=" * 80)
if potentially_missing:
    print(f"⚠️  POTENTIALLY MISSING: {potentially_missing}")
    print(f"\nThese prefixes might need to be added to capture all ME papers!")
else:
    print("✅ All ME prefixes should be covered!")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print("\nTo ensure ALL Mechanical Engineering papers are captured,")
print("the valid_prefixes list should include:")
print(f"\n{sorted(all_me_prefixes)}")
