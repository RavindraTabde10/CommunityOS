"""
Test Events Endpoint
Quick diagnostic script to check if events API is working
"""
import sys
import requests
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("TESTING EVENTS ENDPOINT")
print("=" * 70)
print()

# Test 1: Check if backend is running
print("Test 1: Checking if backend is running...")
try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=2)
    print(f"✅ Backend is running: {response.json()}")
except requests.exceptions.ConnectionError:
    print("❌ Backend is NOT running!")
    print("   Please start the backend with: uvicorn app.main:app --reload")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error connecting to backend: {e}")
    sys.exit(1)

print()

# Test 2: Check if we can import the events module
print("Test 2: Checking if events module can be imported...")
try:
    from app.api.v1 import events
    print("✅ Events module imported successfully")
except Exception as e:
    print(f"❌ Error importing events module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Check if events table exists
print("Test 3: Checking if events table exists in database...")
try:
    from app.db.session import SessionLocal
    from app.models.event import Event
    
    db = SessionLocal()
    count = db.query(Event).count()
    print(f"✅ Events table exists with {count} records")
    db.close()
except Exception as e:
    print(f"❌ Error checking events table: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Try to call the events endpoint (needs auth token)
print("Test 4: Checking events API endpoint (without auth)...")
try:
    response = requests.get("http://127.0.0.1:8000/api/v1/events/upcoming", timeout=2)
    if response.status_code == 401:
        print("✅ Events endpoint is accessible (requires authentication)")
    elif response.status_code == 200:
        print(f"✅ Events endpoint working: {response.json()}")
    else:
        print(f"⚠️  Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Error calling events endpoint: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
