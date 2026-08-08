"""
Committee Member Endpoints
API routes for committee member management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.committee_member import (
    CommitteeMemberCreate,
    CommitteeMemberUpdate,
    CommitteeMemberResponse
)
from app.services import committee_service

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/", response_model=CommitteeMemberResponse, status_code=status.HTTP_201_CREATED)
def create_committee_member(
    data: CommitteeMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new committee member (Admin only)"""
    member = committee_service.create_committee_member(db, data)
    return {
        "id": member.id,
        "role": member.role,
        "position_name": member.position_name,
        "responsibilities": member.responsibilities,
        "contact_email": member.contact_email,
        "contact_phone": member.contact_phone,
        "display_order": member.display_order,
        "user_id": member.user_id,
        "user_name": member.user.name if member.user else None,
        "user_email": member.user.email if member.user else None,
        "is_active": member.is_active,
        "term_start_date": member.term_start_date,
        "term_end_date": member.term_end_date,
        "created_at": member.created_at
    }


@router.get("/active", response_model=List[dict])
def get_active_committee_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active committee members (Public - all authenticated users)"""
    return committee_service.get_active_committee_members(db)


@router.get("/", response_model=List[CommitteeMemberResponse])
def get_all_committee_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all committee members including inactive (Admin only)"""
    members = committee_service.get_all_committee_members(db)
    result = []
    for member in members:
        result.append({
            "id": member.id,
            "role": member.role,
            "position_name": member.position_name,
            "responsibilities": member.responsibilities,
            "contact_email": member.contact_email,
            "contact_phone": member.contact_phone,
            "display_order": member.display_order,
            "user_id": member.user_id,
            "user_name": member.user.name if member.user else None,
            "user_email": member.user.email if member.user else None,
            "user_unit": member.user.unit_number if member.user else None,
            "is_active": member.is_active,
            "term_start_date": member.term_start_date,
            "term_end_date": member.term_end_date,
            "created_at": member.created_at
        })
    return result


@router.get("/{member_id}", response_model=CommitteeMemberResponse)
def get_committee_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get committee member by ID"""
    member = committee_service.get_committee_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Committee member not found"
        )
    return {
        "id": member.id,
        "role": member.role,
        "position_name": member.position_name,
        "responsibilities": member.responsibilities,
        "contact_email": member.contact_email,
        "contact_phone": member.contact_phone,
        "display_order": member.display_order,
        "user_id": member.user_id,
        "user_name": member.user.name,
        "user_email": member.user.email,
        "is_active": member.is_active,
        "term_start_date": member.term_start_date,
        "term_end_date": member.term_end_date,
        "created_at": member.created_at
    }


@router.put("/{member_id}", response_model=CommitteeMemberResponse)
def update_committee_member(
    member_id: int,
    data: CommitteeMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update committee member (Admin only)"""
    member = committee_service.update_committee_member(db, member_id, data)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Committee member not found"
        )
    return {
        "id": member.id,
        "role": member.role,
        "position_name": member.position_name,
        "responsibilities": member.responsibilities,
        "contact_email": member.contact_email,
        "contact_phone": member.contact_phone,
        "display_order": member.display_order,
        "user_id": member.user_id,
        "user_name": member.user.name if member.user else None,
        "user_email": member.user.email if member.user else None,
        "is_active": member.is_active,
        "term_start_date": member.term_start_date,
        "term_end_date": member.term_end_date,
        "created_at": member.created_at
    }


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_committee_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete committee member (Admin only)"""
    success = committee_service.delete_committee_member(db, member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Committee member not found"
        )
