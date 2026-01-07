import sqlite3

# First, let's see what ME papers we currently have
conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

print("=== CURRENT ME PAPERS IN DATABASE ===")
cursor.execute('SELECT semester, COUNT(*) FROM pyq_files WHERE branch="ME" GROUP BY semester ORDER BY semester')
me_sems = cursor.fetchall()
for row in me_sems:
    print(f'Semester {row[0]}: {row[1]} papers')

print("\n=== ME SUBJECT CODE PREFIXES ===")
cursor.execute('SELECT DISTINCT subject_code FROM pyq_files WHERE branch="ME" ORDER BY subject_code')
me_codes = cursor.fetchall()

# Extract prefixes (first 2-6 letters before numbers)
import re
prefixes = set()
for code in me_codes:
    # Extract prefix (letters before first digit)
    match = re.match(r'^([A-Z]+)', code[0])
    if match:
        prefixes.add(match.group(1))
        print(f'{code[0]} → Prefix: {match.group(1)}')

print(f"\n=== UNIQUE ME PREFIXES ===")
print(sorted(prefixes))

conn.close()
