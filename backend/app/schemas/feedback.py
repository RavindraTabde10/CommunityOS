"""
Feedback Schemas
Pydantic models for feedback creation, update, and response.
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class UserSummary(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    category: str = "general"
    description: str = Field(..., min_length=10, description="Minimum 10 characters")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {"process", "facility", "communication", "safety", "general"}
        if v not in valid:
            raise ValueError(f"category must be one of {valid}")
        return v


class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    admin_response: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {"pending", "acknowledged", "in_review", "implemented", "rejected"}
        if v not in valid:
            raise ValueError(f"status must be one of {valid}")
        return v


class FeedbackUserEdit(BaseModel):
    """Submitter-initiated edit — only content fields, not status."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=10)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {"process", "facility", "communication", "safety", "general"}
        if v not in valid:
            raise ValueError(f"category must be one of {valid}")
        return v


class FeedbackResponse(BaseModel):
    id: str
    title: str
    category: Any
    description: str
    status: Any
    admin_response: Optional[str] = None
    submitted_by: str
    submitter: Optional[UserSummary] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("category", "status", mode="before")
    @classmethod
    def coerce_enum(cls, v: Any) -> str:
        return v.value if hasattr(v, "value") else str(v)

    class Config:
        from_attributes = True
