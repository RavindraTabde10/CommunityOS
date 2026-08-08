"""
Event Model
Represents community events like meetings, festivals, maintenance schedules, etc.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class EventType(str, enum.Enum):
    """Types of events that can be scheduled"""
    MEETING = "MEETING"
    FESTIVAL = "FESTIVAL"
    MAINTENANCE = "MAINTENANCE"
    SOCIAL = "SOCIAL"
    SPORTS = "SPORTS"
    OTHER = "OTHER"


class Event(Base):
    """Event model for community events"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    venue = Column(String(200), nullable=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Audit fields
    created_by = Column(String, nullable=False)  # Admin user ID (UUID string)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', type='{self.event_type}', start='{self.start_datetime}')>"
