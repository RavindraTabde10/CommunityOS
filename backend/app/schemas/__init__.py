"""
Schemas package - Pydantic models for request/response validation
"""
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
)
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
)
from app.schemas.activity import (
    ActivityResponse,
    ActivityListResponse,
)
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    CheckInRequest,
    CheckInResponse,
    CheckOutRequest,
    CheckOutResponse,
    AvailabilityCheck,
    AvailabilityResponse,
    AssetStatsResponse,
    QRCodeResponse,
    QRCodeScanRequest,
    QRCodeScanResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "PasswordChange",
    "PasswordResetRequest",
    "PasswordReset",
    "UserRoleUpdate",
    "UserStatusUpdate",
    # Issue schemas
    "IssueCreate",
    "IssueUpdate",
    "IssueResponse",
    # Comment schemas
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentListResponse",
    # Activity schemas
    "ActivityResponse",
    "ActivityListResponse",
    # Asset schemas
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    # Booking schemas
    "BookingCreate",
    "BookingUpdate",
    "BookingResponse",
    "CheckInRequest",
    "CheckInResponse",
    "CheckOutRequest",
    "CheckOutResponse",
    "AvailabilityCheck",
    "AvailabilityResponse",
    "AssetStatsResponse",
    "QRCodeResponse",
    "QRCodeScanRequest",
    "QRCodeScanResponse",
]
