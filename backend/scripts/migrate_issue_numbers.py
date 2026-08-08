"""
Simple script to add issue_number column to existing database
Run this if the migration doesn't work
"""

import sqlite3
import os

# Database path
db_path = "society_app.db"

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking database schema...")

# Check if issue_number column exists
cursor.execute("PRAGMA table_info(issues)")
columns = [col[1] for col in cursor.fetchall()]

if 'issue_number' in columns:
    print("✅ issue_number column already exists")
else:
    print("Adding issue_number column...")
    try:
        # Add column
        cursor.execute("ALTER TABLE issues ADD COLUMN issue_number TEXT")
        print("✅ issue_number column added")
        
        # Update existing issues with sequential numbers
        cursor.execute("SELECT id FROM issues ORDER BY created_at")
        issues = cursor.fetchall()
        
        for idx, (issue_id,) in enumerate(issues, 1):
            issue_number = f"{idx:06d}"
            new_id = f"RGTS-{issue_number}"
            cursor.execute(
                "UPDATE issues SET issue_number = ? WHERE id = ?",
                (issue_number, issue_id)
            )
            print(f"  Updated issue {issue_id} -> RGTS-{issue_number}")
        
        # Now update IDs to RGTS format
        cursor.execute("SELECT id, issue_number FROM issues")
        for old_id, issue_number in cursor.fetchall():
            new_id = f"RGTS-{issue_number}"
            if old_id != new_id:
                cursor.execute("UPDATE issues SET id = ? WHERE id = ?", (new_id, old_id))
                # Also update foreign keys in issue_photos
                cursor.execute("UPDATE issue_photos SET issue_id = ? WHERE issue_id = ?", (new_id, old_id))
                print(f"  Migrated {old_id} -> {new_id}")
        
        conn.commit()
        print("✅ Migration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

conn.close()
print("\n🎉 Done! Restart your server and try again.")
