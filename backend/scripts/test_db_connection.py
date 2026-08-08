"""
Database Connection Test Script
Run this to verify your database connection before running migrations
"""
import os
import sys
from urllib.parse import urlparse
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Get DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        print("\nPlease ensure your .env file exists and contains:")
        print("DATABASE_URL=postgresql://user:password@host:port/database")
        sys.exit(1)
    
    # Parse the URL
    try:
        parsed = urlparse(db_url)
        
        # Mask password for display
        password_masked = parsed.password[:4] + "*" * (len(parsed.password) - 4) if parsed.password else "None"
        
        print("\n📋 Connection Details:")
        print(f"  Scheme:   {parsed.scheme}")
        print(f"  Username: {parsed.username}")
        print(f"  Password: {password_masked}")
        print(f"  Host:     {parsed.hostname}")
        print(f"  Port:     {parsed.port}")
        print(f"  Database: {parsed.path.lstrip('/')}")
        print()
        
        # Check if it's the pooler
        if parsed.hostname and "pooler.supabase.com" in parsed.hostname:
            print("✓ Using Supabase Connection Pooler")
        elif parsed.hostname and "db." in parsed.hostname:
            print("⚠️  WARNING: Using direct connection (not pooler)")
            print("   Recommended: Use pooler URL instead")
        
        # Check port
        if parsed.port == 6543:
            print("✓ Using correct pooler port (6543)")
        elif parsed.port == 5432:
            print("⚠️  WARNING: Port 5432 detected")
            print("   For Supabase pooler, use port 6543")
        else:
            print(f"⚠️  Unusual port: {parsed.port}")
        
        print()
        print("-" * 60)
        print("🔌 Attempting connection...")
        print("-" * 60)
        
        # Attempt connection
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            connect_timeout=10
        )
        
        print("✅ CONNECTION SUCCESSFUL!")
        print()
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("📊 Database Info:")
        print(f"  Version: {version[:50]}...")
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"  Current Database: {db_name}")
        
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()[0]
        print(f"  Current User: {user}")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run: alembic upgrade head")
        
    except psycopg2.OperationalError as e:
        print("❌ CONNECTION FAILED!")
        print()
        print("Error Details:")
        print(f"  {str(e)}")
        print()
        print("🔧 Troubleshooting Steps:")
        print()
        print("1. Check your DATABASE_URL in .env file")
        print("   - Should be: postgresql://user:password@host:6543/database")
        print("   - Use port 6543 for Supabase pooler")
        print()
        print("2. Verify your password is correct")
        print("   - Go to Supabase Dashboard → Settings → Database")
        print("   - Reset password if needed")
        print()
        print("3. Check if your Supabase project is active")
        print("   - Go to your Supabase dashboard")
        print("   - Ensure project is not paused")
        print()
        print("4. Try the Session Pooler URL:")
        print("   - Dashboard → Settings → Database")
        print("   - Connection Pooling: Session")
        print("   - Copy the URI")
        print()
        print("5. Check your network/firewall")
        print("   - Some corporate networks block database connections")
        print("   - Try a different network if possible")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}")
        print(f"   {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
