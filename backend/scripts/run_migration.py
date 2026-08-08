"""
Quick Migration Runner
Applies pending database migrations
"""
import os
import sys
from pathlib import Path

# Set up the path
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("APPLYING DATABASE MIGRATIONS")
print("=" * 70)
print()

try:
    # Import alembic after setting up the path
    from alembic.config import Config
    from alembic import command
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    print("📝 Running migrations...")
    command.upgrade(alembic_cfg, "head")
    print()
    print("✅ Migrations applied successfully!")
    print()
    print("🎉 Events table created! You can now:")
    print("  1. Refresh the dashboard - events widget should work")
    print("  2. Create test events via Swagger UI: http://127.0.0.1:8000/api/docs")
    print()
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print()
    print("Alembic is not installed. Please install it:")
    print("  pip install alembic")
    print()
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error applying migrations: {e}")
    print()
    print("Troubleshooting:")
    print("  - Make sure you're in the backend directory")
    print("  - Check that alembic.ini exists")
    print("  - Verify DATABASE_URL in .env file")
    print()
    sys.exit(1)
