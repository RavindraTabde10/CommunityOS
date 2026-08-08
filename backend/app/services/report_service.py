"""
Report Service
Business logic for generating reports and analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, cast, String, extract
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import csv
import io
import json

from app.models.user import User, UserRole
from app.models.issue import Issue, IssueStatus, IssueCategory, IssuePriority
from app.models.contractor import ContractorProfile, ContractorRating, WorkCompletion, AvailabilityStatus
from app.models.asset import Asset, AssetBooking, AssetType, BookingStatus
from app.models.activity import IssueActivity
from app.schemas.report import (
    DashboardStats, IssueAnalytics, ContractorPerformance, AssetUsageReport,
    TrendData, RecentRating, TimeSlot, ExportFormat
)


class ReportService:
    """Service for generating reports and analytics"""
    
    @staticmethod
    def get_dashboard_stats(db: Session, current_user: User, from_date: Optional[date] = None, to_date: Optional[date] = None) -> DashboardStats:
        """
        Get dashboard statistics
        
        Args:
            db: Database session
            current_user: Current authenticated user
            from_date: Optional start date filter
            to_date: Optional end date filter
            
        Returns:
            DashboardStats with comprehensive metrics
        """
        # Build base issue query
        issue_query = db.query(Issue)
        
        # Apply date filter if provided
        if from_date:
            issue_query = issue_query.filter(Issue.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            issue_query = issue_query.filter(Issue.created_at <= datetime.combine(to_date, datetime.max.time()))
        
        # Role-based filtering (residents see only their issues)
        if current_user.role == UserRole.RESIDENT:
            issue_query = issue_query.filter(Issue.reported_by == current_user.id)
        
        # Issue statistics
        total_issues = issue_query.count()
        open_issues = issue_query.filter(Issue.status == IssueStatus.OPEN).count()
        in_progress_issues = issue_query.filter(Issue.status == IssueStatus.IN_PROGRESS).count()
        resolved_issues = issue_query.filter(Issue.status == IssueStatus.RESOLVED).count()
        closed_issues = issue_query.filter(Issue.status == IssueStatus.CLOSED).count()
        
        # Average resolution time (in hours)
        avg_resolution_time = ReportService._calculate_avg_resolution_time(db, current_user, from_date, to_date)
        
        # User statistics (only for admin/facility roles)
        total_users = 0
        users_by_role = {}
        active_contractors = 0
        
        if current_user.role in [UserRole.ADMIN, UserRole.FACILITY, UserRole.BUILDER]:
            total_users = db.query(User).filter(User.is_active == True).count()
            
            # Count users by role
            role_counts = db.query(
                User.role,
                func.count(User.id)
            ).filter(User.is_active == True).group_by(User.role).all()
            
            users_by_role = {role.value: count for role, count in role_counts}
            
            # Active contractors
            active_contractors = db.query(ContractorProfile).filter(
                ContractorProfile.is_active == True,
                ContractorProfile.is_available == True
            ).count()
        
        # Asset and booking statistics (only for admin/facility roles)
        total_assets = 0
        active_assets = 0
        total_bookings = 0
        pending_bookings = 0
        confirmed_bookings = 0
        total_booking_revenue = 0.0
        
        if current_user.role in [UserRole.ADMIN, UserRole.FACILITY]:
            total_assets = db.query(Asset).count()
            active_assets = db.query(Asset).filter(Asset.is_active == True).count()
            
            booking_query = db.query(AssetBooking)
            if from_date:
                booking_query = booking_query.filter(AssetBooking.booking_date >= from_date)
            if to_date:
                booking_query = booking_query.filter(AssetBooking.booking_date <= to_date)
            
            total_bookings = booking_query.count()
            pending_bookings = booking_query.filter(AssetBooking.status == BookingStatus.PENDING).count()
            confirmed_bookings = booking_query.filter(AssetBooking.status == BookingStatus.CONFIRMED).count()
            
            # Calculate total revenue
            revenue_result = booking_query.with_entities(func.sum(AssetBooking.payment_amount)).scalar()
            total_booking_revenue = float(revenue_result) if revenue_result else 0.0
        
        # Recent activity count (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity_count = db.query(IssueActivity).filter(
            IssueActivity.created_at >= seven_days_ago
        ).count()
        
        return DashboardStats(
            total_issues=total_issues,
            open_issues=open_issues,
            in_progress_issues=in_progress_issues,
            resolved_issues=resolved_issues,
            closed_issues=closed_issues,
            avg_resolution_time_hours=avg_resolution_time,
            total_users=total_users,
            users_by_role=users_by_role,
            active_contractors=active_contractors,
            total_assets=total_assets,
            active_assets=active_assets,
            total_bookings=total_bookings,
            pending_bookings=pending_bookings,
            confirmed_bookings=confirmed_bookings,
            total_booking_revenue=total_booking_revenue,
            recent_activity_count=recent_activity_count
        )
    
    @staticmethod
    def get_issue_analytics(
        db: Session,
        current_user: User,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> IssueAnalytics:
        """
        Get issue analytics with distribution and trends
        
        Args:
            db: Database session
            current_user: Current authenticated user
            category: Filter by category
            priority: Filter by priority
            status: Filter by status
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            IssueAnalytics with detailed metrics
        """
        # Build base query
        query = db.query(Issue)
        
        # Role-based filtering
        if current_user.role == UserRole.RESIDENT:
            query = query.filter(Issue.reported_by == current_user.id)
        
        # Apply filters
        if category:
            query = query.filter(Issue.category == IssueCategory(category.lower()))
        if priority:
            query = query.filter(Issue.priority == IssuePriority(priority.lower()))
        if status:
            query = query.filter(Issue.status == IssueStatus(status.lower()))
        if from_date:
            query = query.filter(Issue.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.filter(Issue.created_at <= datetime.combine(to_date, datetime.max.time()))
        
        # Total issues in filter
        total_issues = query.count()
        
        # Issues by category
        category_counts = db.query(
            Issue.category,
            func.count(Issue.id)
        ).filter(
            Issue.id.in_([issue.id for issue in query.all()])
        ).group_by(Issue.category).all()
        issues_by_category = {cat.value: count for cat, count in category_counts}
        
        # Issues by priority
        priority_counts = db.query(
            Issue.priority,
            func.count(Issue.id)
        ).filter(
            Issue.id.in_([issue.id for issue in query.all()]) if total_issues > 0 else True
        ).group_by(Issue.priority).all()
        issues_by_priority = {pri.value: count for pri, count in priority_counts}
        
        # Issues by status
        status_counts = db.query(
            Issue.status,
            func.count(Issue.id)
        ).filter(
            Issue.id.in_([issue.id for issue in query.all()]) if total_issues > 0 else True
        ).group_by(Issue.status).all()
        issues_by_status = {stat.value: count for stat, count in status_counts}
        
        # Average resolution time by category
        avg_resolution_by_category = {}
        for cat in IssueCategory:
            avg_time = ReportService._calculate_avg_resolution_time(
                db, current_user, from_date, to_date, category=cat.value
            )
            if avg_time:
                avg_resolution_by_category[cat.value] = avg_time
        
        # Resolution rate
        resolved_count = query.filter(
            Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED])
        ).count()
        resolution_rate = (resolved_count / total_issues * 100) if total_issues > 0 else 0.0
        
        # Trend data (daily counts)
        trend_data = ReportService._generate_issue_trend(query)
        
        # Date range
        date_range = None
        if from_date or to_date:
            date_range = {
                "from": from_date.isoformat() if from_date else None,
                "to": to_date.isoformat() if to_date else None
            }
        
        return IssueAnalytics(
            issues_by_category=issues_by_category,
            issues_by_priority=issues_by_priority,
            issues_by_status=issues_by_status,
            avg_resolution_time_by_category=avg_resolution_by_category,
            resolution_rate=round(resolution_rate, 2),
            trend_data=trend_data,
            total_issues=total_issues,
            date_range=date_range
        )
    
    @staticmethod
    def get_contractor_performance(
        db: Session,
        current_user: User,
        contractor_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[ContractorPerformance]:
        """
        Get contractor performance reports
        
        Args:
            db: Database session
            current_user: Current authenticated user
            contractor_id: Filter by specific contractor
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of ContractorPerformance reports
        """
        # Build query
        query = db.query(ContractorProfile).join(User, ContractorProfile.user_id == User.id)
        
        if contractor_id:
            query = query.filter(ContractorProfile.id == contractor_id)
        
        contractors = query.all()
        
        results = []
        for contractor in contractors:
            # Get recent ratings
            rating_query = db.query(ContractorRating).filter(
                ContractorRating.contractor_id == contractor.id
            )
            
            if from_date:
                rating_query = rating_query.filter(
                    ContractorRating.created_at >= datetime.combine(from_date, datetime.min.time())
                )
            if to_date:
                rating_query = rating_query.filter(
                    ContractorRating.created_at <= datetime.combine(to_date, datetime.max.time())
                )
            
            recent_ratings = rating_query.order_by(ContractorRating.created_at.desc()).limit(5).all()
            
            recent_ratings_list = [
                RecentRating(
                    issue_id=rating.issue_id,
                    rating=rating.rating,
                    review_text=rating.review_text,
                    rated_by=rating.rated_by,
                    rated_at=rating.created_at
                )
                for rating in recent_ratings
            ]
            
            results.append(ContractorPerformance(
                contractor_id=contractor.id,
                contractor_name=contractor.user.name,
                email=contractor.user.email,
                company_name=contractor.company_name,
                specializations=contractor.specializations or [],
                total_jobs_completed=contractor.total_jobs_completed,
                completion_rate=float(contractor.completion_rate),
                average_rating=float(contractor.average_rating),
                total_ratings=contractor.total_ratings,
                avg_response_time_hours=contractor.response_time_avg,
                is_available=contractor.is_available,
                is_verified=contractor.is_verified,
                recent_ratings=recent_ratings_list
            ))
        
        return results
    
    @staticmethod
    def get_asset_usage_report(
        db: Session,
        current_user: User,
        asset_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[AssetUsageReport]:
        """
        Get asset usage reports
        
        Args:
            db: Database session
            current_user: Current authenticated user
            asset_id: Filter by specific asset
            asset_type: Filter by asset type
            from_date: Start date filter
            to_date: End date filter
            
        Returns:
            List of AssetUsageReport
        """
        # Build asset query
        asset_query = db.query(Asset).filter(Asset.is_active == True)
        
        if asset_id:
            asset_query = asset_query.filter(Asset.id == asset_id)
        if asset_type:
            asset_query = asset_query.filter(Asset.asset_type == AssetType(asset_type.lower()))
        
        assets = asset_query.all()
        
        results = []
        for asset in assets:
            # Build booking query for this asset
            booking_query = db.query(AssetBooking).filter(AssetBooking.asset_id == asset.id)
            
            if from_date:
                booking_query = booking_query.filter(AssetBooking.booking_date >= from_date)
            if to_date:
                booking_query = booking_query.filter(AssetBooking.booking_date <= to_date)
            
            bookings = booking_query.all()
            
            # Calculate metrics
            total_bookings = len(bookings)
            confirmed_bookings = sum(1 for b in bookings if b.status == BookingStatus.CONFIRMED)
            cancelled_bookings = sum(1 for b in bookings if b.status == BookingStatus.CANCELLED)
            completed_bookings = sum(1 for b in bookings if b.status == BookingStatus.COMPLETED)
            
            total_revenue = sum(float(b.payment_amount) for b in bookings if b.payment_amount)
            
            # Average booking duration
            durations = [b.duration_minutes for b in bookings if b.duration_minutes]
            avg_duration = sum(durations) / len(durations) if durations else None
            
            # Calculate utilization rate
            utilization_rate = ReportService._calculate_utilization_rate(asset, bookings, from_date, to_date)
            
            # Popular time slots
            popular_slots = ReportService._get_popular_time_slots(bookings)
            
            # Booking trend
            booking_trend = ReportService._generate_booking_trend(bookings)
            
            # Date range
            date_range = None
            if from_date or to_date:
                date_range = {
                    "from": from_date.isoformat() if from_date else None,
                    "to": to_date.isoformat() if to_date else None
                }
            
            results.append(AssetUsageReport(
                asset_id=asset.id,
                asset_name=asset.name,
                asset_type=asset.asset_type.value,
                total_bookings=total_bookings,
                confirmed_bookings=confirmed_bookings,
                cancelled_bookings=cancelled_bookings,
                completed_bookings=completed_bookings,
                total_revenue=total_revenue,
                utilization_rate=round(utilization_rate, 2),
                avg_booking_duration_minutes=round(avg_duration, 2) if avg_duration else None,
                popular_time_slots=popular_slots,
                booking_trend=booking_trend,
                date_range=date_range
            ))
        
        return results
    
    @staticmethod
    def export_report(
        db: Session,
        current_user: User,
        report_type: str,
        filters: Dict[str, Any],
        format: ExportFormat
    ) -> Dict[str, Any]:
        """
        Export report data in specified format
        
        Args:
            db: Database session
            current_user: Current authenticated user
            report_type: Type of report (dashboard, issues, contractors, assets)
            filters: Report filters
            format: Export format (csv or json)
            
        Returns:
            Dictionary with export data
        """
        # Generate report data based on type
        if report_type == "dashboard":
            data = ReportService.get_dashboard_stats(
                db, current_user,
                filters.get("from_date"), filters.get("to_date")
            )
            data_dict = data.model_dump()
            record_count = 1
            
        elif report_type == "issues":
            data = ReportService.get_issue_analytics(
                db, current_user,
                filters.get("category"),
                filters.get("priority"),
                filters.get("status"),
                filters.get("from_date"),
                filters.get("to_date")
            )
            data_dict = data.model_dump()
            record_count = data.total_issues
            
        elif report_type == "contractors":
            data = ReportService.get_contractor_performance(
                db, current_user,
                filters.get("contractor_id"),
                filters.get("from_date"),
                filters.get("to_date")
            )
            data_dict = [item.model_dump() for item in data]
            record_count = len(data)
            
        elif report_type == "assets":
            data = ReportService.get_asset_usage_report(
                db, current_user,
                filters.get("asset_id"),
                filters.get("asset_type"),
                filters.get("from_date"),
                filters.get("to_date")
            )
            data_dict = [item.model_dump() for item in data]
            record_count = len(data)
            
        else:
            return {
                "format": format.value,
                "data": None,
                "record_count": 0,
                "generated_at": datetime.utcnow(),
                "message": f"Invalid report type: {report_type}"
            }
        
        # Format data
        if format == ExportFormat.CSV:
            csv_data = ReportService._format_as_csv(data_dict)
            return {
                "format": "csv",
                "data": csv_data,
                "record_count": record_count,
                "generated_at": datetime.utcnow(),
                "message": "Report exported successfully"
            }
        else:  # JSON
            return {
                "format": "json",
                "data": json.dumps(data_dict, indent=2, default=str),
                "record_count": record_count,
                "generated_at": datetime.utcnow(),
                "message": "Report exported successfully"
            }
    
    # Helper methods
    
    @staticmethod
    def _calculate_avg_resolution_time(
        db: Session,
        current_user: User,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Optional[float]:
        """Calculate average resolution time in hours"""
        query = db.query(Issue).filter(
            Issue.resolved_at.isnot(None),
            Issue.created_at.isnot(None)
        )
        
        # Role-based filtering
        if current_user.role == UserRole.RESIDENT:
            query = query.filter(Issue.reported_by == current_user.id)
        
        if from_date:
            query = query.filter(Issue.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.filter(Issue.created_at <= datetime.combine(to_date, datetime.max.time()))
        if category:
            query = query.filter(Issue.category == IssueCategory(category.lower()))
        
        issues = query.all()
        
        if not issues:
            return None
        
        total_hours = 0
        for issue in issues:
            delta = issue.resolved_at - issue.created_at
            total_hours += delta.total_seconds() / 3600  # Convert to hours
        
        return round(total_hours / len(issues), 2)
    
    @staticmethod
    def _generate_issue_trend(query) -> List[TrendData]:
        """Generate daily issue creation trend"""
        issues = query.order_by(Issue.created_at).all()
        
        if not issues:
            return []
        
        # Group by date
        date_counts = {}
        for issue in issues:
            date_str = issue.created_at.date().isoformat()
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        # Convert to TrendData list
        return [TrendData(date=date_str, count=count) for date_str, count in sorted(date_counts.items())]
    
    @staticmethod
    def _calculate_utilization_rate(
        asset: Asset,
        bookings: List[AssetBooking],
        from_date: Optional[date],
        to_date: Optional[date]
    ) -> float:
        """Calculate asset utilization rate as percentage"""
        if not asset.operating_hours_start or not asset.operating_hours_end:
            return 0.0
        
        # Calculate total available hours
        operating_hours_per_day = (
            datetime.combine(date.today(), asset.operating_hours_end) -
            datetime.combine(date.today(), asset.operating_hours_start)
        ).total_seconds() / 3600
        
        # Calculate number of days
        if from_date and to_date:
            days = (to_date - from_date).days + 1
        elif from_date:
            days = (date.today() - from_date).days + 1
        elif to_date:
            # If only to_date, assume 30 days back
            days = 30
        else:
            days = 30  # Default to 30 days
        
        total_available_hours = operating_hours_per_day * days
        
        # Calculate booked hours
        confirmed_bookings = [b for b in bookings if b.status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]]
        total_booked_minutes = sum(b.duration_minutes for b in confirmed_bookings if b.duration_minutes)
        total_booked_hours = total_booked_minutes / 60
        
        if total_available_hours == 0:
            return 0.0
        
        return (total_booked_hours / total_available_hours) * 100
    
    @staticmethod
    def _get_popular_time_slots(bookings: List[AssetBooking]) -> List[TimeSlot]:
        """Get popular booking time slots"""
        hour_counts = {}
        
        for booking in bookings:
            if booking.start_time:
                hour = booking.start_time.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Sort by count and return top 5
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [TimeSlot(hour=hour, booking_count=count) for hour, count in sorted_hours]
    
    @staticmethod
    def _generate_booking_trend(bookings: List[AssetBooking]) -> List[TrendData]:
        """Generate daily booking trend with planned vs completed breakdown"""
        date_data: Dict[str, Dict[str, int]] = {}

        for booking in bookings:
            if booking.booking_date:
                d = booking.booking_date.isoformat()
                if d not in date_data:
                    date_data[d] = {'total': 0, 'planned': 0, 'completed': 0}
                date_data[d]['total'] += 1
                if booking.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
                    date_data[d]['planned'] += 1
                elif booking.status == BookingStatus.COMPLETED:
                    date_data[d]['completed'] += 1

        return [
            TrendData(date=d, count=v['total'], planned=v['planned'], completed=v['completed'])
            for d, v in sorted(date_data.items())
        ]
    
    @staticmethod
    def _format_as_csv(data: Any) -> str:
        """Convert data to CSV format"""
        output = io.StringIO()
        
        if isinstance(data, dict):
            # Single record (like dashboard)
            writer = csv.DictWriter(output, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)
        elif isinstance(data, list) and len(data) > 0:
            # Multiple records (like contractors or assets)
            # Flatten nested structures for CSV
            flattened = []
            for item in data:
                flat_item = ReportService._flatten_dict(item)
                flattened.append(flat_item)
            
            writer = csv.DictWriter(output, fieldnames=flattened[0].keys())
            writer.writeheader()
            writer.writerows(flattened)
        
        return output.getvalue()
    
    @staticmethod
    def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ReportService._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to comma-separated strings
                items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)
