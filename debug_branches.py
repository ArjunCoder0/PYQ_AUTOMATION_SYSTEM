import sqlite3

conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

print("\n=== CSE PAPERS ===")
cursor.execute('SELECT subject_code, subject_name, semester FROM pyq_files WHERE branch="CSE" ORDER BY semester')
for row in cursor.fetchall():
    print(f'Sem {row[2]}: {row[0]} - {row[1]}')

print("\n=== ECE PAPERS (Sem 1-2, first 15) ===")
cursor.execute('SELECT subject_code, subject_name, semester FROM pyq_files WHERE branch="ECE" AND semester <= 2 LIMIT 15')
for row in cursor.fetchall():
    print(f'Sem {row[2]}: {row[0]} - {row[1]}')

print("\n=== ALL SEMESTER 3+ CSE-like codes ===")
cursor.execute('SELECT branch, semester, subject_code, subject_name FROM pyq_files WHERE semester >= 3 AND (subject_code LIKE "%CS%" OR subject_code LIKE "%IT%") ORDER BY semester LIMIT 20')
for row in cursor.fetchall():
    print(f'{row[0]} Sem {row[1]}: {row[2]} - {row[3]}')

conn.close()
