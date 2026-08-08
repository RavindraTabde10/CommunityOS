"""
User Database Model
SQLAlchemy ORM model for users table
"""

from sqlalchemy import Column, String, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    RESIDENT = "resident"
    CONTRACTOR = "contractor"
    BUILDER = "builder"
    ADMIN = "admin"
    SECURITY = "security"
    FACILITY = "facility"


class ResidencyType(str, enum.Enum):
    """Residency type enumeration"""
    OWNER = "owner"
    TENANT = "tenant"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.RESIDENT)
    unit_number = Column(String)
    residency_type = Column(Enum(ResidencyType), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    comments = relationship("Comment", back_populates="user")
    contractor_profile = relationship(
        "ContractorProfile", 
        back_populates="user", 
        foreign_keys="ContractorProfile.user_id",
        uselist=False, 
        cascade="all, delete-orphan"
    )
