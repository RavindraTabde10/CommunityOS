"""
Asset & Facility Management Service
Business logic for assets, bookings, availability, and QR codes
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import qrcode
import io
import base64
import uuid

from app.models.asset import (
    Asset,
    AssetBooking,
    AssetType,
    BookingStatus,
    PaymentStatus,
)
from app.models.user import User
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    BookingCreate,
    BookingUpdate,
    TimeSlot,
)


class AssetService:
    """Service for managing assets and facilities"""
    
    @staticmethod
    def create_asset(db: Session, asset_data: AssetCreate) -> Asset:
        """Create a new asset"""
        # Generate unique QR code data
        qr_data = f"asset-{uuid.uuid4().hex[:12]}"
        
        asset = Asset(
            **asset_data.model_dump(),
            qr_code_data=qr_data
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset
    
    @staticmethod
    def get_asset(db: Session, asset_id: str) -> Optional[Asset]:
        """Get asset by ID"""
        return db.query(Asset).filter(Asset.id == asset_id).first()
    
    @staticmethod
    def list_assets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        asset_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_bookable: Optional[bool] = None,
    ) -> Tuple[List[Asset], int]:
        """List assets with filters and pagination"""
        query = db.query(Asset)
        
        # Apply filters
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        if is_active is not None:
            query = query.filter(Asset.is_active == is_active)
        if is_bookable is not None:
            query = query.filter(Asset.is_bookable == is_bookable)
        
        total = query.count()
        assets = query.offset(skip).limit(limit).all()
        return assets, total
    
    @staticmethod
    def update_asset(db: Session, asset_id: str, asset_data: AssetUpdate) -> Optional[Asset]:
        """Update asset details"""
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        # Update only provided fields
        update_data = asset_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(asset, key, value)
        
        db.commit()
        db.refresh(asset)
        return asset
    
    @staticmethod
    def delete_asset(db: Session, asset_id: str) -> bool:
        """Soft delete asset (set is_active to False)"""
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return False
        
        asset.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def generate_qr_code(asset: Asset) -> str:
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(asset.qr_code_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def find_asset_by_qr(db: Session, qr_code_data: str) -> Optional[Asset]:
        """Find asset by QR code data"""
        return db.query(Asset).filter(Asset.qr_code_data == qr_code_data).first()


class BookingService:
    """Service for managing asset bookings"""
    
    @staticmethod
    def calculate_duration(start_time: time, end_time: time) -> int:
        """Calculate duration in minutes between two times"""
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        
        # Handle overnight bookings
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        duration = (end_dt - start_dt).seconds // 60
        return duration
    
    @staticmethod
    def calculate_cost(asset: Asset, duration_minutes: int) -> Decimal:
        """Calculate booking cost based on asset hourly rate"""
        duration_hours = Decimal(duration_minutes) / Decimal(60)
        cost = asset.hourly_rate * duration_hours
        return cost.quantize(Decimal('0.01'))
    
    @staticmethod
    def validate_booking_time(
        db: Session,
        asset: Asset,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[str] = None,
        number_of_guests: int = 1,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate booking time against various rules
        Returns: (is_valid, error_message)
        """
        # Check if asset is bookable
        if not asset.is_bookable:
            return False, "This asset is not available for booking"
        
        # Check if asset is active
        if not asset.is_active:
            return False, "This asset is currently inactive"
        
        # Check if booking is in the past
        now = datetime.now()
        booking_datetime = datetime.combine(booking_date, start_time)
        if booking_datetime < now:
            return False, "Cannot book in the past"
        
        # Check advance booking limit
        days_ahead = (booking_date - date.today()).days
        if days_ahead > asset.advance_booking_days:
            return False, f"Cannot book more than {asset.advance_booking_days} days in advance"
        
        # Check operating hours
        if asset.operating_hours_start and asset.operating_hours_end:
            if start_time < asset.operating_hours_start or end_time > asset.operating_hours_end:
                return False, f"Booking must be within operating hours ({asset.operating_hours_start.strftime('%H:%M')} - {asset.operating_hours_end.strftime('%H:%M')})"
        
        # Check duration limits
        duration = BookingService.calculate_duration(start_time, end_time)
        if duration < asset.min_booking_duration:
            return False, f"Booking duration must be at least {asset.min_booking_duration} minutes"
        if duration > asset.max_booking_duration:
            return False, f"Booking duration cannot exceed {asset.max_booking_duration} minutes"
        
        # Fetch all overlapping bookings for this asset and date
        overlap_query = db.query(AssetBooking).filter(
            and_(
                AssetBooking.asset_id == asset.id,
                AssetBooking.booking_date == booking_date,
                AssetBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    and_(AssetBooking.start_time <= start_time, AssetBooking.end_time > start_time),
                    and_(AssetBooking.start_time < end_time, AssetBooking.end_time >= end_time),
                    and_(AssetBooking.start_time >= start_time, AssetBooking.end_time <= end_time),
                )
            )
        )
        if exclude_booking_id:
            overlap_query = overlap_query.filter(AssetBooking.id != exclude_booking_id)
        overlapping = overlap_query.all()

        if asset.capacity:
            # Multi-booking allowed up to capacity
            already_booked = sum(b.number_of_guests for b in overlapping)
            remaining = asset.capacity - already_booked
            if remaining <= 0:
                return False, "This time slot is at full capacity. Please try another slot."
            if number_of_guests > remaining:
                return False, (
                    f"Only {remaining} spot(s) remaining for this time slot. "
                    f"Please reduce the number of guests or try another slot."
                )
        else:
            # No capacity defined: treat slot as exclusive (one booking at a time)
            if overlapping:
                return False, "This time slot conflicts with an existing booking. Please choose a different time."
        
        return True, None
    
    @staticmethod
    def check_booking_conflicts(
        db: Session,
        asset_id: str,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Check if there are any conflicting bookings
        Returns: (has_conflict, list_of_conflicting_booking_ids)
        """
        query = db.query(AssetBooking).filter(
            and_(
                AssetBooking.asset_id == asset_id,
                AssetBooking.booking_date == booking_date,
                AssetBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    # New booking starts during existing booking
                    and_(
                        AssetBooking.start_time <= start_time,
                        AssetBooking.end_time > start_time
                    ),
                    # New booking ends during existing booking
                    and_(
                        AssetBooking.start_time < end_time,
                        AssetBooking.end_time >= end_time
                    ),
                    # New booking completely contains existing booking
                    and_(
                        AssetBooking.start_time >= start_time,
                        AssetBooking.end_time <= end_time
                    )
                )
            )
        )
        
        # Exclude current booking if updating
        if exclude_booking_id:
            query = query.filter(AssetBooking.id != exclude_booking_id)
        
        conflicting_bookings = query.all()
        has_conflict = len(conflicting_bookings) > 0
        conflicting_ids = [b.id for b in conflicting_bookings]
        
        return has_conflict, conflicting_ids
    
    @staticmethod
    def create_booking(
        db: Session,
        user: User,
        booking_data: BookingCreate,
    ) -> Tuple[Optional[AssetBooking], Optional[str]]:
        """
        Create a new booking
        Returns: (booking, error_message)
        """
        # Get asset
        asset = db.query(Asset).filter(Asset.id == booking_data.asset_id).first()
        if not asset:
            return None, "Asset not found"
        
        # Validate booking time (includes capacity check)
        is_valid, error_msg = BookingService.validate_booking_time(
            db, asset, booking_data.booking_date,
            booking_data.start_time, booking_data.end_time,
            number_of_guests=booking_data.number_of_guests,
        )
        if not is_valid:
            return None, error_msg
        
        # Check per-booking guest limit against asset capacity (single booking vs capacity)
        if asset.capacity and booking_data.number_of_guests > asset.capacity:
            return None, f"Number of guests ({booking_data.number_of_guests}) exceeds asset capacity ({asset.capacity})"

        # Enforce per-booking guest limit set by admin
        if asset.max_guests_per_booking and booking_data.number_of_guests > asset.max_guests_per_booking:
            return None, (
                f"You can bring a maximum of {asset.max_guests_per_booking} guest(s) per booking for this facility."
            )
        
        # Calculate duration and cost
        duration = BookingService.calculate_duration(
            booking_data.start_time, booking_data.end_time
        )
        cost = BookingService.calculate_cost(asset, duration)
        
        # Create booking
        booking = AssetBooking(
            asset_id=booking_data.asset_id,
            user_id=user.id,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            duration_minutes=duration,
            purpose=booking_data.purpose,
            number_of_guests=booking_data.number_of_guests,
            payment_amount=cost,
            status=BookingStatus.CONFIRMED,  # Auto-confirm for now
            payment_status=PaymentStatus.PENDING,
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking, None
    
    @staticmethod
    def get_booking(db: Session, booking_id: str) -> Optional[AssetBooking]:
        """Get booking by ID"""
        return db.query(AssetBooking).filter(AssetBooking.id == booking_id).first()
    
    @staticmethod
    def list_user_bookings(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> Tuple[List[AssetBooking], int]:
        """List bookings for a specific user"""
        query = db.query(AssetBooking).filter(AssetBooking.user_id == user_id)
        
        if status:
            query = query.filter(AssetBooking.status == status)
        
        total = query.count()
        bookings = query.order_by(AssetBooking.booking_date.desc(), AssetBooking.start_time.desc()) \
                        .offset(skip).limit(limit).all()
        return bookings, total
    
    @staticmethod
    def list_asset_bookings(
        db: Session,
        asset_id: str,
        skip: int = 0,
        limit: int = 100,
        booking_date: Optional[date] = None,
    ) -> Tuple[List[AssetBooking], int]:
        """List bookings for a specific asset"""
        query = db.query(AssetBooking).filter(AssetBooking.asset_id == asset_id)
        
        if booking_date:
            query = query.filter(AssetBooking.booking_date == booking_date)
        
        total = query.count()
        bookings = query.order_by(AssetBooking.booking_date.desc(), AssetBooking.start_time) \
                        .offset(skip).limit(limit).all()
        return bookings, total
    
    @staticmethod
    def update_booking(
        db: Session,
        booking_id: str,
        booking_data: BookingUpdate,
    ) -> Tuple[Optional[AssetBooking], Optional[str]]:
        """Update booking details"""
        booking = db.query(AssetBooking).filter(AssetBooking.id == booking_id).first()
        if not booking:
            return None, "Booking not found"
        
        # Can't update cancelled or completed bookings
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            return None, f"Cannot update {booking.status.value} booking"
        
        # Get asset
        asset = db.query(Asset).filter(Asset.id == booking.asset_id).first()
        
        # Check if time is being updated
        new_date = booking_data.booking_date or booking.booking_date
        new_start = booking_data.start_time or booking.start_time
        new_end = booking_data.end_time or booking.end_time
        
        time_changed = (
            new_date != booking.booking_date or
            new_start != booking.start_time or
            new_end != booking.end_time
        )
        
        if time_changed:
            # Validate new time (pass current number_of_guests)
            is_valid, error_msg = BookingService.validate_booking_time(
                db, asset, new_date, new_start, new_end,
                exclude_booking_id=booking_id,
                number_of_guests=booking_data.number_of_guests or booking.number_of_guests,
            )
            if not is_valid:
                return None, error_msg
            
            # Recalculate duration and cost
            duration = BookingService.calculate_duration(new_start, new_end)
            cost = BookingService.calculate_cost(asset, duration)
            booking.duration_minutes = duration
            booking.payment_amount = cost
        
        # Update fields
        update_data = booking_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(booking, key, value)
        
        db.commit()
        db.refresh(booking)
        return booking, None
    
    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: str,
        cancellation_reason: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Cancel a booking"""
        booking = db.query(AssetBooking).filter(AssetBooking.id == booking_id).first()
        if not booking:
            return False, "Booking not found"
        
        if booking.status == BookingStatus.CANCELLED:
            return False, "Booking already cancelled"
        
        if booking.status == BookingStatus.COMPLETED:
            return False, "Cannot cancel completed booking"
        
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        booking.cancellation_reason = cancellation_reason
        booking.payment_status = PaymentStatus.REFUNDED
        
        db.commit()
        return True, None
    
    @staticmethod
    def check_in(db: Session, booking_id: str) -> Tuple[Optional[AssetBooking], Optional[str]]:
        """Check-in to a booking"""
        booking = db.query(AssetBooking).filter(AssetBooking.id == booking_id).first()
        if not booking:
            return None, "Booking not found"
        
        if booking.status != BookingStatus.CONFIRMED:
            return None, f"Cannot check-in to {booking.status.value} booking"
        
        if booking.checked_in_at:
            return None, "Already checked in"
        
        # Check if it's the right date and time
        now = datetime.now()
        booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
        
        # Allow check-in 15 minutes before and anytime after start time
        if now < booking_datetime - timedelta(minutes=15):
            return None, "Too early to check in"
        
        booking.checked_in_at = now
        booking.status = BookingStatus.CONFIRMED
        db.commit()
        db.refresh(booking)
        return booking, None
    
    @staticmethod
    def check_out(db: Session, booking_id: str) -> Tuple[Optional[AssetBooking], Optional[str]]:
        """Check-out from a booking"""
        booking = db.query(AssetBooking).filter(AssetBooking.id == booking_id).first()
        if not booking:
            return None, "Booking not found"
        
        if not booking.checked_in_at:
            return None, "Must check-in before check-out"
        
        if booking.checked_out_at:
            return None, "Already checked out"
        
        booking.checked_out_at = datetime.now()
        booking.status = BookingStatus.COMPLETED
        db.commit()
        db.refresh(booking)
        return booking, None
    
    @staticmethod
    def get_available_slots(
        db: Session,
        asset_id: str,
        booking_date: date,
    ) -> List[TimeSlot]:
        """Get available time slots for an asset on a specific date.
        
        For capacity-based assets a slot stays available until all spots are taken.
        """
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return []
        
        if not asset.operating_hours_start or not asset.operating_hours_end:
            return []
        
        # Get all active bookings for this date
        bookings = db.query(AssetBooking).filter(
            and_(
                AssetBooking.asset_id == asset_id,
                AssetBooking.booking_date == booking_date,
                AssetBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        ).order_by(AssetBooking.start_time).all()

        # Build 15-minute slots across operating hours
        slots = []
        slot_minutes = 15
        op_start = asset.operating_hours_start
        op_end   = asset.operating_hours_end

        current = op_start
        while current < op_end:
            # Calculate slot end
            next_dt = datetime.combine(date.today(), current) + timedelta(minutes=slot_minutes)
            slot_end = next_dt.time()
            if slot_end > op_end:
                slot_end = op_end

            # Count guests already booked in this 15-min window
            overlapping_guests = sum(
                b.number_of_guests for b in bookings
                if b.start_time <= current and b.end_time > current
            )

            if asset.capacity:
                is_available = overlapping_guests < asset.capacity
            else:
                is_available = overlapping_guests == 0

            slots.append(TimeSlot(
                start_time=current,
                end_time=slot_end,
                is_available=is_available,
            ))
            current = slot_end

        return slots
