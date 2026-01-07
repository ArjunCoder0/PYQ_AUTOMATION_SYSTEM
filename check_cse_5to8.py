import sqlite3

conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

print("\n=== CSE PAPERS BY SEMESTER ===")
cursor.execute('SELECT semester, COUNT(*) FROM pyq_files WHERE branch="CSE" GROUP BY semester ORDER BY semester')
cse_sems = cursor.fetchall()
for row in cse_sems:
    print(f'Semester {row[0]}: {row[1]} papers')

total_cse = sum(row[1] for row in cse_sems)
print(f'\nTotal CSE papers: {total_cse}')

print("\n=== CSE SEMESTER 5-8 PAPERS ===")
cursor.execute('SELECT semester, subject_code, subject_name FROM pyq_files WHERE branch="CSE" AND semester >= 5 ORDER BY semester')
for row in cursor.fetchall():
    print(f'Sem {row[0]}: {row[1]} - {row[2]}')

print("\n=== ALL SEMESTER 5 PAPERS (all branches) ===")
cursor.execute('SELECT branch, subject_code, subject_name FROM pyq_files WHERE semester=5 ORDER BY branch')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} - {row[2]}')

conn.close()
