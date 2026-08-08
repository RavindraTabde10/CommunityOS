"""
Feedback API Endpoints
Manages resident feedback and process improvement suggestions.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackUpdate, FeedbackUserEdit
from app.services import feedback_service

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit feedback or a suggestion (any authenticated user)."""
    return feedback_service.create_feedback(db, data, current_user.id)


@router.get("")
def list_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List feedback. Admins see all; others see only their own."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    user_id = None if user_role == "admin" else str(current_user.id)
    rows, total = feedback_service.get_all_feedback(db, skip=skip, limit=limit, user_id=user_id, status=status)
    return {"feedback": rows, "total": total}


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fb = feedback_service.get_feedback(db, feedback_id)
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if user_role != "admin" and fb.submitted_by != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return fb


@router.patch("/{feedback_id}", response_model=FeedbackResponse)
def edit_own_feedback(
    feedback_id: str,
    data: FeedbackUserEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submitter can edit title/category/description while status is still pending."""
    fb = feedback_service.get_feedback(db, feedback_id)
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    if fb.submitted_by != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    fb_status = fb.status.value if hasattr(fb.status, "value") else fb.status
    if fb_status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending feedback can be edited")
    return feedback_service.edit_feedback(db, feedback_id, data)


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: str,
    data: FeedbackUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update feedback status and/or add admin response (admin only)."""
    fb = feedback_service.update_feedback(db, feedback_id, data, current_user.id)
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return fb


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete feedback (admin only)."""
    if not feedback_service.delete_feedback(db, feedback_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
