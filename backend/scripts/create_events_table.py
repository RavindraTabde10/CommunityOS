"""
Direct SQL Migration for Events Table
Creates the events table directly in SQLite database
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "society_app.db"

print("=" * 70)
print("CREATING EVENTS TABLE")
print("=" * 70)
print()

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if events table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    if cursor.fetchone():
        print("⚠️  Events table already exists!")
        print()
    else:
        # Create events table
        cursor.execute("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                event_type VARCHAR(20) NOT NULL,
                venue VARCHAR(200),
                start_datetime DATETIME NOT NULL,
                end_datetime DATETIME,
                is_active BOOLEAN DEFAULT 1,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX ix_events_id ON events (id)")
        cursor.execute("CREATE INDEX ix_events_start_datetime ON events (start_datetime)")
        cursor.execute("CREATE INDEX ix_events_is_active ON events (is_active)")
        
        conn.commit()
        print("✅ Events table created successfully!")
        print()
    
    # Insert sample events for testing
    print("📝 Creating sample events...")
    
    sample_events = [
        ("Annual Committee Meeting", "Discuss society maintenance and future plans", "meeting", 
         "Clubhouse Main Hall", "2026-08-31 18:00:00", "2026-08-31 20:00:00", 1, 1),
        ("Diwali Celebration 2026", "Community Diwali celebration with cultural programs", "festival",
         "Community Garden", "2026-11-01 17:00:00", "2026-11-01 22:00:00", 1, 1),
        ("Water Tank Cleaning", "Annual water tank cleaning and sanitization", "maintenance",
         "Building A, B, C Roof", "2026-09-15 08:00:00", "2026-09-15 16:00:00", 1, 1),
    ]
    
    for event in sample_events:
        try:
            cursor.execute("""
                INSERT INTO events (title, description, event_type, venue, start_datetime, end_datetime, is_active, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, event)
        except sqlite3.IntegrityError:
            pass  # Event already exists
    
    conn.commit()
    print("✅ Sample events created!")
    print()
    
    # Show created events
    cursor.execute("SELECT id, title, event_type, start_datetime FROM events ORDER BY start_datetime")
    events = cursor.fetchall()
    
    if events:
        print("📅 Current Events:")
        print("-" * 70)
        for event_id, title, event_type, start_dt in events:
            print(f"  {event_id}. {title} ({event_type}) - {start_dt}")
        print("-" * 70)
    
    conn.close()
    
    print()
    print("🎉 Events feature is ready!")
    print()
    print("Next steps:")
    print("  1. Restart the backend server (if running)")
    print("  2. Refresh the dashboard - events should now appear!")
    print("  3. Create more events via Swagger UI: http://127.0.0.1:8000/api/docs")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()
