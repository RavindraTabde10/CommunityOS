"""
Committee Member Model
Manages committee member profiles and roles
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class CommitteeRole(str, enum.Enum):
    """Committee member roles"""
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    MEMBER = "member"


class CommitteeMember(Base):
    """Committee member model"""
    __tablename__ = "committee_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(CommitteeRole), nullable=False)
    position_name = Column(String(100))  # Custom position title
    responsibilities = Column(String(500))  # Brief description
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    term_start_date = Column(DateTime, nullable=True)
    term_end_date = Column(DateTime, nullable=True)
    display_order = Column(Integer, default=0)  # For ordering on dashboard
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="committee_membership")
