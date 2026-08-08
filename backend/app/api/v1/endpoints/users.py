"""
User Management Endpoints
Handles user profile updates, password changes, and admin user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserResponse, 
    UserUpdate, 
    PasswordChange, 
    UserListResponse,
    UserRoleUpdate,
    UserStatusUpdate,
    UserCreate,
)
from app.api.v1.endpoints.auth import get_current_user
from app.services.auth_service import AuthService


router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def _assert_unit_residency_unique(db: Session, unit_number: str, residency_type: str, exclude_user_id: str):
    """Raise 409 if another active resident already occupies this unit with the same residency_type."""
    conflict = (
        db.query(User)
        .filter(
            User.unit_number == unit_number,
            User.residency_type == residency_type,
            User.role == UserRole.RESIDENT,
            User.is_active == True,
            User.id != exclude_user_id,
        )
        .first()
    )
    if conflict:
        label = "owner" if residency_type == "owner" else "tenant"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unit {unit_number} already has a registered {label}: {conflict.name}"
        )


# ==================== USER PROFILE MANAGEMENT ====================

@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    Users can update their own name, phone, and unit_number
    """
    try:
        # Update only provided fields
        if user_update.name is not None:
            current_user.name = user_update.name
        if user_update.phone is not None:
            current_user.phone = user_update.phone
        # unit_number and residency_type are admin-only fields
        if current_user.role == UserRole.ADMIN:
            if user_update.unit_number is not None:
                current_user.unit_number = user_update.unit_number
            if user_update.residency_type is not None:
                current_user.residency_type = user_update.residency_type
        
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        return current_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    
    Requires current password for verification
    """
    # Verify current password
    if not AuthService.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    if password_data.new_password == password_data.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    try:
        # Update password
        current_user.password_hash = AuthService.get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


# ==================== ADMIN USER MANAGEMENT ====================

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only). When creating a tenant for a unit that already
    has an active tenant, the previous tenant is automatically deactivated."""
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        role_enum = UserRole(user_data.role.lower())
    except ValueError:
        role_enum = UserRole.RESIDENT

    # Auto-deactivate the previous tenant when a new one is registered for the same unit
    if user_data.unit_number and user_data.residency_type == 'tenant':
        old_tenant = db.query(User).filter(
            User.unit_number == user_data.unit_number,
            User.residency_type == 'tenant',
            User.role == UserRole.RESIDENT,
            User.is_active == True,
        ).first()
        if old_tenant:
            old_tenant.is_active = False
            old_tenant.updated_at = datetime.utcnow()
    
    new_user = User(
        email=user_data.email,
        password_hash=AuthService.get_password_hash(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
        role=role_enum,
        unit_number=user_data.unit_number,
        residency_type=user_data.residency_type,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    role: Optional[str] = Query(None, description="Filter by role"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by account status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List users with pagination. Admins see all users; other roles see only active residents.
    """
    print(f"DEBUG: list_users called with is_active={is_active}, type={type(is_active)}")

    # Non-admins may only browse the resident directory
    if current_user.role != UserRole.ADMIN:
        role = 'resident'
        is_active = True

    query = db.query(User)

    # Apply role filter
    if role:
        try:
            role_enum = UserRole(role.lower())
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Valid roles: {', '.join([r.value for r in UserRole])}"
            )
    
    # Apply status filter (for pending approvals)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_pattern)) | (User.email.ilike(search_pattern))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    # Debug logging
    print(f"DEBUG: Found {total} users, returning {len(users)} users")
    
    return UserListResponse(
        users=users,
        total=total,
        skip=skip,
        limit=limit
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update any user's profile (Admin only)
    
    Admins can update any user's name, phone, and unit_number
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Update only provided fields
        if user_update.name is not None:
            user.name = user_update.name
        if user_update.phone is not None:
            user.phone = user_update.phone
        if user_update.unit_number is not None:
            user.unit_number = user_update.unit_number
        if user_update.residency_type is not None:
            user.residency_type = user_update.residency_type

        # Enforce: max 1 owner and 1 tenant per unit
        if user.unit_number and user.residency_type and user.role == UserRole.RESIDENT:
            _assert_unit_residency_unique(db, user.unit_number, user.residency_type, user.id)

        # Tenant must have name and phone so visitor requests can be routed
        effective_type = user_update.residency_type or user.residency_type
        if effective_type == 'tenant':
            effective_name = user_update.name or user.name
            effective_phone = user_update.phone or user.phone
            if not effective_name or not effective_name.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Tenant name is required for visitor request routing"
                )
            if not effective_phone or not effective_phone.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Tenant phone number is required for visitor request routing"
                )

        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user's role (Admin only)
    
    Change a user's role (resident, contractor, admin, etc.)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    try:
        role_enum = UserRole(role_update.role.lower())
    except ValueError:
        valid_roles = [r.value for r in UserRole]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Valid roles: {', '.join(valid_roles)}"
        )
    
    try:
        user.role = role_enum
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user account (Admin only)
    
    Deactivated users cannot log in
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own status"
        )
    
    try:
        user.is_active = status_update.is_active
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user account (Admin only)
    
    Warning: This is a hard delete and cannot be undone
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    try:
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
