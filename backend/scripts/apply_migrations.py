"""
Apply database migrations
"""
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command

def run_migrations():
    """Run alembic migrations"""
    print("=" * 70)
    print("APPLYING DATABASE MIGRATIONS")
    print("=" * 70)
    print()
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Run upgrade
    print("📝 Running migrations...")
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations applied successfully!")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        return False
    
    print()
    print("✅ Database is up to date!")
    return True

if __name__ == "__main__":
    run_migrations()
