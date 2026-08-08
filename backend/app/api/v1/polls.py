"""
Polls API Endpoints
Manages community polls and voting.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.poll import PollCreate, PollUpdate, PollListResponse, PollResponse, PollVoteCreate
from app.services import poll_service


router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for poll creation."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("", response_model=PollListResponse)
def get_all_polls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all polls with optional status filtering."""
    polls, total = poll_service.get_all_polls(
        db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )
    return PollListResponse(polls=[poll_service.serialize_poll(poll) for poll in polls], total=total)


@router.get("/{poll_id}", response_model=PollResponse)
def get_poll(
    poll_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a poll by ID."""
    poll = poll_service.get_poll_by_id(db, poll_id)
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )
    return poll_service.serialize_poll(poll)


@router.post("", response_model=PollResponse, status_code=status.HTTP_201_CREATED)
def create_poll(
    poll_data: PollCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new poll (admin only)."""
    poll = poll_service.create_poll(db, poll_data, current_user.id)
    return poll_service.serialize_poll(poll)


@router.delete("/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poll(
    poll_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a poll and all its votes (admin only)."""
    deleted = poll_service.delete_poll(db, poll_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )


@router.put("/{poll_id}", response_model=PollResponse)
def update_poll(
    poll_id: int,
    poll_data: PollUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a poll (admin only)."""
    poll = poll_service.update_poll(db, poll_id, poll_data)
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )
    return poll_service.serialize_poll(poll)


@router.post("/{poll_id}/vote", response_model=PollResponse)
def vote_on_poll(
    poll_id: int,
    vote_data: PollVoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cast/update the current user's vote for a poll."""
    poll = poll_service.get_poll_by_id(db, poll_id)
    if not poll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poll not found",
        )

    if not poll.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This poll is not active",
        )

    if poll.active_till and poll.active_till < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This poll has expired",
        )

    try:
        updated_poll = poll_service.vote_on_poll(
            db,
            poll_id=poll_id,
            user_id=current_user.id,
            option_index=vote_data.option_index,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return poll_service.serialize_poll(updated_poll)
