from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.guideline import GuidelineResponse, BulkGuidelineUpdate
from app.services.guideline_service import GuidelineService

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.get("/", response_model=List[GuidelineResponse])
def get_guidelines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return active guidelines (all authenticated users)"""
    return GuidelineService.get_active(db)


@router.get("/all", response_model=List[GuidelineResponse])
def get_all_guidelines(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return all guidelines including inactive (admin only)"""
    return GuidelineService.get_all(db)


@router.put("/bulk", response_model=List[GuidelineResponse])
def bulk_update_guidelines(
    payload: BulkGuidelineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Replace all guidelines with the provided list (admin only)"""
    return GuidelineService.bulk_replace(db, payload.guidelines)
