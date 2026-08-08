"""
Organization Database Model
SQLAlchemy ORM model for organizations (tenants) table
"""

from sqlalchemy import Column, String, Integer, Date, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class OrganizationType(str, enum.Enum):
    """Organization type enumeration"""
    APARTMENT_COMPLEX = "apartment_complex"
    HOUSING_SOCIETY = "housing_society"
    GATED_COMMUNITY = "gated_community"
    VILLA_COMMUNITY = "villa_community"


class OrganizationStatus(str, enum.Enum):
    """Organization status enumeration"""
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """Organization (tenant) model"""
    __tablename__ = "organizations"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Information
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contact Information
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(String)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    pincode = Column(String(10))
    
    # Organization Details
    organization_type = Column(Enum(OrganizationType), default=OrganizationType.APARTMENT_COMPLEX)
    total_units = Column(Integer)
    total_towers = Column(Integer)
    possession_date = Column(Date)
    formation_date = Column(Date)
    
    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color code
    
    # Status
    status = Column(Enum(OrganizationStatus), default=OrganizationStatus.TRIAL, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.BASIC, index=True)
    subscription_start_date = Column(Date)
    subscription_end_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime)  # Soft delete support
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    settings = relationship("OrganizationSetting", back_populates="organization", cascade="all, delete-orphan")
    usage_metrics = relationship("UsageMetric", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
