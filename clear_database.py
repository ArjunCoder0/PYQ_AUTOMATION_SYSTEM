import sqlite3

# Connect to database
conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

# Show current papers
print("Current papers in database:")
cursor.execute('SELECT id, subject_code, subject_name, file_path FROM pyq_files')
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Code: {row[1]}, Name: {row[2]}, Path: {row[3][:50]}...")

print("\n" + "="*80)
choice = input("\nDo you want to DELETE ALL papers? (yes/no): ")

if choice.lower() == 'yes':
    cursor.execute('DELETE FROM pyq_files')
    conn.commit()
    print("✓ All papers deleted!")
    print("\nNow upload your ZIP file again via the admin panel.")
    print("The new upload will store Cloudinary URLs in the database.")
else:
    print("No changes made.")

conn.close()
