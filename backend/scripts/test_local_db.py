"""
Test Local SQLite Database Connection
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database():
    print("=" * 70)
    print("LOCAL DATABASE CONNECTION TEST")
    print("=" * 70)
    print()
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        print()
        print("Please add to your .env file:")
        print("DATABASE_URL=sqlite:///./society_app.db")
        sys.exit(1)
    
    print(f"📋 Database URL: {database_url}")
    print()
    
    # Check if database file exists
    if database_url.startswith("sqlite:///"):
        db_file = database_url.replace("sqlite:///./", "")
        db_path = Path(__file__).parent / db_file
        
        if db_path.exists():
            print(f"✓ Database file exists: {db_path}")
            print(f"  Size: {db_path.stat().st_size} bytes")
        else:
            print(f"ℹ️  Database file will be created at: {db_path}")
            print("   Run 'alembic upgrade head' to create tables")
    
    print()
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ DATABASE CONNECTION SUCCESSFUL!")
        print()
        
        # Check if tables exist
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]
        
        if tables:
            print("📊 Existing Tables:")
            for table in tables:
                print(f"  • {table}")
            print()
        else:
            print("ℹ️  No tables found yet.")
            print("   Run: alembic upgrade head")
            print()
        
        print("=" * 70)
        print("✅ READY TO USE!")
        print("=" * 70)
        print()
        print("Start your FastAPI app:")
        print("  uvicorn app.main:app --reload")
        
    except Exception as e:
        print("❌ CONNECTION FAILED!")
        print()
        print(f"Error: {type(e).__name__}")
        print(f"Details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_database()
