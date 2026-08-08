"""
Asset & Facility Management Models
SQLAlchemy ORM models for assets, bookings, and maintenance
"""

from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey, Integer, Numeric, Boolean, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class AssetType(str, enum.Enum):
    """Asset type enumeration"""
    GYM = "gym"
    POOL = "pool"
    CLUBHOUSE = "clubhouse"
    PARTY_HALL = "party_hall"
    SPORTS_COURT = "sports_court"
    MEETING_ROOM = "meeting_room"
    PARKING = "parking"
    OTHER = "other"


class BookingStatus(str, enum.Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"


class MaintenanceType(str, enum.Enum):
    """Maintenance type enumeration"""
    ROUTINE = "routine"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CLEANING = "cleaning"


class MaintenanceStatus(str, enum.Enum):
    """Maintenance status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Asset(Base):
    """Asset/Facility model - represents bookable facilities in the society"""
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Information
    name = Column(String, nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    description = Column(Text)
    location = Column(String)  # Building/Floor
    capacity = Column(Integer)  # Maximum occupancy
    
    # Booking Configuration
    is_bookable = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    hourly_rate = Column(Numeric(10, 2), default=0)
    advance_booking_days = Column(Integer, default=30)  # How far in advance can book
    min_booking_duration = Column(Integer, default=60)  # Minutes
    max_booking_duration = Column(Integer, default=240)  # Minutes
    max_guests_per_booking = Column(Integer, nullable=True)  # None = no per-booking limit
    
    # Operating Hours
    operating_hours_start = Column(Time)
    operating_hours_end = Column(Time)
    
    # QR Code for Access
    qr_code_data = Column(String, unique=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    bookings = relationship("AssetBooking", back_populates="asset", cascade="all, delete-orphan")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset", cascade="all, delete-orphan")


class AssetBooking(Base):
    """Asset booking model - tracks facility bookings"""
    __tablename__ = "asset_bookings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # References
    asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Booking Details
    booking_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    purpose = Column(Text)
    number_of_guests = Column(Integer, default=1)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    
    # Payment
    payment_amount = Column(Numeric(10, 2), default=0)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Check-in/Check-out
    checked_in_at = Column(DateTime)
    checked_out_at = Column(DateTime)
    
    # Cancellation
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="bookings")
    user = relationship("User", backref="asset_bookings")


class AssetMaintenance(Base):
    """Asset maintenance model - tracks maintenance schedules"""
    __tablename__ = "asset_maintenance"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # References
    asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    
    # Maintenance Details
    scheduled_date = Column(Date, nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    description = Column(Text)
    performed_by = Column(String)
    
    # Status
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, nullable=False)
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
