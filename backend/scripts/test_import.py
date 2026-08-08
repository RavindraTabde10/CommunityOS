"""
Quick test to verify imports work
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
print("Testing imports...")

try:
    from app.services import event_service
    print("✅ SUCCESS: event_service imported correctly")
    print(f"   Available functions: {dir(event_service)}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
