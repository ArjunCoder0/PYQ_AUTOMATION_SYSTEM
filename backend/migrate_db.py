"""
Database Migration: Add zip_url column to upload_jobs table
Run this once to update existing databases
"""
import sqlite3
import os

def migrate_database():
    """Add zip_url column if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(__file__), 'pyq_database.db')
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet, skipping migration")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(upload_jobs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'zip_url' not in columns:
            print("Adding zip_url column to upload_jobs table...")
            cursor.execute('ALTER TABLE upload_jobs ADD COLUMN zip_url TEXT')
            conn.commit()
            print("✓ Migration complete: zip_url column added")
        else:
            print("✓ zip_url column already exists, no migration needed")
            
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
