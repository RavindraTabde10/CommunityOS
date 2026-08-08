"""
Comment Schemas - Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    """Base schema for comment"""
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")


class CommentCreate(CommentBase):
    """Schema for creating a comment"""
    pass


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: str = Field(..., min_length=1, max_length=2000, description="Updated comment content")


class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: int
    issue_id: str
    user_id: str
    user_name: str
    user_email: str
    created_at: datetime
    updated_at: datetime
    is_own: bool = False  # Set dynamically based on current user

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Schema for paginated comment list response"""
    comments: list[CommentResponse]
    total: int
    skip: int
    limit: int
