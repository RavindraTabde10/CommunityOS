"""
Poll Schemas
Pydantic models for poll creation, listing, and voting.
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class PollBase(BaseModel):
    """Shared fields for poll creation/response."""
    question: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    options: list[str] = Field(..., min_length=2, max_length=10)
    is_active: bool = True
    active_till: Optional[datetime] = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        cleaned = [option.strip() for option in value if option and option.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 non-empty options are required")

        if len({option.lower() for option in cleaned}) != len(cleaned):
            raise ValueError("Options must be unique")

        return cleaned


class PollCreate(PollBase):
    """Schema for creating polls."""
    pass


class PollUpdate(BaseModel):
    """Schema for updating an existing poll (all fields optional)."""
    question: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    options: Optional[list[str]] = Field(None, min_length=2, max_length=10)
    is_active: Optional[bool] = None
    active_till: Optional[datetime] = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        cleaned = [o.strip() for o in value if o and o.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 non-empty options are required")
        if len({o.lower() for o in cleaned}) != len(cleaned):
            raise ValueError("Options must be unique")
        return cleaned


class PollVoteCreate(BaseModel):
    """Schema for casting/updating a user's vote."""
    option_index: int = Field(..., ge=0)


class PollVoteResponse(BaseModel):
    """Vote row in poll response."""
    user_id: str
    option_index: int
    voted_at: datetime

    @field_validator("user_id", mode="before")
    @classmethod
    def coerce_user_id(cls, value: Any) -> str:
        return str(value)

    class Config:
        from_attributes = True


class PollResponse(PollBase):
    """Poll response with vote analytics."""
    id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    votes: list[PollVoteResponse] = []
    option_vote_counts: list[int] = []
    total_votes: int = 0

    @field_validator("created_by", mode="before")
    @classmethod
    def coerce_created_by(cls, value: Any) -> str:
        return str(value)

    class Config:
        from_attributes = True


class PollListResponse(BaseModel):
    """Paginated poll list."""
    polls: list[PollResponse]
    total: int
