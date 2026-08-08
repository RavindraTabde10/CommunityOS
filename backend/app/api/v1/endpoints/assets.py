"""
Asset Management Endpoints
Handles asset CRUD operations and QR code generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetStatsResponse,
    QRCodeResponse,
    QRCodeScanRequest,
    QRCodeScanResponse,
)
from app.models.user import User, UserRole
from app.models.asset import AssetBooking, BookingStatus
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.services.asset_service import AssetService


router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and facility managers can perform this action"
        )
    return current_user


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new asset/facility (Admin only)
    
    Required fields:
    - name: Asset name
    - asset_type: One of gym, pool, clubhouse, party_hall, sports_court, meeting_room, parking, other
    
    Optional fields:
    - description, location, capacity, hourly_rate
    - Operating hours, booking duration limits, advance booking days
    """
    try:
        new_asset = AssetService.create_asset(db, asset)
        return new_asset
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating asset: {str(e)}"
        )


@router.get("/", response_model=List[AssetResponse])
async def list_assets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    asset_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_bookable: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all assets with optional filters
    
    Filters:
    - asset_type: Filter by asset type
    - is_active: Filter by active status
    - is_bookable: Filter by bookable status
    """
    assets, total = AssetService.list_assets(
        db, skip, limit, asset_type, is_active, is_bookable
    )
    return assets


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get asset details by ID"""
    asset = AssetService.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    asset_data: AssetUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update asset details (Admin only)"""
    updated_asset = AssetService.update_asset(db, asset_id, asset_data)
    if not updated_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return updated_asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate asset (soft delete) (Admin only)
    
    This sets is_active to False instead of deleting the record
    """
    success = AssetService.delete_asset(db, asset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return


@router.get("/{asset_id}/qrcode", response_model=QRCodeResponse)
async def generate_qr_code(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate QR code for asset
    
    Returns base64 encoded QR code image
    """
    asset = AssetService.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    try:
        qr_image = AssetService.generate_qr_code(asset)
        return QRCodeResponse(
            asset_id=asset.id,
            asset_name=asset.name,
            qr_code_data=asset.qr_code_data,
            qr_code_image_url=qr_image
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating QR code: {str(e)}"
        )


@router.post("/scan", response_model=QRCodeScanResponse)
async def scan_qr_code(
    scan_data: QRCodeScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scan QR code and get asset details
    
    Used for mobile app check-in/check-out
    """
    asset = AssetService.find_asset_by_qr(db, scan_data.qr_code_data)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR code"
        )
    
    return QRCodeScanResponse(
        asset=asset,
        message=f"Found asset: {asset.name}"
    )


@router.get("/{asset_id}/stats", response_model=AssetStatsResponse)
async def get_asset_stats(
    asset_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for an asset (Admin only)
    
    Returns:
    - Total bookings
    - Completed bookings
    - Cancelled bookings
    - Total revenue
    - Average booking duration
    - Occupancy rate
    """
    asset = AssetService.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Get all bookings for this asset
    all_bookings = db.query(AssetBooking).filter(AssetBooking.asset_id == asset_id).all()
    
    total_bookings = len(all_bookings)
    completed_bookings = len([b for b in all_bookings if b.status == BookingStatus.COMPLETED])
    cancelled_bookings = len([b for b in all_bookings if b.status == BookingStatus.CANCELLED])
    
    # Calculate revenue (only from completed bookings)
    total_revenue = sum([b.payment_amount for b in all_bookings if b.status == BookingStatus.COMPLETED])
    
    # Average duration
    if all_bookings:
        avg_duration = sum([b.duration_minutes for b in all_bookings]) / len(all_bookings)
    else:
        avg_duration = 0
    
    # Occupancy rate (simplified - could be more sophisticated)
    occupancy_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
    
    return AssetStatsResponse(
        asset_id=asset.id,
        asset_name=asset.name,
        total_bookings=total_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        total_revenue=total_revenue,
        average_booking_duration=avg_duration,
        occupancy_rate=occupancy_rate,
        popular_time_slots=[]  # TODO: Implement time slot analysis
    )
