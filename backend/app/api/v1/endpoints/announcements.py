"""
Announcement API Endpoints
RESTful API for announcement management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse
)
from app.services.announcement_service import AnnouncementService

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create new announcement (Admin only)
    
    **Permissions**: Admin only
    
    **Request Body**:
    - title: Announcement title (max 200 chars)
    - content: Full announcement message
    - priority: Priority level (low, normal, high, critical)
    - is_active: Active status (default: true)
    - start_date: Optional start date
    - end_date: Optional end date
    
    **Returns**: Created announcement
    """
    announcement = AnnouncementService.create_announcement(
        db=db,
        announcement_data=announcement_data,
        created_by=current_user.id
    )
    return announcement


@router.get("/active", response_model=List[AnnouncementResponse])
async def get_active_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active announcements (All authenticated users)
    
    **Permissions**: All authenticated users
    
    **Filtering**:
    - Only active announcements (is_active = true)
    - Within date range (if start_date/end_date set)
    - Ordered by priority (highest first) and creation date
    
    **Returns**: List of active announcements
    """
    announcements = AnnouncementService.get_active_announcements(db=db)
    return announcements


@router.get("/", response_model=List[AnnouncementResponse])
async def get_all_announcements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all announcements including inactive (Admin only)
    
    **Permissions**: Admin only
    
    **Query Parameters**:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100)
    
    **Returns**: List of all announcements
    """
    announcements = AnnouncementService.get_all_announcements(
        db=db,
        skip=skip,
        limit=limit
    )
    return announcements


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get announcement by ID
    
    **Permissions**: All authenticated users
    
    **Path Parameters**:
    - announcement_id: UUID of the announcement
    
    **Returns**: Announcement details
    
    **Raises**:
    - 404: Announcement not found
    """
    announcement = AnnouncementService.get_announcement_by_id(
        db=db,
        announcement_id=announcement_id
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    return announcement


@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: str,
    update_data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update announcement (Admin only)
    
    **Permissions**: Admin only
    
    **Path Parameters**:
    - announcement_id: UUID of the announcement
    
    **Request Body**: (all fields optional)
    - title: Updated title
    - content: Updated content
    - priority: Updated priority
    - is_active: Updated active status
    - start_date: Updated start date
    - end_date: Updated end date
    
    **Returns**: Updated announcement
    
    **Raises**:
    - 404: Announcement not found
    """
    announcement = AnnouncementService.get_announcement_by_id(
        db=db,
        announcement_id=announcement_id
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    updated_announcement = AnnouncementService.update_announcement(
        db=db,
        announcement=announcement,
        update_data=update_data
    )
    return updated_announcement


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete announcement (Admin only)
    
    **Permissions**: Admin only
    
    **Path Parameters**:
    - announcement_id: UUID of the announcement
    
    **Returns**: 204 No Content on success
    
    **Raises**:
    - 404: Announcement not found
    """
    announcement = AnnouncementService.get_announcement_by_id(
        db=db,
        announcement_id=announcement_id
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    AnnouncementService.delete_announcement(db=db, announcement=announcement)
    return None
