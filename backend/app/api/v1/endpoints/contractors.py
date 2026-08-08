"""
Contractor Management Endpoints
Handles contractor profiles, ratings, work completion, and performance statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.contractor import (
    ContractorProfileCreate,
    ContractorProfileUpdate,
    ContractorProfileResponse,
    ContractorListResponse,
    ContractorRatingCreate,
    ContractorRatingResponse,
    ContractorRatingsListResponse,
    ContractorStatsResponse,
    WorkCompletionVerify
)
from app.api.v1.endpoints.auth import get_current_user
from app.services.contractor_service import ContractorService, RatingService


router = APIRouter()


def require_admin_or_facility(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is admin or facility manager"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or facility manager privileges required"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# ==================== CONTRACTOR PROFILE MANAGEMENT ====================

@router.post("/", response_model=ContractorProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_contractor_profile(
    profile_data: ContractorProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a contractor profile for current user
    
    User must have contractor role to create a profile.
    Only one profile per user is allowed.
    """
    contractor_profile = ContractorService.create_contractor_profile(
        contractor_data=profile_data,
        user_id=current_user.id,
        db=db
    )
    
    return contractor_profile


@router.get("/", response_model=ContractorListResponse)
async def list_contractors(
    specialization: Optional[str] = Query(None, description="Filter by specialization (e.g., electrical, plumbing)"),
    is_available: Optional[bool] = Query(None, description="Filter by availability status"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum average rating (0.0 to 5.0)"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all contractors with optional filters
    
    Supports filtering by:
    - Specialization (exact match in specializations array)
    - Availability status
    - Minimum rating
    - Verification status
    """
    contractors, total = ContractorService.list_contractors(
        specialization=specialization,
        is_available=is_available,
        min_rating=min_rating,
        is_verified=is_verified,
        skip=skip,
        limit=limit,
        db=db
    )
    
    return {
        "total": total,
        "items": contractors
    }


@router.get("/{contractor_id}", response_model=ContractorProfileResponse)
async def get_contractor_details(
    contractor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed contractor profile by ID
    
    Returns full contractor information including user details,
    performance metrics, and verification status.
    """
    contractor = ContractorService.get_contractor_by_id(contractor_id, db)
    return contractor


@router.put("/{contractor_id}", response_model=ContractorProfileResponse)
async def update_contractor_profile(
    contractor_id: str,
    profile_data: ContractorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update contractor profile
    
    Contractors can update their own profile.
    Admins can update any contractor profile.
    """
    # Get contractor profile
    contractor = ContractorService.get_contractor_by_id(contractor_id, db)
    
    # Check permission - owner or admin
    if contractor.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own contractor profile"
        )
    
    # Update profile
    updated_contractor = ContractorService.update_contractor_profile(
        contractor_id=contractor_id,
        contractor_data=profile_data,
        db=db
    )
    
    return updated_contractor


@router.get("/{contractor_id}/stats", response_model=ContractorStatsResponse)
async def get_contractor_stats(
    contractor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive contractor performance statistics
    
    Returns:
    - Total/completed/cancelled jobs
    - Completion rate
    - Average rating and rating breakdown
    - Jobs by category
    - Recent ratings
    """
    stats = ContractorService.calculate_contractor_stats(contractor_id, db)
    return stats


@router.post("/{contractor_id}/verify", response_model=ContractorProfileResponse)
async def verify_contractor(
    contractor_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Verify a contractor (Admin only)
    
    Marks the contractor as verified and records the admin who verified them.
    Verified contractors may have higher visibility or priority in listings.
    """
    contractor = ContractorService.verify_contractor(
        contractor_id=contractor_id,
        verified_by_user_id=current_user.id,
        db=db
    )
    
    return contractor


# ==================== CONTRACTOR RATINGS ====================

@router.post("/{contractor_id}/rate", response_model=ContractorRatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_contractor(
    contractor_id: str,
    rating_data: ContractorRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rate a contractor after work completion
    
    Requirements:
    - User must be the issue reporter
    - Issue must be assigned to this contractor
    - Work must be marked as complete
    - Only one rating per issue
    
    Accepts overall rating (1-5) and optional category ratings for:
    - Quality
    - Punctuality
    - Professionalism
    """
    rating = RatingService.create_rating(
        contractor_id=contractor_id,
        rating_data=rating_data,
        rated_by_user_id=current_user.id,
        db=db
    )
    
    return rating


@router.get("/{contractor_id}/ratings", response_model=ContractorRatingsListResponse)
async def get_contractor_ratings(
    contractor_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=50, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all ratings for a contractor
    
    Returns ratings with reviewer information, ordered by most recent first.
    """
    ratings, total = RatingService.get_contractor_ratings(
        contractor_id=contractor_id,
        skip=skip,
        limit=limit,
        db=db
    )
    
    return {
        "total": total,
        "items": ratings
    }
