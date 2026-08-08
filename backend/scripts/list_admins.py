"""List all admin users in the database"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.user import User, UserRole

def list_admins():
    db = SessionLocal()
    try:
        # Get all admin users
        admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
        
        print("\n" + "="*60)
        print("ADMIN USERS IN DATABASE")
        print("="*60)
        
        if not admins:
            print("No admin users found!")
        else:
            for admin in admins:
                print(f"\nEmail: {admin.email}")
                print(f"Full Name: {admin.full_name}")
                print(f"Unit Number: {admin.unit_number}")
                print(f"Is Approved: {admin.is_approved}")
                print(f"Is Active: {admin.is_active}")
                print("-" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    list_admins()
