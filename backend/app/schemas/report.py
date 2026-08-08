"""
Report Schemas
Pydantic schemas for reports and analytics
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, date
from enum import Enum


class ExportFormat(str, Enum):
    """Export format enumeration"""
    CSV = "csv"
    JSON = "json"


class DateRangeFilter(BaseModel):
    """Date range filter for reports"""
    from_date: Optional[date] = Field(None, description="Start date (inclusive)")
    to_date: Optional[date] = Field(None, description="End date (inclusive)")


class IssueReportFilter(BaseModel):
    """Filters for issue analytics report"""
    category: Optional[str] = Field(None, description="Filter by category")
    priority: Optional[str] = Field(None, description="Filter by priority")
    status: Optional[str] = Field(None, description="Filter by status")
    from_date: Optional[date] = Field(None, description="Start date")
    to_date: Optional[date] = Field(None, description="End date")


class ContractorReportFilter(BaseModel):
    """Filters for contractor performance report"""
    contractor_id: Optional[str] = Field(None, description="Filter by contractor ID")
    from_date: Optional[date] = Field(None, description="Start date")
    to_date: Optional[date] = Field(None, description="End date")


class AssetReportFilter(BaseModel):
    """Filters for asset usage report"""
    asset_id: Optional[str] = Field(None, description="Filter by asset ID")
    asset_type: Optional[str] = Field(None, description="Filter by asset type")
    from_date: Optional[date] = Field(None, description="Start date")
    to_date: Optional[date] = Field(None, description="End date")


class ExportRequest(BaseModel):
    """Request schema for exporting reports"""
    report_type: str = Field(..., description="Type of report: dashboard, issues, contractors, assets")
    format: ExportFormat = Field(ExportFormat.JSON, description="Export format")
    filters: Optional[Dict[str, Any]] = Field(None, description="Report filters")


# Response Schemas

class DashboardStats(BaseModel):
    """Dashboard statistics response"""
    # Issue Statistics
    total_issues: int = Field(..., description="Total number of issues")
    open_issues: int = Field(..., description="Number of open issues")
    in_progress_issues: int = Field(..., description="Number of in-progress issues")
    resolved_issues: int = Field(..., description="Number of resolved issues")
    closed_issues: int = Field(..., description="Number of closed issues")
    avg_resolution_time_hours: Optional[float] = Field(None, description="Average resolution time in hours")
    
    # User Statistics
    total_users: int = Field(..., description="Total registered users")
    users_by_role: Dict[str, int] = Field(default_factory=dict, description="User count by role")
    active_contractors: int = Field(0, description="Number of active contractors")
    
    # Asset Statistics
    total_assets: int = Field(0, description="Total number of assets")
    active_assets: int = Field(0, description="Number of active assets")
    total_bookings: int = Field(0, description="Total bookings")
    pending_bookings: int = Field(0, description="Pending bookings")
    confirmed_bookings: int = Field(0, description="Confirmed bookings")
    total_booking_revenue: float = Field(0.0, description="Total revenue from bookings")
    
    # Activity Statistics
    recent_activity_count: int = Field(0, description="Activity count in last 7 days")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")


class TrendData(BaseModel):
    """Trend data point"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    count: int = Field(..., description="Total count for that date")
    planned: int = Field(0, description="Pending + confirmed bookings")
    completed: int = Field(0, description="Completed bookings")


class IssueAnalytics(BaseModel):
    """Issue analytics response"""
    # Distribution
    issues_by_category: Dict[str, int] = Field(default_factory=dict, description="Issue count by category")
    issues_by_priority: Dict[str, int] = Field(default_factory=dict, description="Issue count by priority")
    issues_by_status: Dict[str, int] = Field(default_factory=dict, description="Issue count by status")
    
    # Performance Metrics
    avg_resolution_time_by_category: Dict[str, float] = Field(
        default_factory=dict, 
        description="Average resolution time in hours by category"
    )
    resolution_rate: float = Field(..., description="Percentage of issues resolved")
    
    # Trends
    trend_data: List[TrendData] = Field(default_factory=list, description="Daily issue creation trend")
    
    # Summary
    total_issues: int = Field(..., description="Total issues in the filter")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range applied")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")


class RecentRating(BaseModel):
    """Recent contractor rating"""
    issue_id: Optional[str] = None
    rating: int
    review_text: Optional[str] = None
    rated_by: str
    rated_at: datetime


class ContractorPerformance(BaseModel):
    """Contractor performance report"""
    contractor_id: str = Field(..., description="Contractor profile ID")
    contractor_name: str = Field(..., description="Contractor name")
    email: str = Field(..., description="Contractor email")
    company_name: Optional[str] = Field(None, description="Company name")
    specializations: List[str] = Field(default_factory=list, description="Specializations")
    
    # Performance Metrics
    total_jobs_completed: int = Field(0, description="Total jobs completed")
    completion_rate: float = Field(0.0, description="Job completion rate percentage")
    average_rating: float = Field(0.0, description="Average rating (0-5)")
    total_ratings: int = Field(0, description="Total number of ratings")
    avg_response_time_hours: Optional[float] = Field(None, description="Average response time in hours")
    
    # Status
    is_available: bool = Field(True, description="Is contractor available")
    is_verified: bool = Field(False, description="Is contractor verified")
    
    # Recent Ratings
    recent_ratings: List[RecentRating] = Field(default_factory=list, description="Last 5 ratings")


class TimeSlot(BaseModel):
    """Popular time slot"""
    hour: int = Field(..., description="Hour of the day (0-23)")
    booking_count: int = Field(..., description="Number of bookings")


class AssetUsageReport(BaseModel):
    """Asset usage report"""
    asset_id: str = Field(..., description="Asset ID")
    asset_name: str = Field(..., description="Asset name")
    asset_type: str = Field(..., description="Asset type")
    
    # Usage Metrics
    total_bookings: int = Field(0, description="Total bookings")
    confirmed_bookings: int = Field(0, description="Confirmed bookings")
    cancelled_bookings: int = Field(0, description="Cancelled bookings")
    completed_bookings: int = Field(0, description="Completed bookings")
    total_revenue: float = Field(0.0, description="Total revenue generated")
    
    # Utilization
    utilization_rate: float = Field(0.0, description="Utilization rate percentage")
    avg_booking_duration_minutes: Optional[float] = Field(None, description="Average booking duration")
    
    # Popular Times
    popular_time_slots: List[TimeSlot] = Field(default_factory=list, description="Most popular booking times")
    
    # Trends
    booking_trend: List[TrendData] = Field(default_factory=list, description="Daily booking trend")
    
    # Date Range
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range applied")


class ExportResponse(BaseModel):
    """Export response"""
    format: str = Field(..., description="Export format used")
    data: Optional[str] = Field(None, description="Exported data (CSV string or JSON)")
    record_count: int = Field(..., description="Number of records exported")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Export timestamp")
    message: str = Field(..., description="Status message")
