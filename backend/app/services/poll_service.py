"""
Poll Service
Business logic for polls and voting.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.poll import Poll, PollVote
from app.schemas.poll import PollCreate, PollUpdate


def _build_vote_counts(poll: Poll) -> list[int]:
    options = poll.options or []
    counts = [0] * len(options)

    for vote in poll.votes:
        if 0 <= vote.option_index < len(counts):
            counts[vote.option_index] += 1

    return counts


def serialize_poll(poll: Poll) -> dict:
    """Serialize poll ORM object with vote analytics."""
    counts = _build_vote_counts(poll)
    return {
        "id": poll.id,
        "question": poll.question,
        "description": poll.description,
        "options": poll.options or [],
        "is_active": poll.is_active,
        "created_by": str(poll.created_by),
        "created_at": poll.created_at,
        "updated_at": poll.updated_at,
        "active_till": poll.active_till,
        "votes": [
            {
                "user_id": str(vote.user_id),
                "option_index": vote.option_index,
                "voted_at": vote.voted_at,
            }
            for vote in poll.votes
        ],
        "option_vote_counts": counts,
        "total_votes": len(poll.votes),
    }


def get_all_polls(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> tuple[list[Poll], int]:
    """Get polls with optional status filter."""
    count_query = db.query(Poll)
    data_query = db.query(Poll).options(joinedload(Poll.votes))

    if is_active is not None:
        count_query = count_query.filter(Poll.is_active == is_active)
        data_query = data_query.filter(Poll.is_active == is_active)

    total = count_query.count()
    polls = data_query.order_by(Poll.created_at.desc()).offset(skip).limit(limit).all()
    return polls, total


def get_poll_by_id(db: Session, poll_id: int) -> Optional[Poll]:
    """Get a poll by ID with votes preloaded."""
    return db.query(Poll).options(joinedload(Poll.votes)).filter(Poll.id == poll_id).first()


def create_poll(db: Session, poll_data: PollCreate, user_id: str) -> Poll:
    """Create a poll."""
    poll = Poll(
        **poll_data.model_dump(),
        created_by=str(user_id),
    )
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return get_poll_by_id(db, poll.id)


def delete_poll(db: Session, poll_id: int) -> bool:
    """Delete a poll and all its votes."""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return False
    db.delete(poll)
    db.commit()
    return True


def update_poll(db: Session, poll_id: int, poll_data: PollUpdate) -> Optional[Poll]:
    """Update an existing poll's metadata (question, options, active state)."""
    poll = get_poll_by_id(db, poll_id)
    if not poll:
        return None
    update_fields = poll_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(poll, field, value)
    poll.updated_at = datetime.utcnow()
    db.commit()
    return get_poll_by_id(db, poll_id)


def vote_on_poll(db: Session, poll_id: int, user_id: str, option_index: int) -> Optional[Poll]:
    """Cast or update a user's vote for a poll."""
    poll = get_poll_by_id(db, poll_id)
    if not poll:
        return None

    options = poll.options or []
    if option_index < 0 or option_index >= len(options):
        raise ValueError("Invalid poll option")

    existing_vote = db.query(PollVote).filter(
        PollVote.poll_id == poll_id,
        PollVote.user_id == str(user_id),
    ).first()

    now = datetime.utcnow()
    if existing_vote:
        existing_vote.option_index = option_index
        existing_vote.voted_at = now
    else:
        db.add(
            PollVote(
                poll_id=poll_id,
                user_id=str(user_id),
                option_index=option_index,
                voted_at=now,
            )
        )

    poll.updated_at = now
    db.commit()

    return get_poll_by_id(db, poll_id)
