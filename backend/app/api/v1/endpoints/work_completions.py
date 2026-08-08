"""
Work Completion Endpoints
Handles work completion verification and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.contractor import WorkCompletionVerify, WorkCompletionResponse
from app.api.v1.endpoints.auth import get_current_user
from app.services.contractor_service import WorkCompletionService


router = APIRouter()


def require_admin_or_facility(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is admin or facility manager"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or facility manager privileges required"
        )
    return current_user


@router.post("/{completion_id}/verify", response_model=WorkCompletionResponse)
async def verify_work_completion(
    completion_id: str,
    verification_data: WorkCompletionVerify,
    current_user: User = Depends(require_admin_or_facility),
    db: Session = Depends(get_db)
):
    """
    Verify work completion (Admin/Facility only)
    
    Requirements:
    - User must be admin or facility manager
    - Work must be marked as complete
    - Can only be verified once
    
    If approved:
    - Issue status changes to CLOSED
    - Contractor metrics updated
    
    If not approved:
    - Work remains unverified
    - Additional notes can be provided
    """
    work_completion = WorkCompletionService.verify_work_completion(
        completion_id=completion_id,
        is_approved=verification_data.is_approved,
        verification_notes=verification_data.verification_notes,
        verified_by_user_id=current_user.id,
        db=db
    )
    
    return work_completion
