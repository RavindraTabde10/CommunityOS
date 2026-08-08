"""
Event Service
Business logic for event management
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List
from app.models.event import Event, EventType
from app.schemas.event import EventCreate, EventUpdate


def get_upcoming_events(db: Session, limit: int = 5) -> List[Event]:
    """
    Get upcoming active events sorted by start date
    
    Args:
        db: Database session
        limit: Maximum number of events to return
    
    Returns:
        List of upcoming events
    """
    now = datetime.now()
    return db.query(Event).filter(
        and_(
            Event.is_active == True,
            Event.start_datetime >= now
        )
    ).order_by(Event.start_datetime.asc()).limit(limit).all()


def get_all_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[EventType] = None,
    is_active: Optional[bool] = None,
    include_past: bool = True
) -> tuple[List[Event], int]:
    """
    Get all events with optional filters
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        event_type: Filter by event type
        is_active: Filter by active status
        include_past: Include past events
    
    Returns:
        Tuple of (events list, total count)
    """
    query = db.query(Event)
    
    # Apply filters
    filters = []
    if event_type:
        filters.append(Event.event_type == event_type)
    if is_active is not None:
        filters.append(Event.is_active == is_active)
    if not include_past:
        filters.append(Event.start_datetime >= datetime.now())
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    events = query.order_by(Event.start_datetime.desc()).offset(skip).limit(limit).all()
    
    return events, total


def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
    """
    Get event by ID
    
    Args:
        db: Database session
        event_id: Event ID
    
    Returns:
        Event or None if not found
    """
    return db.query(Event).filter(Event.id == event_id).first()


def create_event(db: Session, event_data: EventCreate, user_id: int) -> Event:
    """
    Create a new event
    
    Args:
        db: Database session
        event_data: Event creation data
        user_id: ID of the admin creating the event
    
    Returns:
        Created event
    """
    event = Event(
        **event_data.model_dump(),
        created_by=user_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(db: Session, event_id: int, event_data: EventUpdate) -> Optional[Event]:
    """
    Update an existing event
    
    Args:
        db: Database session
        event_id: Event ID
        event_data: Event update data
    
    Returns:
        Updated event or None if not found
    """
    event = get_event_by_id(db, event_id)
    if not event:
        return None
    
    # Update only provided fields
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event_id: int) -> bool:
    """
    Delete an event (soft delete by setting is_active=False)
    
    Args:
        db: Database session
        event_id: Event ID
    
    Returns:
        True if deleted, False if not found
    """
    event = get_event_by_id(db, event_id)
    if not event:
        return False
    
    event.is_active = False
    db.commit()
    return True


def hard_delete_event(db: Session, event_id: int) -> bool:
    """
    Permanently delete an event from database
    
    Args:
        db: Database session
        event_id: Event ID
    
    Returns:
        True if deleted, False if not found
    """
    event = get_event_by_id(db, event_id)
    if not event:
        return False
    
    db.delete(event)
    db.commit()
    return True
