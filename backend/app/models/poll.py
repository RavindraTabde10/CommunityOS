"""
Poll Models
Represents community polls and per-user votes.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Poll(Base):
    """Poll model for community voting questions."""
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    options = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    active_till = Column(DateTime, nullable=True)

    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    votes = relationship("PollVote", back_populates="poll", cascade="all, delete-orphan")


class PollVote(Base):
    """Stores one active vote per user per poll."""
    __tablename__ = "poll_votes"
    __table_args__ = (
        UniqueConstraint("poll_id", "user_id", name="uq_poll_vote_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    option_index = Column(Integer, nullable=False)
    voted_at = Column(DateTime, server_default=func.now(), nullable=False)

    poll = relationship("Poll", back_populates="votes")
