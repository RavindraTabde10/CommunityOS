"""
Announcement Service
Business logic for announcement operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
import uuid

from app.models.announcement import Announcement, AnnouncementPriority
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate


class AnnouncementService:
    """Service class for announcement operations"""
    
    @staticmethod
    def create_announcement(
        db: Session,
        announcement_data: AnnouncementCreate,
        created_by: str
    ) -> Announcement:
        """
        Create a new announcement
        
        Args:
            db: Database session
            announcement_data: Announcement creation data
            created_by: User ID of creator
            
        Returns:
            Created announcement
        """
        announcement = Announcement(
            id=str(uuid.uuid4()),
            created_by=created_by,
            **announcement_data.model_dump()
        )
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return announcement
    
    @staticmethod
    def get_active_announcements(
        db: Session
    ) -> List[Announcement]:
        """
        Get all active announcements
        Filters by:
        - is_active = True
        - Current date is between start_date and end_date (if set)
        - Orders by priority (desc) and created_at (desc)
        
        Args:
            db: Database session
            
        Returns:
            List of active announcements
        """
        now = datetime.utcnow()
        
        query = db.query(Announcement).filter(
            and_(
                Announcement.is_active == True,
                or_(
                    Announcement.start_date.is_(None),
                    Announcement.start_date <= now
                ),
                or_(
                    Announcement.end_date.is_(None),
                    Announcement.end_date >= now
                )
            )
        ).order_by(
            Announcement.priority.desc(),
            Announcement.created_at.desc()
        )
        
        return query.all()
    
    @staticmethod
    def get_all_announcements(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Announcement]:
        """
        Get all announcements (admin view)
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of all announcements
        """
        return db.query(Announcement).order_by(
            Announcement.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_announcement_by_id(
        db: Session,
        announcement_id: str
    ) -> Optional[Announcement]:
        """
        Get announcement by ID
        
        Args:
            db: Database session
            announcement_id: Announcement ID
            
        Returns:
            Announcement or None
        """
        return db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
    
    @staticmethod
    def update_announcement(
        db: Session,
        announcement: Announcement,
        update_data: AnnouncementUpdate
    ) -> Announcement:
        """
        Update announcement with provided data
        
        Args:
            db: Database session
            announcement: Announcement to update
            update_data: Update data (only non-None fields are updated)
            
        Returns:
            Updated announcement
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(announcement, field, value)
        
        db.commit()
        db.refresh(announcement)
        return announcement
    
    @staticmethod
    def delete_announcement(
        db: Session,
        announcement: Announcement
    ) -> None:
        """
        Delete announcement
        
        Args:
            db: Database session
            announcement: Announcement to delete
        """
        db.delete(announcement)
        db.commit()
