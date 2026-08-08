"""
Contractor Database Models
SQLAlchemy ORM models for contractor management
"""

from sqlalchemy import Column, String, Integer, Text, Enum, DateTime, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class AvailabilityStatus(str, enum.Enum):
    """Contractor availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    ON_LEAVE = "on_leave"
    INACTIVE = "inactive"


class ContractorProfile(Base):
    """Contractor-specific profile information"""
    __tablename__ = "contractor_profiles"
    
    id = Column(String, primary_key=True)  # Format: CONTCR-XXXXXX
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Business Information
    company_name = Column(String)
    gst_number = Column(String, unique=True)
    license_number = Column(String)
    
    # Skills & Specializations (JSON array)
    specializations = Column(JSON, nullable=False)  # ["electrical", "plumbing", etc.]
    years_of_experience = Column(Integer)
    
    # Availability
    is_available = Column(Boolean, default=True, nullable=False)
    availability_status = Column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE, nullable=False)
    
    # Performance Metrics
    total_jobs_completed = Column(Integer, default=0, nullable=False)
    average_rating = Column(Numeric(3, 2), default=0.0, nullable=False)  # 0.00 to 5.00
    total_ratings = Column(Integer, default=0, nullable=False)
    response_time_avg = Column(Integer)  # Average response time in hours
    completion_rate = Column(Numeric(5, 2), default=0.0, nullable=False)  # Percentage
    
    # Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime)
    verified_by = Column(String, ForeignKey("users.id"))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="contractor_profile")
    verifier = relationship("User", foreign_keys=[verified_by])
    ratings = relationship("ContractorRating", back_populates="contractor", cascade="all, delete-orphan")
    work_completions = relationship("WorkCompletion", back_populates="contractor", cascade="all, delete-orphan")


class ContractorRating(Base):
    """Ratings and reviews for contractors"""
    __tablename__ = "contractor_ratings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contractor_id = Column(String, ForeignKey("contractor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_id = Column(String, ForeignKey("issues.id", ondelete="SET NULL"))
    rated_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Rating Details
    rating = Column(Integer, nullable=False)  # 1 to 5
    quality_rating = Column(Integer)  # 1 to 5
    punctuality_rating = Column(Integer)  # 1 to 5
    professionalism_rating = Column(Integer)  # 1 to 5
    
    # Review
    review_text = Column(Text)
    
    # Photos (optional)
    work_photos = Column(JSON)  # Array of photo URLs
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    contractor = relationship("ContractorProfile", back_populates="ratings")
    issue = relationship("Issue")
    reviewer = relationship("User")


class WorkCompletion(Base):
    """Work completion records and verification"""
    __tablename__ = "work_completions"
    
    id = Column(String, primary_key=True)  # Format: WKCMP-XXXXXX
    issue_id = Column(String, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    contractor_id = Column(String, ForeignKey("contractor_profiles.id"), nullable=False, index=True)
    
    # Completion Details
    completed_at = Column(DateTime, nullable=False)
    work_description = Column(Text)
    materials_used = Column(JSON)  # Array of materials with costs
    labor_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    
    # Verification
    verified_by = Column(String, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Photos
    before_photos = Column(JSON)  # URLs from issue photos
    after_photos = Column(JSON)  # URLs uploaded on completion
    
    # Status
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    issue = relationship("Issue")
    contractor = relationship("ContractorProfile", back_populates="work_completions")
    verifier = relationship("User")
