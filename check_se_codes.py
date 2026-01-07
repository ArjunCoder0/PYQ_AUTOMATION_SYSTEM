import sqlite3

conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

print("\n=== ALL CSE PAPERS ===")
cursor.execute('SELECT semester, subject_code, subject_name FROM pyq_files WHERE branch="CSE" ORDER BY semester')
for row in cursor.fetchall():
    print(f'Sem {row[0]}: {row[1]} - {row[2]}')

print("\n=== PAPERS WITH SE PREFIX ===")
cursor.execute('SELECT branch, semester, subject_code, subject_name FROM pyq_files WHERE subject_code LIKE "SE%" ORDER BY branch, semester')
for row in cursor.fetchall():
    print(f'{row[0]} Sem {row[1]}: {row[2]} - {row[3]}')

print("\n=== ALL SEMESTER 3-4 PAPERS ===")
cursor.execute('SELECT branch, semester, subject_code, subject_name FROM pyq_files WHERE semester IN (3, 4) ORDER BY branch, semester LIMIT 30')
for row in cursor.fetchall():
    print(f'{row[0]} Sem {row[1]}: {row[2]} - {row[3]}')

conn.close()
