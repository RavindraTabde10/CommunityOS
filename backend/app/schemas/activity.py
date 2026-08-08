"""
Activity Log Schemas - Pydantic models for activity tracking
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActivityResponse(BaseModel):
    """Schema for activity log response"""
    id: int
    issue_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for paginated activity list response"""
    activities: list[ActivityResponse]
    total: int
    skip: int
    limit: int
