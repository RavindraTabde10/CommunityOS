"""
Photo Upload Endpoints
Handle issue photo uploads
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os

from app.db.session import get_db
from app.models.user import User
from app.models.issue import Issue, IssuePhoto
from app.schemas.issue import IssuePhotoResponse
from app.api.v1.endpoints.auth import get_current_user
from app.services.s3_service import s3_service
from app.core.config import settings


router = APIRouter()


# Allowed image types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/issues/{issue_id}/photos", response_model=IssuePhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_issue_photo(
    issue_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a photo for an issue
    
    - **issue_id**: ID of the issue
    - **file**: Image file (JPEG, PNG, WebP, max 5MB)
    """
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check permission: Only reporter, assigned user, or admin can add photos
    if (issue.reported_by != current_user.id and 
        issue.assigned_to != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to upload photos for this issue"
        )
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file extension. Allowed: .jpg, .jpeg, .png, .webp"
        )
    
    # Upload to S3
    try:
        photo_url = s3_service.upload_file(
            file_content=file_content,
            file_name=file.filename,
            content_type=file.content_type,
            folder=f"issues/{issue_id}"
        )
        
        if not photo_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
    
    # Save photo metadata to database
    issue_photo = IssuePhoto(
        issue_id=issue_id,
        photo_url=photo_url
    )
    db.add(issue_photo)
    db.commit()
    db.refresh(issue_photo)
    
    return issue_photo


@router.get("/issues/{issue_id}/photos", response_model=List[IssuePhotoResponse])
def list_issue_photos(
    issue_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all photos for an issue
    
    - **issue_id**: ID of the issue
    """
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Check permission
    if (issue.reported_by != current_user.id and 
        issue.assigned_to != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view photos for this issue"
        )
    
    # Get photos
    photos = db.query(IssuePhoto).filter(IssuePhoto.issue_id == issue_id).all()
    return photos


@router.delete("/photos/{photo_id}", status_code=status.HTTP_200_OK)
def delete_photo(
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a photo
    
    - **photo_id**: ID of the photo to delete
    """
    # Get photo
    photo = db.query(IssuePhoto).filter(IssuePhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Get associated issue
    issue = db.query(Issue).filter(Issue.id == photo.issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Associated issue not found")
    
    # Check permission: Only reporter, assigned user, or admin can delete photos
    if (issue.reported_by != current_user.id and 
        issue.assigned_to != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this photo"
        )
    
    # Delete from S3
    try:
        s3_service.delete_file(photo.photo_url)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete file from S3: {str(e)}")
    
    # Delete from database
    db.delete(photo)
    db.commit()
    
    return {"message": "Photo deleted successfully"}
