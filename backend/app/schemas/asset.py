"""
Asset & Facility Management Pydantic Schemas
Request/Response models for asset and booking endpoints
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date, time
from decimal import Decimal


# Type definitions
AssetTypeType = Literal["gym", "pool", "clubhouse", "party_hall", "sports_court", "meeting_room", "parking", "other"]
BookingStatusType = Literal["pending", "confirmed", "cancelled", "completed", "no_show"]
PaymentStatusType = Literal["pending", "paid", "refunded"]


class UserSummary(BaseModel):
    """User summary for responses"""
    id: str
    name: str
    email: str
    
    class Config:
        from_attributes = True


# ========== Asset Schemas ==========

class AssetBase(BaseModel):
    """Base asset schema"""
    name: str = Field(..., min_length=2, max_length=100, description="Asset name")
    asset_type: AssetTypeType = Field(..., description="Type of asset/facility")
    description: Optional[str] = Field(None, description="Detailed description")
    location: Optional[str] = Field(None, description="Physical location (building/floor)")
    capacity: Optional[int] = Field(None, gt=0, description="Maximum occupancy")
    hourly_rate: Optional[Decimal] = Field(default=Decimal("0"), ge=0, description="Cost per hour")
    is_bookable: bool = Field(default=True, description="Can be booked online")
    advance_booking_days: Optional[int] = Field(default=30, ge=1, le=365, description="How far in advance can book")
    min_booking_duration: Optional[int] = Field(default=60, ge=15, description="Minimum booking duration (minutes)")
    max_booking_duration: Optional[int] = Field(default=240, ge=30, description="Maximum booking duration (minutes)")
    max_guests_per_booking: Optional[int] = Field(None, ge=1, description="Max guests one person can bring per booking")
    operating_hours_start: Optional[time] = Field(None, description="Opening time")
    operating_hours_end: Optional[time] = Field(None, description="Closing time")


class AssetCreate(AssetBase):
    """Schema for creating an asset"""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an asset"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    asset_type: Optional[AssetTypeType] = None
    description: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    is_bookable: Optional[bool] = None
    is_active: Optional[bool] = None
    advance_booking_days: Optional[int] = Field(None, ge=1, le=365)
    min_booking_duration: Optional[int] = Field(None, ge=15)
    max_booking_duration: Optional[int] = Field(None, ge=30)
    max_guests_per_booking: Optional[int] = Field(None, ge=1)
    operating_hours_start: Optional[time] = None
    operating_hours_end: Optional[time] = None


class AssetResponse(AssetBase):
    """Schema for asset response"""
    id: str
    is_active: bool
    qr_code_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('asset_type', mode='before')
    @classmethod
    def convert_enum_to_str(cls, v):
        """Convert enum values to strings"""
        if hasattr(v, 'value'):
            return v.value
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True


# ========== Booking Schemas ==========

class BookingBase(BaseModel):
    """Base booking schema"""
    asset_id: str = Field(..., description="ID of the asset to book")
    booking_date: date = Field(..., description="Date of booking")
    start_time: time = Field(..., description="Start time")
    end_time: time = Field(..., description="End time")
    purpose: Optional[str] = Field(None, max_length=500, description="Purpose of booking")
    number_of_guests: Optional[int] = Field(default=1, ge=1, description="Number of guests")


class BookingCreate(BookingBase):
    """Schema for creating a booking"""
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    booking_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    purpose: Optional[str] = Field(None, max_length=500)
    number_of_guests: Optional[int] = Field(None, ge=1)
    status: Optional[BookingStatusType] = None


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: str
    asset_id: str
    asset: Optional[AssetResponse] = None
    user_id: str
    user: Optional[UserSummary] = None
    booking_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    purpose: Optional[str] = None
    number_of_guests: int
    status: BookingStatusType
    payment_amount: Decimal
    payment_status: PaymentStatusType
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('status', 'payment_status', mode='before')
    @classmethod
    def convert_enum_to_str(cls, v):
        """Convert enum values to strings"""
        if hasattr(v, 'value'):
            return v.value
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True


# ========== Check-in/Check-out Schemas ==========

class CheckInRequest(BaseModel):
    """Schema for check-in request"""
    pass  # No additional fields needed, booking_id in path


class CheckOutRequest(BaseModel):
    """Schema for check-out request"""
    pass  # No additional fields needed, booking_id in path


class CheckInResponse(BaseModel):
    """Schema for check-in response"""
    booking_id: str
    checked_in_at: datetime
    message: str = "Successfully checked in"


class CheckOutResponse(BaseModel):
    """Schema for check-out response"""
    booking_id: str
    checked_out_at: datetime
    message: str = "Successfully checked out"


# ========== Availability Schemas ==========

class AvailabilityCheck(BaseModel):
    """Schema for checking availability"""
    booking_date: date
    start_time: time
    end_time: time


class TimeSlot(BaseModel):
    """Represents an available time slot"""
    start_time: time
    end_time: time
    is_available: bool


class AvailabilityResponse(BaseModel):
    """Schema for availability response"""
    asset_id: str
    asset_name: str
    booking_date: date
    is_available: bool
    remaining_capacity: Optional[int] = None  # None means no capacity limit set
    available_slots: list[TimeSlot] = []
    conflicting_bookings: list[str] = []  # List of booking IDs that conflict


# ========== Statistics Schemas ==========

class AssetStatsResponse(BaseModel):
    """Schema for asset usage statistics"""
    asset_id: str
    asset_name: str
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    total_revenue: Decimal
    average_booking_duration: float  # in minutes
    occupancy_rate: float  # percentage
    popular_time_slots: list[dict] = []  # [{time: "10:00-12:00", count: 5}, ...]


# ========== QR Code Schemas ==========

class QRCodeResponse(BaseModel):
    """Schema for QR code response"""
    asset_id: str
    asset_name: str
    qr_code_data: str
    qr_code_image_url: Optional[str] = None  # Base64 or URL


class QRCodeScanRequest(BaseModel):
    """Schema for QR code scan request"""
    qr_code_data: str


class QRCodeScanResponse(BaseModel):
    """Schema for QR code scan response"""
    asset: AssetResponse
    message: str = "Asset found"
