"""
Comments API Endpoints
Handles CRUD operations for issue comments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.user import User, UserRole
from app.models.activity import IssueActivity
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from app.schemas.activity import ActivityResponse, ActivityListResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


def log_activity(
    db: Session,
    issue_id: int,
    user_id: str,
    action: str,
    description: str,
    field_name: str = None,
    old_value: str = None,
    new_value: str = None
):
    """Helper function to log issue activity"""
    activity = IssueActivity(
        issue_id=issue_id,
        user_id=user_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        description=description
    )
    db.add(activity)
    db.commit()


@router.post("/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    issue_id: str,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on an issue.
    
    - **issue_id**: ID of the issue to comment on
    - **content**: Comment text (1-2000 characters)
    
    Users can comment on:
    - Their own issues (always)
    - Any issue if they are admin/builder
    """
    # Check if issue exists
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check permissions: Can comment on own issues or if admin/builder
    if current_user.role not in [UserRole.ADMIN, UserRole.BUILDER]:
        if db_issue.reported_by != current_user.id and db_issue.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to comment on this issue"
            )
    
    # Create comment
    db_comment = Comment(
        content=comment.content,
        issue_id=issue_id,
        user_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Log activity
    log_activity(
        db=db,
        issue_id=issue_id,
        user_id=current_user.id,
        action="commented",
        description=f"{current_user.name} added a comment"
    )
    
    # Prepare response
    response = CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        issue_id=db_comment.issue_id,
        user_id=db_comment.user_id,
        user_name=current_user.name,
        user_email=current_user.email,
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        is_own=True
    )
    
    return response


@router.get("/{issue_id}/comments", response_model=CommentListResponse)
def list_comments(
    issue_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all comments for an issue with pagination.
    
    - **issue_id**: ID of the issue
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 50, max: 100)
    
    Comments are ordered by creation time (newest first).
    """
    # Check if issue exists
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check permissions: Can view comments on own issues or if admin/builder
    if current_user.role not in [UserRole.ADMIN, UserRole.BUILDER]:
        if db_issue.reported_by != current_user.id and db_issue.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view comments on this issue"
            )
    
    # Limit max results
    if limit > 100:
        limit = 100
    
    # Get comments with user info
    comments_query = db.query(Comment).filter(
        Comment.issue_id == issue_id,
        Comment.is_deleted == False
    ).order_by(Comment.created_at.desc())
    
    total = comments_query.count()
    comments = comments_query.offset(skip).limit(limit).all()
    
    # Build response with user info
    comment_responses = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        comment_responses.append(
            CommentResponse(
                id=comment.id,
                content=comment.content,
                issue_id=comment.issue_id,
                user_id=comment.user_id,
                user_name=user.name if user else "Unknown User",
                user_email=user.email if user else "",
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                is_own=(comment.user_id == current_user.id)
            )
        )
    
    return CommentListResponse(
        comments=comment_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment.
    
    - **comment_id**: ID of the comment to update
    - **content**: New comment text (1-2000 characters)
    
    Only the comment owner or admins can update comments.
    """
    # Get comment
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check permissions: Owner or admin
    if db_comment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )
    
    # Update comment
    old_content = db_comment.content
    db_comment.content = comment_update.content
    db_comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_comment)
    
    # Log activity
    log_activity(
        db=db,
        issue_id=db_comment.issue_id,
        user_id=current_user.id,
        action="edited_comment",
        description=f"{current_user.name} edited a comment"
    )
    
    # Get user info for response
    user = db.query(User).filter(User.id == db_comment.user_id).first()
    
    return CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        issue_id=db_comment.issue_id,
        user_id=db_comment.user_id,
        user_name=user.name if user else "Unknown User",
        user_email=user.email if user else "",
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        is_own=(db_comment.user_id == current_user.id)
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment (soft delete).
    
    - **comment_id**: ID of the comment to delete
    
    Only the comment owner or admins can delete comments.
    """
    # Get comment
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check permissions: Owner or admin
    if db_comment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    # Soft delete
    db_comment.is_deleted = True
    db_comment.updated_at = datetime.utcnow()
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        issue_id=db_comment.issue_id,
        user_id=current_user.id,
        action="deleted_comment",
        description=f"{current_user.name} deleted a comment"
    )
    
    return None


@router.get("/{issue_id}/activity", response_model=ActivityListResponse)
def get_issue_activity(
    issue_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity log for an issue.
    
    - **issue_id**: ID of the issue
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 50, max: 100)
    
    Shows all changes, comments, and updates for the issue.
    Activities are ordered by time (newest first).
    """
    # Check if issue exists
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check permissions: Can view activity on own issues or if admin/builder
    if current_user.role not in [UserRole.ADMIN, UserRole.BUILDER]:
        if db_issue.reported_by != current_user.id and db_issue.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view activity for this issue"
            )
    
    # Limit max results
    if limit > 100:
        limit = 100
    
    # Get activities
    activities_query = db.query(IssueActivity).filter(
        IssueActivity.issue_id == issue_id
    ).order_by(IssueActivity.created_at.desc())
    
    total = activities_query.count()
    activities = activities_query.offset(skip).limit(limit).all()
    
    # Build response with user info
    activity_responses = []
    for activity in activities:
        user = db.query(User).filter(User.id == activity.user_id).first() if activity.user_id else None
        activity_responses.append(
            ActivityResponse(
                id=activity.id,
                issue_id=activity.issue_id,
                user_id=activity.user_id,
                user_name=user.name if user else "System",
                action=activity.action,
                field_name=activity.field_name,
                old_value=activity.old_value,
                new_value=activity.new_value,
                description=activity.description,
                created_at=activity.created_at
            )
        )
    
    return ActivityListResponse(
        activities=activity_responses,
        total=total,
        skip=skip,
        limit=limit
    )
