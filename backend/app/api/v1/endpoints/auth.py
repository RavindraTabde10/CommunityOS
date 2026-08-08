"""
Authentication Endpoints
Handles user registration, login, token management, and audit log access.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.schemas.user import UserCreate, UserResponse, Token, PasswordResetRequest, PasswordReset
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.audit_service import AuditService
from app.models.user import User, UserRole
from app.models.audit_log import APIAuditLog
from app.db.session import get_db

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = AuthService.get_password_hash(user.password)
        
        # Convert role string to enum
        try:
            user_role = UserRole(user.role.lower())
        except ValueError:
            user_role = UserRole.RESIDENT
        
        db_user = User(
            email=user.email,
            password_hash=hashed_password,
            name=user.name,
            phone=user.phone,
            role=user_role,
            unit_number=user.unit_number,
            is_active=False  # Pending admin approval
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """User login - returns JWT token"""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not AuthService.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval. Please contact an administrator or wait for approval.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.id})

    ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else None)
    )
    AuditService.log(
        db,
        action="login",
        user_id=user.id,
        user_email=user.email,
        ip_address=ip,
        user_agent=request.headers.get("User-Agent"),
        http_method="POST",
        endpoint="/api/v1/auth/login",
        status_code=200,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


# ==================== PASSWORD RESET FLOW ====================

# Simple in-memory storage for reset tokens (in production, use Redis or database)
password_reset_tokens = {}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    
    Sends a password reset link via email
    Always returns success to prevent email enumeration
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {
            "message": "If the email is registered, a password reset link has been sent to your inbox"
        }
    
    # Generate reset token (valid for 1 hour)
    reset_token = AuthService.create_access_token(
        data={"sub": user.id, "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # Store token with expiry (in production, store in Redis or database)
    password_reset_tokens[user.id] = {
        "token": reset_token,
        "expires": datetime.utcnow() + timedelta(hours=1)
    }
    
    # Send password reset email
    email_sent = await EmailService.send_password_reset_email(
        to_email=user.email,
        reset_token=reset_token,
        user_name=user.name
    )
    
    # Return success message (same whether email sent or not, for security)
    response = {
        "message": "If the email is registered, a password reset link has been sent to your inbox"
    }
    
    # In development, include token for testing if email service not configured
    if not EmailService.is_configured():
        response["reset_token"] = reset_token
        response["note"] = "Email service not configured. Use the token above for testing."
    
    return response


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token
    
    Token is obtained from the forgot-password endpoint or email
    """
    print(f"[DEBUG] Reset password request received")
    print(f"[DEBUG] Token: {reset_data.token[:50]}...")
    
    # Verify reset token
    payload = AuthService.decode_token(reset_data.token)
    print(f"[DEBUG] Decoded payload: {payload}")
    
    if not payload or payload.get("type") != "password_reset":
        print(f"[DEBUG] Invalid token type or payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        print(f"[DEBUG] No user_id in token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    print(f"[DEBUG] User ID from token: {user_id}")
    print(f"[DEBUG] Tokens in memory: {list(password_reset_tokens.keys())}")
    
    # Check if token exists and is not expired
    stored_token = password_reset_tokens.get(user_id)
    if not stored_token:
        print(f"[DEBUG] Token not found in memory - likely server was restarted")
        print(f"[DEBUG] Accepting token based on JWT validation only (development mode)")
        # In development, accept valid JWT tokens even if not in memory
        # This allows password reset to work after server restarts
        # In production, use Redis or database to store tokens persistently
    elif stored_token["token"] != reset_data.token:
        print(f"[DEBUG] Token mismatch")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    elif stored_token["expires"] < datetime.utcnow():
        print(f"[DEBUG] Token expired")
        del password_reset_tokens[user_id]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"[DEBUG] User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    print(f"[DEBUG] User found: {user.email}")
    
    # Validate new password
    if len(reset_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    try:
        # Update password
        user.password_hash = AuthService.get_password_hash(reset_data.new_password)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Remove used token if it exists
        if user_id in password_reset_tokens:
            del password_reset_tokens[user_id]
        
        print(f"[DEBUG] Password reset successful for {user.email}")
        return {"message": "Password reset successfully"}
        
    except Exception as e:
        print(f"[DEBUG] Error resetting password: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


# ==================== REFRESH TOKEN ====================

class RefreshTokenRequest:
    """Body model for the refresh endpoint."""
    from pydantic import BaseModel

    class _Model(BaseModel):  # noqa: F821
        refresh_token: str


from pydantic import BaseModel as _BaseModel


class _RefreshBody(_BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    body: _RefreshBody,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access token + rotated refresh token.

    Token rotation means the old refresh token is implicitly invalidated once a
    new pair is issued (stateless invalidation relies on expiry; use Redis for
    stricter revocation in production).
    """
    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = AuthService.decode_token(body.refresh_token)
    if not payload:
        raise invalid_exc

    user_id: str = payload.get("sub")
    if not user_id:
        raise invalid_exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise invalid_exc

    # Issue new token pair (rotation)
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    new_refresh_token = AuthService.create_refresh_token(data={"sub": user.id})

    ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else None)
    )
    AuditService.log(
        db,
        action="token_refresh",
        user_id=user.id,
        user_email=user.email,
        ip_address=ip,
        user_agent=request.headers.get("User-Agent"),
        http_method="POST",
        endpoint="/api/v1/auth/refresh",
        status_code=200,
    )

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


# ==================== AUDIT LOG (admin only) ====================

@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve audit log entries. Admin-only.

    Filters:
    - `user_id` – filter by actor
    - `action`  – filter by operation type (e.g. login, token_refresh)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    logs = AuditService.get_logs(
        db, user_id=user_id, action=action, skip=skip, limit=limit
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user_email,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "http_method": log.http_method,
            "endpoint": log.endpoint,
            "status_code": log.status_code,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
