"""
Check if a user exists in the database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.config import Settings

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def check_user(email: str):
    """Check if user exists"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"✓ User found!")
            print(f"  ID: {user.id}")
            print(f"  Name: {user.name}")
            print(f"  Email: {user.email}")
            print(f"  Phone: {user.phone}")
            print(f"  Role: {user.role}")
            print(f"  Unit: {user.unit_number}")
            print(f"  Active: {user.is_active}")
            print(f"  Created: {user.created_at}")
        else:
            print(f"✗ User not found with email: {email}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "ravindra.tabde10@gmail.com"
    check_user(email)
