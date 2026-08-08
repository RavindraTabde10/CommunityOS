"""
Issues Management Endpoints
Handles issue reporting, tracking, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate
from app.schemas.contractor import (
    IssueAssignment, 
    IssueAssignmentResponse,
    WorkCompletionCreate,
    WorkCompletionResponse
)
from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
from app.models.user import User, UserRole
from app.models.activity import IssueActivity
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.services.contractor_service import WorkCompletionService

router = APIRouter()


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue: IssueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new issue
    
    Valid categories: electrical, plumbing, painting, carpentry, flooring, civil, other
    Valid priorities: low, medium, high, critical
    """
    try:
        # Validate and convert category
        try:
            category = IssueCategory(issue.category.lower())
        except ValueError:
            valid_categories = [cat.value for cat in IssueCategory]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid category '{issue.category}'. Valid categories: {', '.join(valid_categories)}"
            )
        
        # Validate and convert priority
        try:
            priority = IssuePriority(issue.priority.lower()) if issue.priority else IssuePriority.MEDIUM
        except ValueError:
            valid_priorities = [pri.value for pri in IssuePriority]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid priority '{issue.priority}'. Valid priorities: {', '.join(valid_priorities)}"
            )
        
        # Generate RGTS-XXXXXX ID
        # Get the count of existing issues to determine next number
        issue_count = db.query(Issue).count()
        next_number = issue_count + 1
        issue_number = f"{next_number:06d}"  # Format as 000001, 000002, etc.
        issue_id = f"RGTS-{issue_number}"
        
        # Check if ID already exists (race condition safety)
        while db.query(Issue).filter(Issue.id == issue_id).first():
            next_number += 1
            issue_number = f"{next_number:06d}"
            issue_id = f"RGTS-{issue_number}"
        
        # Validate assignee if provided (admin/facility only)
        assigned_to = None
        if issue.assigned_to:
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
            if user_role not in ["admin", "facility"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins and facility managers can assign issues"
                )
            assignee = db.query(User).filter(User.id == issue.assigned_to).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found"
                )
            assigned_to = issue.assigned_to

        # Create issue
        db_issue = Issue(
            id=issue_id,
            issue_number=issue_number,
            title=issue.title,
            description=issue.description,
            category=category,
            priority=priority,
            location=issue.location,
            unit_number=issue.unit_number,
            reported_by=current_user.id,
            assigned_to=assigned_to,
            status=IssueStatus.OPEN
        )
        
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        
        # Log activity
        activity = IssueActivity(
            issue_id=db_issue.id,
            user_id=current_user.id,
            action="created",
            description=f"{current_user.name} created the issue"
        )
        db.add(activity)
        
        if assigned_to:
            assign_activity = IssueActivity(
                issue_id=db_issue.id,
                user_id=current_user.id,
                action="updated",
                field_name="assigned_to",
                old_value=None,
                new_value=assigned_to,
                description=f"{current_user.name} assigned the issue"
            )
            db.add(assign_activity)
        
        db.commit()
        
        # Load relationships explicitly
        db_issue = db.query(Issue).options(
            joinedload(Issue.reporter),
            joinedload(Issue.assignee)
        ).filter(Issue.id == issue_id).first()
        
        return db_issue
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Print detailed error for debugging
        print(f"Error creating issue: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating issue: {str(e)}"
        )


@router.get("/", response_model=List[IssueResponse])
async def list_issues(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    category: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all issues with pagination and filters"""
    query = db.query(Issue).options(
        joinedload(Issue.reporter),
        joinedload(Issue.assignee)
    )
    
    # Apply filters
    if status:
        query = query.filter(Issue.status == status)
    if category:
        query = query.filter(Issue.category == category)

    issues = query.offset(skip).limit(limit).all()
    return issues


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get issue details by ID"""
    issue = db.query(Issue).options(
        joinedload(Issue.reporter),
        joinedload(Issue.assignee)
    ).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    return issue


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: str,
    issue_update: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update issue details"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check permissions
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    if user_role not in ["admin", "facility", "security"] and issue.reported_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this issue"
        )
    
    # Track changes for activity log
    changes = []
    update_data = issue_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        old_value = str(getattr(issue, field)) if hasattr(issue, field) else None
        
        if field == "assigned_to":
            # Only admins/facility can change assignee
            if user_role not in ["admin", "facility"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins and facility managers can assign issues"
                )
            if value is not None:
                assignee = db.query(User).filter(User.id == value).first()
                if not assignee:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Assigned user not found"
                    )
            if str(value) != old_value:
                changes.append((field, old_value, str(value) if value else None))
            setattr(issue, field, value)
        elif field == "status" and value:
            new_status = IssueStatus(value)
            if issue.status != new_status:
                changes.append((field, issue.status.value, new_status.value))
            setattr(issue, field, new_status)
        elif field == "category" and value:
            new_category = IssueCategory(value)
            if issue.category != new_category:
                changes.append((field, issue.category.value, new_category.value))
            setattr(issue, field, new_category)
        elif field == "priority" and value:
            new_priority = IssuePriority(value)
            if issue.priority != new_priority:
                changes.append((field, issue.priority.value, new_priority.value))
            setattr(issue, field, new_priority)
        elif value != old_value:
            changes.append((field, old_value, str(value)))
            setattr(issue, field, value)
    
    db.commit()
    db.refresh(issue)
    
    # Log activities for each change
    for field_name, old_val, new_val in changes:
        activity = IssueActivity(
            issue_id=issue.id,
            user_id=current_user.id,
            action="updated",
            field_name=field_name,
            old_value=old_val,
            new_value=new_val,
            description=f"{current_user.name} changed {field_name} from {old_val} to {new_val}"
        )
        db.add(activity)
    
    if changes:
        db.commit()
    
    # Reload with relationships
    issue = db.query(Issue).options(
        joinedload(Issue.reporter),
        joinedload(Issue.assignee)
    ).filter(Issue.id == issue_id).first()
    
    return issue


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Only admin or issue reporter can delete
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    if user_role != "admin" and issue.reported_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this issue"
        )
    
    try:
        # Log activity before deleting
        activity = IssueActivity(
            issue_id=issue.id,
            user_id=current_user.id,
            action="deleted",
            description=f"{current_user.name} deleted the issue"
        )
        db.add(activity)
        db.commit()
        
        db.delete(issue)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error deleting issue {issue_id}: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting issue: {str(e)}"
        )
    
    return None


# ==================== CONTRACTOR ASSIGNMENT ====================

@router.post("/{issue_id}/assign", response_model=IssueAssignmentResponse)
async def assign_issue_to_contractor(
    issue_id: str,
    assignment_data: IssueAssignment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign an issue to a contractor (Admin/Facility only)
    
    Requirements:
    - User must be admin or facility manager
    - Contractor user must have contractor role
    - Issue must exist and be open
    """
    # Check permission
    if current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or facility managers can assign issues"
        )
    
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Verify contractor user exists and has contractor role
    contractor_user = db.query(User).filter(User.id == assignment_data.contractor_id).first()
    if not contractor_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor user not found"
        )
    
    if contractor_user.role != UserRole.CONTRACTOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have contractor role to be assigned issues"
        )
    
    try:
        # Track previous assignment for activity log
        old_assignee = issue.assigned_to
        
        # Assign contractor
        issue.assigned_to = assignment_data.contractor_id
        issue.status = IssueStatus.IN_PROGRESS
        issue.updated_at = datetime.utcnow()
        
        # Log activity
        activity = IssueActivity(
            issue_id=issue.id,
            user_id=current_user.id,
            action="assigned",
            field_name="assigned_to",
            old_value=old_assignee,
            new_value=assignment_data.contractor_id,
            description=f"{current_user.name} assigned issue to {contractor_user.name}. Notes: {assignment_data.notes or 'None'}"
        )
        db.add(activity)
        
        db.commit()
        db.refresh(issue)
        
        return {
            "issue_id": issue.id,
            "assigned_to": issue.assigned_to,
            "assigned_at": datetime.utcnow(),
            "status": issue.status.value
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign issue: {str(e)}"
        )


@router.delete("/{issue_id}/assign", status_code=status.HTTP_200_OK)
async def unassign_contractor(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unassign contractor from an issue (Admin/Facility only)
    
    Removes the contractor assignment and resets issue status to open.
    """
    # Check permission
    if current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or facility managers can unassign issues"
        )
    
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    if not issue.assigned_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issue is not assigned to any contractor"
        )
    
    try:
        old_assignee = issue.assigned_to
        
        # Unassign
        issue.assigned_to = None
        issue.status = IssueStatus.OPEN
        issue.updated_at = datetime.utcnow()
        
        # Log activity
        activity = IssueActivity(
            issue_id=issue.id,
            user_id=current_user.id,
            action="unassigned",
            field_name="assigned_to",
            old_value=old_assignee,
            new_value=None,
            description=f"{current_user.name} unassigned the contractor"
        )
        db.add(activity)
        
        db.commit()
        
        return {"message": "Contractor unassigned successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unassign contractor: {str(e)}"
        )


# ==================== WORK COMPLETION ====================

@router.post("/{issue_id}/complete", response_model=WorkCompletionResponse, status_code=status.HTTP_201_CREATED)
async def mark_work_complete(
    issue_id: str,
    completion_data: WorkCompletionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark work as complete for an issue (Contractor only)
    
    Requirements:
    - User must be the assigned contractor
    - Issue must be assigned to this contractor
    - Work can only be marked complete once
    
    Automatically updates issue status to RESOLVED.
    """
    work_completion = WorkCompletionService.mark_work_complete(
        issue_id=issue_id,
        completion_data=completion_data,
        contractor_user_id=current_user.id,
        db=db
    )
    
    return work_completion
