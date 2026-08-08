"""
Feedback Model
Stores resident feedback and process improvement suggestions.
"""
import enum
import uuid

from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class FeedbackCategory(str, enum.Enum):
    PROCESS = "process"
    FACILITY = "facility"
    COMMUNICATION = "communication"
    SAFETY = "safety"
    GENERAL = "general"


class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    IN_REVIEW = "in_review"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    category = Column(SAEnum(FeedbackCategory), nullable=False, default=FeedbackCategory.GENERAL)
    description = Column(Text, nullable=False)
    status = Column(SAEnum(FeedbackStatus), nullable=False, default=FeedbackStatus.PENDING, index=True)
    admin_response = Column(Text, nullable=True)

    submitted_by = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    responded_by = Column(String, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    submitter = relationship("User", foreign_keys=[submitted_by])
    responder = relationship("User", foreign_keys=[responded_by])
