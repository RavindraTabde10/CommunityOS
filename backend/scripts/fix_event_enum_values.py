"""
Fix Event Enum Values
Updates existing lowercase event_type values to uppercase to match the schema
"""
import sys
from pathlib import Path
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

db_path = Path(__file__).parent.parent / "society_app.db"

print("=" * 70)
print("FIXING EVENT ENUM VALUES")
print("=" * 70)
print()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if events table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    if not cursor.fetchone():
        print("❌ Events table does not exist!")
        conn.close()
        sys.exit(1)
    
    # Get all events with their current event_type
    cursor.execute("SELECT id, title, event_type FROM events")
    events = cursor.fetchall()
    
    print(f"Found {len(events)} events in database")
    print()
    
    if len(events) == 0:
        print("✅ No events to update")
        conn.close()
        sys.exit(0)
    
    # Mapping from lowercase to uppercase
    type_mapping = {
        'meeting': 'MEETING',
        'festival': 'FESTIVAL',
        'maintenance': 'MAINTENANCE',
        'social': 'SOCIAL',
        'sports': 'SPORTS',
        'other': 'OTHER'
    }
    
    updated_count = 0
    for event_id, title, event_type in events:
        if event_type in type_mapping:
            new_type = type_mapping[event_type]
            print(f"Updating event {event_id} ({title}): {event_type} → {new_type}")
            cursor.execute("UPDATE events SET event_type = ? WHERE id = ?", (new_type, event_id))
            updated_count += 1
        else:
            print(f"Event {event_id} ({title}): {event_type} - already uppercase or unknown")
    
    # Commit the changes
    conn.commit()
    
    print()
    print(f"✅ Updated {updated_count} events")
    print()
    
    # Verify the updates
    cursor.execute("SELECT DISTINCT event_type FROM events")
    types = cursor.fetchall()
    print("Current event types in database:")
    for (event_type,) in types:
        print(f"  - {event_type}")
    
    conn.close()
    
    print()
    print("=" * 70)
    print("FIX COMPLETE")
    print("=" * 70)
    print()
    print("⚠️  Please restart the backend server for changes to take effect:")
    print("   1. Press Ctrl+C in the uvicorn terminal")
    print("   2. Run: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
