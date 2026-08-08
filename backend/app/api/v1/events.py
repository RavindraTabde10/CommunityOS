"""
Events API Endpoints
Manages community events (meetings, festivals, maintenance, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.event import EventType
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.services import event_service


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

router = APIRouter()


@router.get("/upcoming", response_model=list[EventResponse])
def get_upcoming_events(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming active events
    
    **Accessible by:** All authenticated users
    """
    events = event_service.get_upcoming_events(db, limit=limit)
    return events


@router.get("", response_model=EventListResponse)
def get_all_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    event_type: Optional[EventType] = None,
    is_active: Optional[bool] = None,
    include_past: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all events with optional filters
    
    **Accessible by:** All authenticated users
    """
    events, total = event_service.get_all_events(
        db,
        skip=skip,
        limit=limit,
        event_type=event_type,
        is_active=is_active,
        include_past=include_past
    )
    return EventListResponse(events=events, total=total)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get event by ID
    
    **Accessible by:** All authenticated users
    """
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new event
    
    **Accessible by:** Admin only
    """
    # Validate end_datetime if provided
    if event_data.end_datetime and event_data.end_datetime < event_data.start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End datetime must be after start datetime"
        )
    
    event = event_service.create_event(db, event_data, current_user.id)
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing event
    
    **Accessible by:** Admin only
    """
    event = event_service.update_event(db, event_id, event_data)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the event"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete an event (soft delete by default, hard delete if specified)
    
    **Accessible by:** Admin only
    """
    if hard_delete:
        success = event_service.hard_delete_event(db, event_id)
    else:
        success = event_service.delete_event(db, event_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return None
