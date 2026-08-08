"""
Event Schemas
Pydantic models for event validation and serialization
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Any
from app.models.event import EventType


class EventBase(BaseModel):
    """Base event schema with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: EventType
    venue: Optional[str] = Field(None, max_length=200)
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    is_active: bool = True


class EventCreate(EventBase):
    """Schema for creating a new event"""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    venue: Optional[str] = Field(None, max_length=200)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    """Schema for event responses"""
    id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('created_by', mode='before')
    @classmethod
    def coerce_created_by(cls, v: Any) -> str:
        return str(v)

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Schema for list of events"""
    events: list[EventResponse]
    total: int
