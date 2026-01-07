"""
Quick script to check what's in the database
"""
import sqlite3

conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

# Check total records
cursor.execute('SELECT COUNT(*) FROM pyq_files')
total = cursor.fetchone()[0]
print(f"\n=== DATABASE STATUS ===")
print(f"Total papers in database: {total}")

if total > 0:
    # Show sample records
    print("\n=== SAMPLE RECORDS (first 10) ===")
    cursor.execute('SELECT degree, branch, semester, subject_code, subject_name, exam_type, exam_year FROM pyq_files LIMIT 10')
    for row in cursor.fetchall():
        print(f"Degree: {row[0]}, Branch: {row[1]}, Sem: {row[2]}, Code: {row[3]}, Name: {row[4]}, Session: {row[5]} {row[6]}")
    
    # Show branch distribution
    print("\n=== BRANCH DISTRIBUTION ===")
    cursor.execute('SELECT branch, COUNT(*) FROM pyq_files GROUP BY branch')
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} papers")
    
    # Show semester distribution
    print("\n=== SEMESTER DISTRIBUTION ===")
    cursor.execute('SELECT semester, COUNT(*) FROM pyq_files GROUP BY semester ORDER BY semester')
    for row in cursor.fetchall():
        print(f"Semester {row[0]}: {row[1]} papers")
    
    # Check for CE Semester 2
    print("\n=== CE SEMESTER 2 PAPERS ===")
    cursor.execute('SELECT subject_code, subject_name FROM pyq_files WHERE branch="CE" AND semester=2 AND exam_type="Summer" AND exam_year=2025')
    ce_papers = cursor.fetchall()
    if ce_papers:
        for row in ce_papers:
            print(f"  {row[0]} - {row[1]}")
    else:
        print("  No papers found for CE Semester 2 Summer 2025")

conn.close()
