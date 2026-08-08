"""
Activity log model for tracking issue changes
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class IssueActivity(Base):
    """Activity log for tracking all issue changes"""
    __tablename__ = "issue_activities"

    id = Column(Integer, primary_key=True, index=True)
    
    issue_id = Column(String, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)  # created, updated, status_changed, assigned, commented, etc.
    field_name = Column(String(50), nullable=True)  # Which field changed
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    description = Column(Text, nullable=False)  # Human-readable description
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    issue = relationship("Issue", back_populates="activities")
    user = relationship("User")

    def __repr__(self):
        return f"<IssueActivity(id={self.id}, issue_id={self.issue_id}, action={self.action})>"
