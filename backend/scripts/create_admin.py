"""
Create Initial Admin User
Run this script to create the first admin user who can approve other registrations.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


def create_admin():
    """Create initial admin user with active status"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).first()
        
        if existing_admin:
            print(f"✅ Active admin already exists: {existing_admin.email}")
            return
        
        # Admin details
        email = input("Enter admin email (default: admin@riverdale.com): ").strip() or "admin@riverdale.com"
        name = input("Enter admin name (default: System Admin): ").strip() or "System Admin"
        password = input("Enter admin password (min 8 characters): ").strip()
        
        # Validate password
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long")
            return
        
        # Create admin user
        admin = User(
            email=email,
            password_hash=AuthService.get_password_hash(password),
            name=name,
            role=UserRole.ADMIN,
            is_active=True,  # Admin is immediately active
            phone=None,
            unit_number=None
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n✅ Admin user created successfully!")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.name}")
        print(f"   Role: {admin.role.value}")
        print(f"   Status: Active")
        print(f"\nYou can now login and approve pending user registrations.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Create Initial Admin User")
    print("=" * 60)
    print()
    create_admin()
