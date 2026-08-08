# Reports & Analytics - Implementation Plan

## 📋 Feature: Reports & Analytics API

### Objective
Build comprehensive reporting and analytics endpoints to provide insights on:
- Dashboard statistics (overall system metrics)
- Issue analytics (resolution time, category/priority distribution, trends)
- Contractor performance reports (ratings, completion rate, response time)
- Asset usage analytics (booking statistics, revenue, utilization)
- Date range filtering for all reports
- Export functionality (CSV/JSON formats)

---

## 🎯 Affected Components

### Backend Files to Create
- [x] `backend/app/api/v1/endpoints/reports.py` - Reports endpoints
- [x] `backend/app/services/report_service.py` - Report generation logic
- [x] `backend/app/schemas/report.py` - Report request/response schemas

### Backend Files to Modify
- [x] `backend/app/api/v1/api.py` - Add reports router
- [x] `backend/app/models/__init__.py` - Already has all models imported

### Documentation to Update
- [x] `backend/API_IMPLEMENTATION_PLAN.md` - Update Phase 3 status
- [x] `REFERENCE.md` - Add reports endpoint documentation
- [x] `IMPLEMENTATION_CHECKLIST.md` - Mark reports feature as complete

---

## 🛠 Implementation Steps

### Step 1: Create Report Schemas (30 minutes)
**File:** `backend/app/schemas/report.py`

**Schemas to create:**
```python
# Request schemas
- DateRangeFilter (from_date, to_date)
- IssueReportFilter (category, priority, status, date_range)
- ContractorReportFilter (contractor_id, date_range)
- AssetReportFilter (asset_id, asset_type, date_range)
- ExportFormat (format: csv/json)

# Response schemas
- DashboardStats
  - total_issues, open_issues, resolved_issues, avg_resolution_time
  - total_users (by role), active_contractors
  - total_assets, total_bookings, booking_revenue
  - recent_activity_count

- IssueAnalytics
  - issues_by_category (dict)
  - issues_by_priority (dict)
  - issues_by_status (dict)
  - avg_resolution_time_by_category (dict)
  - resolution_rate (percentage)
  - trend_data (daily/weekly counts)

- ContractorPerformance
  - contractor_id, contractor_name
  - total_jobs_completed, completion_rate
  - average_rating, total_ratings
  - avg_response_time (hours)
  - recent_ratings (last 5)

- AssetUsageReport
  - asset_id, asset_name, asset_type
  - total_bookings, total_revenue
  - utilization_rate (percentage)
  - popular_time_slots
  - booking_trend (daily/weekly)

- ExportResponse
  - file_url or data (depending on format)
  - format, generated_at, record_count
```

---

### Step 2: Create Report Service (3-4 hours)
**File:** `backend/app/services/report_service.py`

**Service class:** `ReportService`

**Methods to implement:**

1. **`get_dashboard_stats(db: Session, current_user: User) -> DashboardStats`**
   - Query total/open/resolved issues count
   - Calculate avg resolution time (resolved_at - created_at)
   - Count users by role
   - Count active contractors
   - Count assets and bookings
   - Calculate booking revenue (sum of costs)
   - Count recent activities (last 7 days)

2. **`get_issue_analytics(db: Session, filters: IssueReportFilter, current_user: User) -> IssueAnalytics`**
   - Filter issues by date range, category, priority, status
   - Group by category/priority/status (use SQLAlchemy group_by)
   - Calculate avg resolution time per category
   - Calculate resolution rate (resolved/total)
   - Generate trend data (group by date)
   - Role-based filtering (residents see only their issues)

3. **`get_contractor_performance(db: Session, filters: ContractorReportFilter, current_user: User) -> List[ContractorPerformance]`**
   - Query contractors with profiles
   - Join with ratings and work_completions
   - Calculate metrics: completion_rate, avg_rating, avg_response_time
   - Filter by date range
   - Order by rating or completion rate

4. **`get_asset_usage_report(db: Session, filters: AssetReportFilter, current_user: User) -> List[AssetUsageReport]`**
   - Query assets with bookings
   - Filter by asset_id, asset_type, date_range
   - Calculate total bookings and revenue
   - Calculate utilization rate (booked hours / available hours)
   - Find popular time slots (group by hour)
   - Generate booking trends

5. **`export_report(db: Session, report_type: str, filters: dict, format: str, current_user: User) -> dict`**
   - Call appropriate report method
   - Convert data to CSV or JSON
   - Return file data or save to temp location
   - Include metadata (generated_at, record_count)

**Helper functions:**
- `_apply_date_filter(query, model, date_field, from_date, to_date)`
- `_format_as_csv(data: List[dict]) -> str`
- `_calculate_avg_resolution_time(issues: List[Issue]) -> float`
- `_calculate_utilization_rate(asset: Asset, bookings: List[AssetBooking], date_range) -> float`

---

### Step 3: Create Reports Endpoints (2-3 hours)
**File:** `backend/app/api/v1/endpoints/reports.py`

**Endpoints to create:**

1. **`GET /api/v1/reports/dashboard`**
   - Summary: Get dashboard statistics
   - Auth: Required (any role)
   - Query params: date_range (optional)
   - Response: DashboardStats
   - Role-based data (residents see limited stats)

2. **`GET /api/v1/reports/issues`**
   - Summary: Get issue analytics
   - Auth: Required
   - Query params: category, priority, status, from_date, to_date
   - Response: IssueAnalytics
   - Role-based filtering

3. **`GET /api/v1/reports/contractors`**
   - Summary: Get contractor performance report
   - Auth: Required (admin only)
   - Query params: contractor_id, from_date, to_date
   - Response: List[ContractorPerformance]

4. **`GET /api/v1/reports/assets`**
   - Summary: Get asset usage report
   - Auth: Required (admin/facility)
   - Query params: asset_id, asset_type, from_date, to_date
   - Response: List[AssetUsageReport]

5. **`POST /api/v1/reports/export`**
   - Summary: Export report data
   - Auth: Required (admin only)
   - Request body: { report_type, filters, format }
   - Response: ExportResponse with CSV/JSON data

**Error handling:**
- 400: Invalid date range
- 403: Insufficient permissions
- 422: Invalid filters
- 500: Report generation error

---

### Step 4: Register Router (15 minutes)
**File:** `backend/app/api/v1/api.py`

Add reports router:
```python
from app.api.v1.endpoints import reports

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)
```

---

### Step 5: Testing Plan (2-3 hours)

**Manual Testing (Swagger UI):**
1. Test dashboard stats with different roles (resident, admin)
2. Test issue analytics with various filters
3. Test contractor performance report (admin)
4. Test asset usage report (admin/facility)
5. Test export functionality (CSV and JSON)
6. Test date range filtering
7. Test role-based access control

**Test Cases to Verify:**
- [ ] Dashboard shows correct counts
- [ ] Avg resolution time calculated correctly
- [ ] Issue analytics filters work (category, priority, status)
- [ ] Residents see only their issue analytics
- [ ] Admins see all data
- [ ] Contractor performance metrics accurate
- [ ] Asset utilization rate calculated correctly
- [ ] Date range filtering works
- [ ] Export generates valid CSV/JSON
- [ ] Unauthorized users get 403 errors

**Sample Test Data:**
- Create 10+ issues across different categories/priorities
- Resolve 5-7 issues with different resolution times
- Create 2-3 contractor profiles with ratings
- Create 5+ asset bookings across different assets
- Test with date ranges: last 7 days, last 30 days, custom range

---

### Step 6: Documentation Updates (30 minutes)

**Update REFERENCE.md:**
- Add all 5 new endpoints with descriptions
- Document request/response schemas
- Add example requests and responses
- Document role-based access rules

**Update API_IMPLEMENTATION_PLAN.md:**
- Mark "Reports & Analytics" as completed
- Update Phase 3 progress
- Add completion date

**Update IMPLEMENTATION_CHECKLIST.md:**
- Add checkmarks for completed report features

---

## 📊 Database Queries

### Key Queries to Implement:

1. **Issue Statistics:**
```sql
-- Count by category
SELECT category, COUNT(*) FROM issues WHERE created_at >= ? GROUP BY category

-- Avg resolution time
SELECT AVG(JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24 
FROM issues WHERE resolved_at IS NOT NULL

-- Issues by date (trend)
SELECT DATE(created_at) as date, COUNT(*) 
FROM issues 
WHERE created_at >= ? 
GROUP BY DATE(created_at)
ORDER BY date
```

2. **Contractor Performance:**
```sql
-- Contractor with metrics
SELECT cp.*, AVG(cr.rating) as avg_rating, COUNT(wc.id) as jobs_completed
FROM contractor_profiles cp
LEFT JOIN contractor_ratings cr ON cp.id = cr.contractor_id
LEFT JOIN work_completions wc ON cp.id = wc.contractor_id
GROUP BY cp.id
```

3. **Asset Usage:**
```sql
-- Bookings per asset
SELECT a.id, a.name, COUNT(ab.id) as booking_count, SUM(ab.cost) as revenue
FROM assets a
LEFT JOIN asset_bookings ab ON a.id = ab.asset_id
WHERE ab.booking_date >= ?
GROUP BY a.id
```

---

## 🔒 Security Considerations

1. **Role-Based Access:**
   - Dashboard: All authenticated users (data filtered by role)
   - Issue analytics: All users (residents see only their data)
   - Contractor reports: Admin only
   - Asset reports: Admin and facility managers
   - Export: Admin only

2. **Data Privacy:**
   - Residents should not see other residents' data
   - Contractors should see their own performance only
   - Aggregated data is safe to show

3. **Rate Limiting:**
   - Export endpoint should have rate limiting (future enhancement)
   - Large date ranges should be paginated or limited

---

## 📦 Dependencies

**No new packages required** - All functionality uses existing dependencies:
- SQLAlchemy for queries
- FastAPI for endpoints
- Pydantic for schemas
- Standard library for CSV export

---

## 🚀 Deployment Checklist

- [ ] All endpoints tested locally
- [ ] Documentation updated
- [ ] No database migrations needed (using existing tables)
- [ ] API documented in Swagger
- [ ] Role-based access verified
- [ ] Export functionality tested
- [ ] Performance tested with 100+ records

---

## 📈 Performance Optimization (Future)

1. **Caching:**
   - Cache dashboard stats for 5-10 minutes
   - Use Redis for report caching
   - Invalidate on data changes

2. **Query Optimization:**
   - Add indexes on date fields (created_at, resolved_at)
   - Use query result streaming for large exports
   - Paginate large result sets

3. **Background Processing:**
   - Move PDF export to background task queue
   - Schedule daily/weekly report generation
   - Email reports to admins

---

## ⏱ Estimated Time Breakdown

| Task | Estimated Time |
|------|---------------|
| Create schemas | 30 minutes |
| Implement ReportService | 3-4 hours |
| Create endpoints | 2-3 hours |
| Testing | 2-3 hours |
| Documentation | 30 minutes |
| **Total** | **8-11 hours (~2 days)** |

---

## ✅ Success Criteria

- [ ] 5 new endpoints implemented and working
- [ ] Dashboard shows accurate statistics
- [ ] Issue analytics provides insights
- [ ] Contractor performance tracked correctly
- [ ] Asset usage reported accurately
- [ ] Export generates valid CSV/JSON
- [ ] Role-based access enforced
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Swagger UI documentation clear

---

## 🎯 Next Steps After Completion

1. **Phase 3 Continuation:**
   - Implement Contractor Management (Item 5)
   - Already completed: Asset Management (Item 6)

2. **Future Enhancements:**
   - PDF export with charts/graphs
   - Email scheduled reports
   - Custom report builder
   - Real-time dashboard with WebSockets
   - Advanced analytics (predictions, trends)

---

**Plan Created:** 2026-07-25  
**Status:** Ready for Implementation  
**Priority:** High (Phase 3 - Advanced Features)  
**Estimated Completion:** 2 days
