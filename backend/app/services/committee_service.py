"""
Committee Service
Business logic for committee member management
"""
from sqlalchemy.orm import Session, joinedload
from app.models.committee_member import CommitteeMember
from app.models.user import User
from app.schemas.committee_member import CommitteeMemberCreate, CommitteeMemberUpdate
from typing import List, Optional


def create_committee_member(db: Session, data: CommitteeMemberCreate) -> CommitteeMember:
    """Create a new committee member"""
    member = CommitteeMember(**data.dict())
    db.add(member)
    db.commit()
    db.refresh(member)
    
    # Load the user relationship
    member = db.query(CommitteeMember).options(
        joinedload(CommitteeMember.user)
    ).filter(CommitteeMember.id == member.id).first()
    
    return member


def get_active_committee_members(db: Session) -> List[dict]:
    """Get all active committee members ordered by display_order"""
    members = db.query(CommitteeMember).filter(
        CommitteeMember.is_active == True
    ).options(
        joinedload(CommitteeMember.user)
    ).order_by(
        CommitteeMember.display_order
    ).all()
    
    # Format response with user data
    result = []
    for member in members:
        result.append({
            "id": member.id,
            "role": member.role,
            "position_name": member.position_name,
            "responsibilities": member.responsibilities,
            "contact_email": member.contact_email or (member.user.email if member.user else None),
            "contact_phone": member.contact_phone,
            "user_name": member.user.name if member.user else None,
            "user_email": member.user.email if member.user else None,
            "user_unit": member.user.unit_number if member.user else None,
            "display_order": member.display_order,
            "term_start_date": member.term_start_date,
            "term_end_date": member.term_end_date,
            "is_active": member.is_active,
            "created_at": member.created_at,
            "user_id": member.user_id
        })
    return result


def get_all_committee_members(db: Session) -> List[CommitteeMember]:
    """Get all committee members (for admin)"""
    return db.query(CommitteeMember).options(
        joinedload(CommitteeMember.user)
    ).order_by(CommitteeMember.display_order).all()


def get_committee_member_by_id(db: Session, member_id: int) -> Optional[CommitteeMember]:
    """Get committee member by ID"""
    return db.query(CommitteeMember).options(
        joinedload(CommitteeMember.user)
    ).filter(CommitteeMember.id == member_id).first()


def update_committee_member(
    db: Session, 
    member_id: int, 
    data: CommitteeMemberUpdate
) -> Optional[CommitteeMember]:
    """Update committee member"""
    member = get_committee_member_by_id(db, member_id)
    if not member:
        return None
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(member, key, value)
    
    db.commit()
    db.refresh(member)
    
    # Reload with user relationship
    member = db.query(CommitteeMember).options(
        joinedload(CommitteeMember.user)
    ).filter(CommitteeMember.id == member_id).first()
    
    return member


def delete_committee_member(db: Session, member_id: int) -> bool:
    """Delete committee member"""
    member = get_committee_member_by_id(db, member_id)
    if not member:
        return False
    
    db.delete(member)
    db.commit()
    return True
