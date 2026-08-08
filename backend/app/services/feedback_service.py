"""
Feedback Service
Business logic for feedback and suggestions.
"""
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate


def create_feedback(db: Session, data: FeedbackCreate, user_id: str) -> Feedback:
    fb = Feedback(
        title=data.title,
        category=data.category,
        description=data.description,
        submitted_by=str(user_id),
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return _load(db, fb.id)


def get_feedback(db: Session, feedback_id: str) -> Optional[Feedback]:
    return db.query(Feedback).options(joinedload(Feedback.submitter)).filter(Feedback.id == feedback_id).first()


def get_all_feedback(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
) -> tuple[list[Feedback], int]:
    query = db.query(Feedback).options(joinedload(Feedback.submitter))
    if user_id:
        query = query.filter(Feedback.submitted_by == str(user_id))
    if status:
        query = query.filter(Feedback.status == status)
    total = query.count()
    rows = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
    return rows, total


def edit_feedback(db: Session, feedback_id: str, data) -> Optional[Feedback]:
    """Allow the original submitter to update content of pending feedback."""
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        return None
    if data.title is not None:
        fb.title = data.title
    if data.category is not None:
        fb.category = data.category
    if data.description is not None:
        fb.description = data.description
    db.commit()
    return _load(db, feedback_id)


def update_feedback(db: Session, feedback_id: str, data: FeedbackUpdate, responder_id: str) -> Optional[Feedback]:
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        return None
    if data.status is not None:
        fb.status = data.status
    if data.admin_response is not None:
        fb.admin_response = data.admin_response
        fb.responded_by = str(responder_id)
    db.commit()
    return _load(db, feedback_id)


def delete_feedback(db: Session, feedback_id: str) -> bool:
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        return False
    db.delete(fb)
    db.commit()
    return True


def _load(db: Session, feedback_id: str) -> Optional[Feedback]:
    return db.query(Feedback).options(joinedload(Feedback.submitter)).filter(Feedback.id == feedback_id).first()
