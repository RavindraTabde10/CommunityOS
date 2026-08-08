"""
Booking Management Endpoints
Handles facility bookings, check-in/check-out, and availability
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date

from app.schemas.asset import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    CheckInResponse,
    CheckOutResponse,
    AvailabilityCheck,
    AvailabilityResponse,
    TimeSlot,
)
from app.models.user import User, UserRole
from app.models.asset import AssetBooking
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.services.asset_service import AssetService, BookingService


router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new booking
    
    Required fields:
    - asset_id: ID of the asset to book
    - booking_date: Date of booking
    - start_time: Start time
    - end_time: End time
    
    Validations:
    - Asset must be active and bookable
    - Time slot must not conflict with existing bookings
    - Must be within operating hours
    - Must respect duration limits
    - Cannot book more than advance_booking_days ahead
    """
    new_booking, error = BookingService.create_booking(db, current_user, booking)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Load relationships
    db.refresh(new_booking)
    db_booking = db.query(AssetBooking).options(
        joinedload(AssetBooking.asset),
        joinedload(AssetBooking.user)
    ).filter(AssetBooking.id == new_booking.id).first()
    
    return db_booking


@router.get("/", response_model=List[BookingResponse])
async def list_my_bookings(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List current user's bookings
    
    Filters:
    - status: Filter by booking status (pending, confirmed, cancelled, completed, no_show)
    """
    bookings, total = BookingService.list_user_bookings(
        db, current_user.id, skip, limit, status
    )
    
    # Load relationships
    booking_ids = [b.id for b in bookings]
    bookings_with_relations = db.query(AssetBooking).options(
        joinedload(AssetBooking.asset),
        joinedload(AssetBooking.user)
    ).filter(AssetBooking.id.in_(booking_ids)).all()
    
    return bookings_with_relations


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking details by ID"""
    booking = db.query(AssetBooking).options(
        joinedload(AssetBooking.asset),
        joinedload(AssetBooking.user)
    ).filter(AssetBooking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if booking.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this booking"
        )
    
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update booking details
    
    - Users can only update their own bookings
    - Admins can update any booking
    - Cannot update cancelled or completed bookings
    """
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if booking.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this booking"
        )
    
    updated_booking, error = BookingService.update_booking(db, booking_id, booking_data)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Load relationships
    db_booking = db.query(AssetBooking).options(
        joinedload(AssetBooking.asset),
        joinedload(AssetBooking.user)
    ).filter(AssetBooking.id == booking_id).first()
    
    return db_booking


@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
async def cancel_booking(
    booking_id: str,
    cancellation_reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a booking
    
    - Users can cancel their own bookings
    - Admins can cancel any booking
    """
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if booking.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this booking"
        )
    
    success, error = BookingService.cancel_booking(db, booking_id, cancellation_reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {"message": "Booking cancelled successfully"}


@router.post("/{booking_id}/checkin", response_model=CheckInResponse)
async def check_in(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check-in to a booking
    
    - Can check-in 15 minutes before start time
    - Must be the booking owner
    """
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if booking.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to check-in to this booking"
        )
    
    updated_booking, error = BookingService.check_in(db, booking_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return CheckInResponse(
        booking_id=updated_booking.id,
        checked_in_at=updated_booking.checked_in_at
    )


@router.post("/{booking_id}/checkout", response_model=CheckOutResponse)
async def check_out(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check-out from a booking
    
    - Must have checked in first
    - Must be the booking owner
    """
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check permissions
    if booking.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to check-out from this booking"
        )
    
    updated_booking, error = BookingService.check_out(db, booking_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return CheckOutResponse(
        booking_id=updated_booking.id,
        checked_out_at=updated_booking.checked_out_at
    )


@router.get("/assets/{asset_id}/availability", response_model=AvailabilityResponse)
async def check_availability(
    asset_id: str,
    booking_date: date = Query(..., description="Date to check availability"),
    start_time: Optional[str] = Query(None, description="Start time (HH:MM)"),
    end_time: Optional[str] = Query(None, description="End time (HH:MM)"),
    number_of_guests: int = Query(default=1, ge=1, description="Number of guests to check capacity for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check availability for an asset

    - If start_time and end_time provided: Check specific time slot
    - If not provided: Show all available slots for the day
    - Returns remaining_capacity when asset has a capacity limit
    """
    asset = AssetService.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    # Get 15-min slot grid for the day
    available_slots = BookingService.get_available_slots(db, asset_id, booking_date)

    is_available = True
    remaining_capacity = None

    if start_time and end_time:
        from datetime import time as dt_time
        start_t = dt_time.fromisoformat(start_time)
        end_t   = dt_time.fromisoformat(end_time)

        is_valid, _ = BookingService.validate_booking_time(
            db, asset, booking_date, start_t, end_t,
            number_of_guests=number_of_guests,
        )
        is_available = is_valid

        # Compute remaining capacity for the requested slot
        if asset.capacity:
            from sqlalchemy import and_, or_
            from app.models.asset import AssetBooking as _AB, BookingStatus as _BS
            overlapping_guests = (
                db.query(_AB)
                .filter(
                    and_(
                        _AB.asset_id == asset_id,
                        _AB.booking_date == booking_date,
                        _AB.status.in_([_BS.PENDING, _BS.CONFIRMED]),
                        or_(
                            and_(_AB.start_time <= start_t, _AB.end_time > start_t),
                            and_(_AB.start_time < end_t, _AB.end_time >= end_t),
                            and_(_AB.start_time >= start_t, _AB.end_time <= end_t),
                        ),
                    )
                )
                .with_entities(_AB.number_of_guests)
                .all()
            )
            booked = sum(g[0] for g in overlapping_guests)
            remaining_capacity = max(0, asset.capacity - booked)

    return AvailabilityResponse(
        asset_id=asset.id,
        asset_name=asset.name,
        booking_date=booking_date,
        is_available=is_available,
        remaining_capacity=remaining_capacity,
        available_slots=available_slots,
    )


@router.get("/assets/{asset_id}/bookings", response_model=List[BookingResponse])
async def list_asset_bookings(
    asset_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    booking_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all bookings for an asset
    
    - Users can see their own bookings
    - Admins can see all bookings
    
    Filters:
    - booking_date: Filter by specific date
    """
    # Check if user is admin or facility manager
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.FACILITY]
    
    bookings, total = BookingService.list_asset_bookings(
        db, asset_id, skip, limit, booking_date
    )
    
    # Filter bookings based on permissions
    if not is_admin:
        bookings = [b for b in bookings if b.user_id == current_user.id]
    
    # Load relationships
    booking_ids = [b.id for b in bookings]
    bookings_with_relations = db.query(AssetBooking).options(
        joinedload(AssetBooking.asset),
        joinedload(AssetBooking.user)
    ).filter(AssetBooking.id.in_(booking_ids)).all()
    
    return bookings_with_relations
