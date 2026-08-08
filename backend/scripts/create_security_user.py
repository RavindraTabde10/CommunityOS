"""
Create Security User
Run this script to create a security guard account.
Usage: python create_security_user.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


def create_security_user():
    db = SessionLocal()
    try:
        email = input("Enter security user email: ").strip()
        if not email:
            print("❌ Email is required")
            return

        if db.query(User).filter(User.email == email).first():
            print(f"❌ User with email '{email}' already exists")
            return

        name = input("Enter name (default: Security Guard): ").strip() or "Security Guard"
        phone = input("Enter phone (optional): ").strip() or None
        password = input("Enter password (min 8 characters): ").strip()

        if len(password) < 8:
            print("❌ Password must be at least 8 characters long")
            return

        user = User(
            email=email,
            password_hash=AuthService.get_password_hash(password),
            name=name,
            phone=phone,
            role=UserRole.SECURITY,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print("\n✅ Security user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Name:  {user.name}")
        print(f"   Role:  {user.role.value}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_security_user()
