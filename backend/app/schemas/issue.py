"""
Issue Pydantic Schemas
Request/Response models for issue endpoints
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Any
from datetime import datetime
from uuid import UUID


class UserSummary(BaseModel):
    """User summary for issue responses"""
    id: str
    name: str
    email: str
    role: Optional[str] = None
    
    class Config:
        from_attributes = True


class IssuePhotoResponse(BaseModel):
    """Issue photo response schema"""
    id: str
    photo_url: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Define valid enum values as Literal types for better API docs
IssueCategoryType = Literal["electrical", "plumbing", "painting", "carpentry", "flooring", "civil", "other"]
IssuePriorityType = Literal["low", "medium", "high", "critical"]
IssueStatusType = Literal["open", "in_progress", "resolved", "closed"]


class IssueBase(BaseModel):
    """Base issue schema"""
    title: str = Field(..., min_length=3, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, description="Detailed description of the issue")
    category: IssueCategoryType = Field(..., description="Issue category")
    priority: IssuePriorityType = Field(default="medium", description="Priority level")
    location: Optional[str] = Field(None, description="Physical location (e.g., Building, Floor)")
    unit_number: Optional[str] = Field(None, description="Unit/Flat number")


class IssueCreate(IssueBase):
    """Issue creation schema"""
    assigned_to: Optional[str] = Field(None, description="User ID to assign the issue to (admin/facility only)")


class IssueUpdate(BaseModel):
    """Issue update schema"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    category: Optional[IssueCategoryType] = None
    priority: Optional[IssuePriorityType] = None
    status: Optional[IssueStatusType] = None
    assigned_to: Optional[str] = None


class IssueResponse(IssueBase):
    """Issue response schema"""
    id: str
    issue_number: str
    status: IssueStatusType
    reporter: UserSummary
    assignee: Optional[UserSummary] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    photos: List[IssuePhotoResponse] = []
    
    @field_validator('category', 'priority', 'status', mode='before')
    @classmethod
    def convert_enum_to_str(cls, v: Any) -> str:
        """Convert enum values to strings"""
        if hasattr(v, 'value'):
            return v.value
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True
