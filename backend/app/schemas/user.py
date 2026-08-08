"""
User Pydantic Schemas
Request/Response models for user endpoints
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re
# from app.models.user import UserRole

UNIT_NUMBER_RE = re.compile(r'^[A-Za-z]\d-\d{4}$')


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    role: str  # TODO: Use UserRole enum
    unit_number: Optional[str] = None
    residency_type: Optional[str] = None  # "owner" or "tenant"


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('unit_number')
    @classmethod
    def validate_unit_number(cls, v):
        if v and not UNIT_NUMBER_RE.match(v):
            raise ValueError('Enter a valid unit number (e.g. B6-1001 or B7-0101)')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    unit_number: Optional[str] = Field(None, max_length=20)
    residency_type: Optional[str] = Field(None, description="owner or tenant")

    @field_validator('unit_number')
    @classmethod
    def validate_unit_number(cls, v):
        if v and not UNIT_NUMBER_RE.match(v):
            raise ValueError('Enter a valid unit number (e.g. B6-1001 or B7-0101)')
        return v


class UserResponse(UserBase):
    """User response schema"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list response"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserRoleUpdate(BaseModel):
    """User role update schema"""
    role: str = Field(..., description="New role for the user")


class UserStatusUpdate(BaseModel):
    """User status update schema"""
    is_active: bool = Field(..., description="Whether user account is active")


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
