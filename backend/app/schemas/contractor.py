"""
Contractor Pydantic Schemas
Request/Response models for contractor endpoints
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Contractor Profile Schemas
# ============================================================================

class ContractorProfileBase(BaseModel):
    """Base contractor profile schema"""
    company_name: Optional[str] = Field(None, max_length=200)
    gst_number: Optional[str] = Field(None, max_length=50)
    license_number: Optional[str] = Field(None, max_length=100)
    specializations: List[str] = Field(..., min_length=1, description="List of specializations")
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)


class ContractorProfileCreate(ContractorProfileBase):
    """Contractor profile creation schema"""
    pass


class ContractorProfileUpdate(BaseModel):
    """Contractor profile update schema"""
    company_name: Optional[str] = Field(None, max_length=200)
    gst_number: Optional[str] = Field(None, max_length=50)
    license_number: Optional[str] = Field(None, max_length=100)
    specializations: Optional[List[str]] = Field(None, min_length=1)
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    is_available: Optional[bool] = None
    availability_status: Optional[str] = Field(None, description="available, busy, on_leave, inactive")


class UserBasicInfo(BaseModel):
    """Basic user information for contractor response"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True


class ContractorProfileResponse(BaseModel):
    """Contractor profile response schema"""
    id: str
    user_id: str
    user: Optional[UserBasicInfo] = None
    company_name: Optional[str] = None
    gst_number: Optional[str] = None
    license_number: Optional[str] = None
    specializations: List[str]
    years_of_experience: Optional[int] = None
    is_available: bool
    availability_status: str
    total_jobs_completed: int
    average_rating: float
    total_ratings: int
    response_time_avg: Optional[int] = None
    completion_rate: float
    is_verified: bool
    verified_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContractorListItem(BaseModel):
    """Contractor list item schema (simplified)"""
    id: str
    user_id: str
    user: Optional[UserBasicInfo] = None
    company_name: Optional[str] = None
    specializations: List[str]
    average_rating: float
    total_ratings: int
    total_jobs_completed: int
    is_available: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


class ContractorListResponse(BaseModel):
    """Paginated contractor list response"""
    total: int
    items: List[ContractorListItem]


# ============================================================================
# Contractor Rating Schemas
# ============================================================================

class ContractorRatingCreate(BaseModel):
    """Contractor rating creation schema"""
    issue_id: str
    rating: int = Field(..., ge=1, le=5, description="Overall rating (1-5)")
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    punctuality_rating: Optional[int] = Field(None, ge=1, le=5)
    professionalism_rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)
    work_photos: Optional[List[str]] = Field(None, description="List of photo URLs")
    
    @field_validator('quality_rating', 'punctuality_rating', 'professionalism_rating', mode='before')
    @classmethod
    def convert_zero_to_none(cls, v):
        """Convert 0 to None for optional ratings (0 means not rated)"""
        if v == 0:
            return None
        return v


class ContractorRatingResponse(BaseModel):
    """Contractor rating response schema"""
    id: str
    contractor_id: str
    issue_id: Optional[str] = None
    rated_by: str
    reviewer: Optional[UserBasicInfo] = None
    rating: int
    quality_rating: Optional[int] = None
    punctuality_rating: Optional[int] = None
    professionalism_rating: Optional[int] = None
    review_text: Optional[str] = None
    work_photos: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContractorRatingsListResponse(BaseModel):
    """List of contractor ratings"""
    total: int
    items: List[ContractorRatingResponse]


# ============================================================================
# Work Completion Schemas
# ============================================================================

class MaterialUsed(BaseModel):
    """Material used in work completion"""
    name: str
    quantity: float
    unit: str = "unit"
    cost: float = Field(..., ge=0)


class WorkCompletionCreate(BaseModel):
    """Work completion creation schema"""
    work_description: str = Field(..., min_length=10, max_length=2000)
    materials_used: Optional[List[Dict[str, Any]]] = None
    labor_cost: Optional[float] = Field(None, ge=0)
    total_cost: Optional[float] = Field(None, ge=0)
    after_photos: Optional[List[str]] = Field(None, description="List of after-work photo URLs")


class WorkCompletionVerify(BaseModel):
    """Work completion verification schema"""
    is_approved: bool
    verification_notes: Optional[str] = Field(None, max_length=1000)


class WorkCompletionResponse(BaseModel):
    """Work completion response schema"""
    id: str
    issue_id: str
    contractor_id: str
    completed_at: datetime
    work_description: Optional[str] = None
    materials_used: Optional[List[Dict[str, Any]]] = None
    labor_cost: Optional[float] = None
    total_cost: Optional[float] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    before_photos: Optional[List[str]] = None
    after_photos: Optional[List[str]] = None
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Issue Assignment Schemas
# ============================================================================

class IssueAssignment(BaseModel):
    """Issue assignment to contractor schema"""
    contractor_id: str = Field(..., description="User ID of the contractor (must have contractor role)")
    notes: Optional[str] = Field(None, max_length=500, description="Assignment notes")


class IssueAssignmentResponse(BaseModel):
    """Issue assignment response schema"""
    issue_id: str
    assigned_to: str
    assigned_at: datetime
    status: str


# ============================================================================
# Contractor Stats Schemas
# ============================================================================

class RatingBreakdown(BaseModel):
    """Rating breakdown by star count"""
    five_star: int = 0
    four_star: int = 0
    three_star: int = 0
    two_star: int = 0
    one_star: int = 0


class ContractorStatsResponse(BaseModel):
    """Contractor performance statistics"""
    contractor_id: str
    total_jobs: int
    completed_jobs: int
    cancelled_jobs: int = 0
    completion_rate: float
    average_rating: float
    total_ratings: int
    rating_breakdown: RatingBreakdown
    average_response_time_hours: Optional[int] = None
    jobs_by_category: Dict[str, int]
    recent_ratings: List[ContractorRatingResponse] = []
