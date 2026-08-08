"""
Check Events in Database
"""
import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path(__file__).parent / "society_app.db"

print("=" * 70)
print("CHECKING EVENTS IN DATABASE")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    if not cursor.fetchone():
        print("❌ Events table does not exist!")
        conn.close()
        exit(1)
    
    # Get all events
    cursor.execute("""
        SELECT id, title, event_type, start_datetime, end_datetime, is_active, created_by 
        FROM events 
        ORDER BY start_datetime
    """)
    events = cursor.fetchall()
    
    print(f"Found {len(events)} events in database:")
    print("-" * 70)
    
    now = datetime.now()
    print(f"Current time: {now}")
    print()
    
    for event in events:
        event_id, title, event_type, start_dt, end_dt, is_active, created_by = event
        start_datetime = datetime.fromisoformat(start_dt) if start_dt else None
        is_future = start_datetime > now if start_datetime else False
        status = "UPCOMING" if (is_active and is_future) else "PAST" if is_active else "INACTIVE"
        
        print(f"ID: {event_id}")
        print(f"  Title: {title}")
        print(f"  Type: {event_type}")
        print(f"  Start: {start_dt}")
        print(f"  Active: {is_active}")
        print(f"  Status: {status}")
        print()
    
    # Count upcoming events
    cursor.execute("""
        SELECT COUNT(*) FROM events 
        WHERE is_active = 1 AND start_datetime >= datetime('now')
    """)
    upcoming_count = cursor.fetchone()[0]
    
    print("-" * 70)
    print(f"✅ Total events: {len(events)}")
    print(f"✅ Upcoming events: {upcoming_count}")
    print()
    
    if upcoming_count == 0:
        print("⚠️  No upcoming events found!")
        print("   Events must have start_datetime in the future")
        print()
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
