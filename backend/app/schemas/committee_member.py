"""
Committee Member Schemas
Pydantic models for committee member data validation
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from app.models.committee_member import CommitteeRole


class CommitteeMemberBase(BaseModel):
    """Base committee member schema"""
    role: CommitteeRole
    position_name: Optional[str] = None
    responsibilities: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    display_order: int = 0


class CommitteeMemberCreate(CommitteeMemberBase):
    """Schema for creating a committee member"""
    user_id: str
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None


class CommitteeMemberUpdate(BaseModel):
    """Schema for updating a committee member"""
    role: Optional[CommitteeRole] = None
    position_name: Optional[str] = None
    responsibilities: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None
    display_order: Optional[int] = None


class CommitteeMemberResponse(CommitteeMemberBase):
    """Schema for committee member response"""
    id: int
    user_id: str
    user_name: Optional[str] = None  # From joined user
    user_email: Optional[str] = None  # From joined user
    user_unit: Optional[str] = None  # From joined user
    is_active: bool
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
