"""
Announcement Pydantic Schemas
Request/Response validation schemas for announcements
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AnnouncementPriority(str, Enum):
    """Announcement priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AnnouncementBase(BaseModel):
    """Base announcement schema with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Announcement title")
    content: str = Field(..., min_length=1, description="Announcement content/message")
    priority: AnnouncementPriority = Field(default=AnnouncementPriority.NORMAL, description="Priority level")
    is_active: bool = Field(default=True, description="Whether announcement is currently active")
    start_date: Optional[datetime] = Field(default=None, description="Optional start date")
    end_date: Optional[datetime] = Field(default=None, description="Optional end date")


class AnnouncementCreate(AnnouncementBase):
    """Schema for creating new announcement"""
    pass


class AnnouncementUpdate(BaseModel):
    """Schema for updating announcement (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    priority: Optional[AnnouncementPriority] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AnnouncementResponse(AnnouncementBase):
    """Schema for announcement response"""
    id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True
