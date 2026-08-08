"""
Visitor Log API Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.visitor import VisitorLog
from app.schemas.visitor import VisitorLogCreate, VisitorLogResponse, VisitorStatusUpdate, VisitorStatus, VisitorLogUpdate
from app.services.visitor_service import VisitorService
from fastapi import HTTPException

router = APIRouter()


def require_security_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.SECURITY, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security or Admin access required")
    return current_user


def require_security_only(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.SECURITY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only security personnel can log visitor entries")
    return current_user


@router.get("/resident-by-unit/{unit_number}")
async def get_resident_by_unit(
    unit_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_security_or_admin),
):
    """Return the active occupant (tenant preferred over owner) for a unit"""
    # Prefer the tenant if the unit is rented
    resident = (
        db.query(User)
        .filter(User.unit_number == unit_number, User.role == UserRole.RESIDENT, User.is_active == True)
        .order_by(
            # tenant residency_type sorts first (NULL last)
            (User.residency_type == 'tenant').desc()
        )
        .first()
    )
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active resident found for this unit")
    return {
        "name": resident.name,
        "phone": resident.phone,
        "unit_number": resident.unit_number,
        "residency_type": resident.residency_type,
    }


@router.post("/", response_model=VisitorLogResponse, status_code=status.HTTP_201_CREATED)
async def log_visitor(
    data: VisitorLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_security_or_admin),
):
    """Log a new visitor entry (Security/Admin only)"""
    return VisitorService.log_visitor(db=db, data=data, logged_by=current_user.id)


@router.get("/", response_model=List[VisitorLogResponse])
async def get_all_visitors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_security_or_admin),
):
    """Get all visitor logs (Security/Admin only)"""
    return VisitorService.get_all_visitors(db=db, skip=skip, limit=limit)


@router.get("/my-visitors", response_model=List[VisitorLogResponse])
async def get_my_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all visitors logged for the current resident's unit"""
    return VisitorService.get_visitors_for_resident(db=db, user_id=current_user.id)


@router.get("/my-visitors/pending", response_model=List[VisitorLogResponse])
async def get_pending_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pending visitor approval requests for the current resident"""
    return VisitorService.get_pending_for_resident(db=db, user_id=current_user.id)


@router.get("/{visitor_id}", response_model=VisitorLogResponse)
async def get_visitor(
    visitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific visitor log"""
    return VisitorService.get_visitor(db=db, visitor_id=visitor_id)


@router.patch("/{visitor_id}", response_model=VisitorLogResponse)
async def edit_visitor(
    visitor_id: str,
    data: VisitorLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_security_or_admin),
):
    """Edit a pending visitor entry (Security/Admin only)"""
    return VisitorService.edit_visitor(db=db, visitor_id=visitor_id, data=data, current_user=current_user)


@router.patch("/{visitor_id}/status", response_model=VisitorLogResponse)
async def update_visitor_status(
    visitor_id: str,
    update: VisitorStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve, deny, or check out a visitor"""
    return VisitorService.update_status(
        db=db,
        visitor_id=visitor_id,
        new_status=update.status,
        current_user=current_user,
    )
