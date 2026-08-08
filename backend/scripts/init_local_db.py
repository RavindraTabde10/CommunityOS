"""
Initialize Local SQLite Database
Creates a local database and generates configuration
"""
import secrets
import os
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def setup_local_database():
    print("=" * 70)
    print("LOCAL DATABASE SETUP")
    print("=" * 70)
    print()
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Database path
    db_path = Path(__file__).parent / "society_app.db"
    database_url = f"sqlite:///./{db_path.name}"
    
    print("✅ Configuration Generated!")
    print()
    print("📋 Add these to your .env file:")
    print("-" * 70)
    print(f"DATABASE_URL={database_url}")
    print(f"SECRET_KEY={secret_key}")
    print("-" * 70)
    print()
    
    print("ℹ️  Database Details:")
    print(f"  • Type: SQLite")
    print(f"  • Location: {db_path.absolute()}")
    print(f"  • File will be created when you run migrations")
    print()
    
    print("📝 Next Steps:")
    print("  1. Copy the configuration above to your .env file")
    print("  2. Run: alembic upgrade head")
    print("  3. Start your app: uvicorn app.main:app --reload")
    print()
    
    # Save to a config file for reference
    config_file = Path(__file__).parent / ".env.local.sample"
    with open(config_file, "w") as f:
        f.write(f"# Local SQLite Configuration\n")
        f.write(f"DATABASE_URL={database_url}\n")
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"\n# JWT Settings\n")
        f.write(f"ALGORITHM=HS256\n")
        f.write(f"ACCESS_TOKEN_EXPIRE_MINUTES=30\n")
    
    print(f"💾 Configuration saved to: {config_file.name}")
    print()
    print("=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    setup_local_database()
