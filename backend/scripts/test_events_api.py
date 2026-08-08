"""
Test Events API Endpoint
Tests the /api/v1/events/upcoming endpoint with authentication
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("=" * 70)
print("TESTING EVENTS API ENDPOINT")
print("=" * 70)
print()

# First, login to get a token
print("1. Logging in as admin...")
try:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "admin",
            "password": "admin123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print(f"   ✅ Login successful! Token: {token[:20]}...")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"      {login_response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print()

# Now test the events endpoint
print("2. Fetching upcoming events...")
try:
    events_response = requests.get(
        f"{BASE_URL}/events/upcoming?limit=3",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"   Status Code: {events_response.status_code}")
    
    if events_response.status_code == 200:
        events = events_response.json()
        print(f"   ✅ Success! Found {len(events)} events")
        print()
        print("Events:")
        print("-" * 70)
        for event in events:
            print(f"  • {event.get('title')} ({event.get('event_type')})")
            print(f"    Start: {event.get('start_datetime')}")
            print(f"    Venue: {event.get('venue')}")
            print()
    else:
        print(f"   ❌ Failed to fetch events")
        print(f"   Response: {events_response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
