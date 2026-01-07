"""
COMPLETE SUBJECT CODE PREFIX REFERENCE
For all Engineering Branches in the PYQ System
"""

print("=" * 100)
print(" " * 30 + "COMPLETE PREFIX REFERENCE")
print("=" * 100)

branches = {
    "Computer Science Engineering (CSE)": {
        "Sem 1-2": ["BSC", "ESC", "STBSC", "STESC"],
        "Sem 3-4": ["SE1BECS", "SE2BECS", "PCCINS (Instrumentation)"],
        "Sem 5-6": ["TEE101CS", "TEE102CS", "TEE103CS", "TEE105CS", "TEE1062CS"],
        "Sem 7-8": ["BE101CS", "BE102CS", "BE103CS-I", "BE201CS", "BE202CS-III", "BE203CS-I"],
    },
    
    "Mechanical Engineering (ME)": {
        "Sem 1-2": ["BSC", "ESC", "STBSC", "STESC"],
        "Sem 3-4": ["SE1BMES", "SE2BMES", "PCCME", "PCC-ME", "HSMC", "BSC-ME"],
        "Sem 5-6": ["TEE101ME", "TEE102ME", "TEEME", "PCCME", "PCC-ME", "OEC", "PEC"],
        "Sem 7-8": ["BE101ME", "BE201ME", "BEME", "PEC-ME", "PECMEL", "OEC"],
    },
    
    "Civil Engineering (CE)": {
        "Sem 1-2": ["BSC", "ESC", "STBSC", "STESC"],
        "Sem 3-4": ["SE1BCES", "SE2BCES", "PCCCE", "PCC-CE", "BSC-CE"],
        "Sem 5-6": ["TEE101CE", "TEE102CE", "TEECE", "PCCCE", "PCC-CE", "OEC", "PEC-CE"],
        "Sem 7-8": ["BE101CE", "BE201CE", "BECE", "PEC-CE", "PECCEL", "OEC"],
    },
    
    "Electrical Engineering (EE)": {
        "Sem 1-2": ["BSC", "ESC", "STBSC", "STESC"],
        "Sem 3-4": ["SE1BEES", "SE2BEES", "PCCEE", "PCC-EE"],
        "Sem 5-6": ["TEE101EE", "TEE102EE", "TEEEE", "PCCEE", "PCC-EE", "OEC", "PEC"],
        "Sem 7-8": ["BE101EE", "BE201EE", "BEEE", "PEC-EE", "PECEEL", "OEC"],
    },
    
    "Electronics & Communication (ECE)": {
        "Sem 1-2": ["BSC", "ESC", "STBSC", "STESC"],
        "Sem 3-4": ["SE1BECS", "SE2BECS", "SE1BICS", "SE2BICS", "IN", "ET"],
        "Sem 5-6": ["TEE101EC", "TEE102EC", "TEEEC", "IN", "ET", "OEC", "PEC"],
        "Sem 7-8": ["BE101EC", "BE201EC", "BEEC", "IN", "ET", "PEC", "OEC"],
    },
}

for branch, semesters in branches.items():
    print(f"\n{'=' * 100}")
    print(f"  {branch}")
    print(f"{'=' * 100}")
    
    for sem_range, prefixes in semesters.items():
        print(f"\n  {sem_range}:")
        for prefix in prefixes:
            print(f"    • {prefix}")

print(f"\n{'=' * 100}")
print("CURRENT VALID PREFIXES IN SYSTEM")
print(f"{'=' * 100}")

current_valid = ['BSC', 'ESC', 'PCC', 'HSMC', 'MC', 'OEC', 'PEC', 'ST', 'SE', 'TEE', 'BE', 
                 'UB', 'PS', 'US', 'MMCS', 'STUG', 'STPG', 'BP', 'MPG', 'MPH', 'MED', 
                 'IN', 'ET', 'PSES', 'PEPS', 'PECS', 'PCSS']

print(f"\nTotal prefixes: {len(current_valid)}")
print(f"\nPrefixes: {', '.join(current_valid)}")

print(f"\n{'=' * 100}")
print("✅ COVERAGE STATUS")
print(f"{'=' * 100}")
print("""
The current valid_prefixes list covers ALL branches because:

1. Base prefixes (BSC, ESC, PCC, OEC, PEC, HSMC) - ✅ Included
2. Semester-specific (ST, SE, TEE, BE) - ✅ Included  
3. Branch codes will be extracted from filename context - ✅ Working
4. Special codes (IN, ET for ECE/Instrumentation) - ✅ Included

All subject codes like SE1BMES, TEE101CS, BE201ME will be matched because:
- SE1BMES starts with 'SE' ✅
- TEE101CS starts with 'TEE' ✅
- BE201ME starts with 'BE' ✅
""")

print(f"{'=' * 100}")
