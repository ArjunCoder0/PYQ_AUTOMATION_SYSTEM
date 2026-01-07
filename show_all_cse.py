import sqlite3

conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

print("\n=== ALL CSE PAPERS IN DATABASE ===")
cursor.execute('SELECT semester, subject_code, subject_name, file_path FROM pyq_files WHERE branch="CSE" ORDER BY semester')
for row in cursor.fetchall():
    filename = row[3].split('/')[-1] if '/' in row[3] else row[3].split('\\')[-1]
    print(f'Sem {row[0]}: {row[1]} - {row[2]}')
    print(f'  File: {filename[:80]}...')

print(f"\n=== TOTAL CSE PAPERS: {cursor.rowcount} ===")

# Check all semesters
print("\n=== CSE PAPERS BY SEMESTER ===")
cursor.execute('SELECT semester, COUNT(*) FROM pyq_files WHERE branch="CSE" GROUP BY semester ORDER BY semester')
for row in cursor.fetchall():
    print(f'Semester {row[0]}: {row[1]} papers')

conn.close()
