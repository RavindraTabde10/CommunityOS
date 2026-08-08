"""
Reports & Analytics Endpoints
Handles report generation and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.schemas.report import (
    DashboardStats, IssueAnalytics, ContractorPerformance, AssetUsageReport,
    ExportRequest, ExportResponse
)
from app.models.user import User, UserRole
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.services.report_service import ReportService


router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics(
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Returns comprehensive metrics including:
    - Issue counts (total, open, resolved, etc.)
    - Average resolution time
    - User statistics (for admins)
    - Asset and booking statistics (for admins/facility)
    - Recent activity count
    
    **Permissions:**
    - All authenticated users can access
    - Residents see limited data (only their issues)
    - Admins/Facility see full statistics
    
    **Query Parameters:**
    - from_date: Optional start date filter
    - to_date: Optional end date filter
    """
    try:
        # Validate date range
        if from_date and to_date and from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date must be before or equal to to_date"
            )
        
        stats = ReportService.get_dashboard_stats(db, current_user, from_date, to_date)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard statistics: {str(e)}"
        )


@router.get("/issues", response_model=IssueAnalytics)
async def get_issue_analytics(
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get issue analytics and trends
    
    Returns detailed issue analytics including:
    - Distribution by category, priority, and status
    - Average resolution time by category
    - Resolution rate percentage
    - Daily trend data
    
    **Permissions:**
    - All authenticated users can access
    - Residents see only their issue analytics
    - Admins see all issue analytics
    
    **Query Parameters:**
    - category: Filter by issue category (electrical, plumbing, etc.)
    - priority: Filter by priority (low, medium, high, critical)
    - status: Filter by status (open, in_progress, resolved, closed)
    - from_date: Start date filter
    - to_date: End date filter
    """
    try:
        # Validate date range
        if from_date and to_date and from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date must be before or equal to to_date"
            )
        
        analytics = ReportService.get_issue_analytics(
            db, current_user, category, priority, status, from_date, to_date
        )
        return analytics
        
    except ValueError as e:
        # Handle invalid enum values
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating issue analytics: {str(e)}"
        )


@router.get("/contractors", response_model=List[ContractorPerformance])
async def get_contractor_performance(
    contractor_id: Optional[str] = Query(None, description="Filter by contractor ID"),
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get contractor performance reports
    
    Returns contractor performance metrics including:
    - Total jobs completed and completion rate
    - Average rating and total ratings
    - Response time statistics
    - Recent ratings (last 5)
    - Verification and availability status
    
    **Permissions:**
    - Admin only
    
    **Query Parameters:**
    - contractor_id: Filter by specific contractor
    - from_date: Start date filter for ratings
    - to_date: End date filter for ratings
    """
    # Check admin permission
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access contractor performance reports"
        )
    
    try:
        # Validate date range
        if from_date and to_date and from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date must be before or equal to to_date"
            )
        
        reports = ReportService.get_contractor_performance(
            db, current_user, contractor_id, from_date, to_date
        )
        return reports
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating contractor performance report: {str(e)}"
        )


@router.get("/assets", response_model=List[AssetUsageReport])
async def get_asset_usage_report(
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get asset usage reports
    
    Returns asset usage analytics including:
    - Total bookings and revenue
    - Booking status distribution (confirmed, cancelled, completed)
    - Utilization rate percentage
    - Average booking duration
    - Popular time slots
    - Daily booking trends
    
    **Permissions:**
    - Admin and Facility managers only
    
    **Query Parameters:**
    - asset_id: Filter by specific asset
    - asset_type: Filter by asset type (gym, pool, clubhouse, etc.)
    - from_date: Start date filter
    - to_date: End date filter
    """
    # Check permission
    if current_user.role not in [UserRole.ADMIN, UserRole.FACILITY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and facility managers can access asset usage reports"
        )
    
    try:
        # Validate date range
        if from_date and to_date and from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date must be before or equal to to_date"
            )
        
        reports = ReportService.get_asset_usage_report(
            db, current_user, asset_id, asset_type, from_date, to_date
        )
        return reports
        
    except ValueError as e:
        # Handle invalid enum values
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating asset usage report: {str(e)}"
        )


@router.post("/export", response_model=ExportResponse)
async def export_report(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export report data in CSV or JSON format
    
    Exports report data based on report type and filters.
    
    **Supported Report Types:**
    - `dashboard` - Dashboard statistics
    - `issues` - Issue analytics
    - `contractors` - Contractor performance (admin only)
    - `assets` - Asset usage reports (admin/facility only)
    
    **Export Formats:**
    - `csv` - Comma-separated values
    - `json` - JSON format (pretty-printed)
    
    **Permissions:**
    - Admin only
    
    **Request Body:**
    ```json
    {
      "report_type": "issues",
      "format": "csv",
      "filters": {
        "category": "electrical",
        "from_date": "2026-01-01",
        "to_date": "2026-07-25"
      }
    }
    ```
    
    **Response:**
    Returns the exported data as a string (CSV or JSON), along with metadata.
    """
    # Check admin permission
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can export reports"
        )
    
    # Validate report type
    valid_report_types = ["dashboard", "issues", "contractors", "assets"]
    if request.report_type not in valid_report_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report_type. Must be one of: {', '.join(valid_report_types)}"
        )
    
    try:
        # Convert date strings to date objects if present
        filters = request.filters or {}
        if "from_date" in filters and isinstance(filters["from_date"], str):
            filters["from_date"] = date.fromisoformat(filters["from_date"])
        if "to_date" in filters and isinstance(filters["to_date"], str):
            filters["to_date"] = date.fromisoformat(filters["to_date"])
        
        result = ReportService.export_report(
            db, current_user, request.report_type, filters, request.format
        )
        
        return ExportResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid filter values: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )
