"""
Issue Database Model
SQLAlchemy ORM model for issues table
"""

from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.base import Base


class IssueCategory(str, enum.Enum):
    """Issue category enumeration"""
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    PAINTING = "painting"
    CARPENTRY = "carpentry"
    FLOORING = "flooring"
    CIVIL = "civil"
    OTHER = "other"


class IssuePriority(str, enum.Enum):
    """Issue priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(str, enum.Enum):
    """Issue status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Issue(Base):
    """Issue model"""
    __tablename__ = "issues"
    
    id = Column(String, primary_key=True)  # Format: RGTS-XXXXXX
    
    issue_number = Column(String, unique=True, nullable=False)  # Sequential number
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(Enum(IssueCategory), nullable=False)
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN)
    location = Column(String)
    unit_number = Column(String)
    reported_by = Column(String, ForeignKey("users.id"))
    assigned_to = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    resolved_at = Column(DateTime)
    
    # Relationships
    photos = relationship("IssuePhoto", back_populates="issue", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    activities = relationship("IssueActivity", back_populates="issue", cascade="all, delete-orphan")
    reporter = relationship("User", foreign_keys=[reported_by], backref="reported_issues")
    assignee = relationship("User", foreign_keys=[assigned_to], backref="assigned_issues")


class IssuePhoto(Base):
    """Issue photo model"""
    __tablename__ = "issue_photos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("issues.id"))
    photo_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    issue = relationship("Issue", back_populates="photos")
