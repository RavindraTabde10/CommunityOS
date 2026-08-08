"""
Create Initial Database Migration
Generates migration files from SQLAlchemy models
"""
import subprocess
import sys

def create_migration():
    print("=" * 70)
    print("CREATING INITIAL DATABASE MIGRATION")
    print("=" * 70)
    print()
    
    print("📝 Generating migration from models...")
    
    try:
        result = subprocess.run(
            [
                sys.executable, 
                "-m", 
                "alembic", 
                "revision", 
                "--autogenerate", 
                "-m", 
                "Initial migration - users and issues tables"
            ],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print()
            print("✅ Migration created successfully!")
            print()
            print("📝 Next step: Apply the migration")
            print("   Run: alembic upgrade head")
        else:
            print()
            print("❌ Failed to create migration")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_migration()
