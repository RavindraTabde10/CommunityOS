# Asset & Facility Management - Implementation Plan

## 📋 Feature Overview

**Feature:** Asset & Facility Management System  
**Phase:** Phase 3 - Advanced Features  
**Estimated Time:** 5-6 days  
**Status:** Ready for Implementation  
**Date:** 2026-07-25

---

## 🎯 Objective

Implement a complete asset and facility booking system for residential societies, allowing residents to:
- View available facilities (gym, pool, clubhouse, party hall, etc.)
- Book facilities for specific time slots
- Check-in/check-out from facilities
- Track facility usage
- Generate QR codes for facility access

Administrators can:
- Create and manage facilities
- View booking statistics
- Track maintenance schedules
- Monitor facility usage

---

## 📊 Implementation Components

### 1. Database Models

#### Asset Model
```python
- id: UUID (primary key)
- organization_id: ForeignKey (for multi-tenancy)
- name: String (e.g., "Swimming Pool", "Gym")
- asset_type: Enum (gym, pool, clubhouse, party_hall, sports_court, meeting_room, parking, other)
- description: Text
- location: String (building/floor)
- capacity: Integer (max people)
- hourly_rate: Decimal (booking cost)
- is_bookable: Boolean (can be booked online)
- is_active: Boolean (available for use)
- operating_hours_start: Time
- operating_hours_end: Time
- advance_booking_days: Integer (how far in advance can book)
- min_booking_duration: Integer (minutes)
- max_booking_duration: Integer (minutes)
- qr_code_data: String (unique identifier for QR)
- created_at: DateTime
- updated_at: DateTime
```

#### AssetBooking Model
```python
- id: UUID (primary key)
- organization_id: ForeignKey
- asset_id: ForeignKey
- user_id: ForeignKey
- booking_date: Date
- start_time: Time
- end_time: Time
- duration_minutes: Integer
- purpose: Text (optional)
- number_of_guests: Integer
- status: Enum (pending, confirmed, cancelled, completed, no_show)
- payment_amount: Decimal
- payment_status: Enum (pending, paid, refunded)
- checked_in_at: DateTime (nullable)
- checked_out_at: DateTime (nullable)
- cancelled_at: DateTime (nullable)
- cancellation_reason: Text (nullable)
- created_at: DateTime
- updated_at: DateTime
```

#### AssetMaintenance Model (Optional for MVP)
```python
- id: UUID (primary key)
- asset_id: ForeignKey
- scheduled_date: Date
- maintenance_type: Enum (routine, repair, inspection, cleaning)
- description: Text
- performed_by: String
- status: Enum (scheduled, in_progress, completed, cancelled)
- completed_at: DateTime
- notes: Text
- created_at: DateTime
```

### 2. Enums

```python
class AssetType(str, enum.Enum):
    GYM = "gym"
    POOL = "pool"
    CLUBHOUSE = "clubhouse"
    PARTY_HALL = "party_hall"
    SPORTS_COURT = "sports_court"
    MEETING_ROOM = "meeting_room"
    PARKING = "parking"
    OTHER = "other"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
```

### 3. Pydantic Schemas

#### Request Schemas
- `AssetCreate` - Create new asset (admin)
- `AssetUpdate` - Update asset details (admin)
- `BookingCreate` - Create booking request
- `BookingUpdate` - Update booking (status, etc.)
- `CheckInRequest` - Check-in to facility
- `CheckOutRequest` - Check-out from facility

#### Response Schemas
- `AssetResponse` - Asset details with relationships
- `BookingResponse` - Booking details with user and asset info
- `AssetStatsResponse` - Usage statistics
- `BookingCalendarResponse` - Available time slots

### 4. API Endpoints

```
Asset Management (Admin):
POST   /api/v1/assets                       - Create asset
GET    /api/v1/assets                       - List all assets
GET    /api/v1/assets/{id}                  - Get asset details
PUT    /api/v1/assets/{id}                  - Update asset
DELETE /api/v1/assets/{id}                  - Delete/deactivate asset
GET    /api/v1/assets/{id}/stats            - Usage statistics

Booking Management:
POST   /api/v1/assets/{id}/bookings         - Create booking
GET    /api/v1/assets/{id}/bookings         - List bookings for asset
GET    /api/v1/bookings                     - List user's bookings
GET    /api/v1/bookings/{id}                - Get booking details
PUT    /api/v1/bookings/{id}                - Update booking
DELETE /api/v1/bookings/{id}                - Cancel booking
GET    /api/v1/assets/{id}/availability     - Check availability

Check-in/Check-out:
POST   /api/v1/bookings/{id}/checkin        - Check-in to facility
POST   /api/v1/bookings/{id}/checkout       - Check-out from facility

QR Code:
GET    /api/v1/assets/{id}/qrcode           - Generate/get QR code
POST   /api/v1/assets/scan                  - Scan QR code for access
```

### 5. Services

#### AssetService
- `create_asset()` - Create new asset
- `update_asset()` - Update asset details
- `get_asset()` - Get asset by ID
- `list_assets()` - List with filters
- `check_availability()` - Check if asset is available
- `generate_qr_code()` - Generate unique QR code

#### BookingService
- `create_booking()` - Create and validate booking
- `cancel_booking()` - Cancel with refund logic
- `check_conflicts()` - Check for time conflicts
- `calculate_cost()` - Calculate booking cost
- `get_available_slots()` - Get available time slots
- `check_in()` - Check-in user
- `check_out()` - Check-out user
- `auto_complete_bookings()` - Mark as completed after end time

---

## 🛠 Implementation Steps

### Step 1: Database Models & Migration (Day 1)
1. Create `backend/app/models/asset.py`
   - Asset model with all fields
   - AssetBooking model with relationships
   - AssetMaintenance model (optional)
   - Enums for asset types and booking status

2. Update `backend/app/models/__init__.py`
   - Export new models

3. Create Alembic migration
   - Run: `alembic revision --autogenerate -m "add asset and booking tables"`
   - Review migration file
   - Apply: `alembic upgrade head`

**Files to Create:**
- `backend/app/models/asset.py`

**Files to Modify:**
- `backend/app/models/__init__.py`

### Step 2: Pydantic Schemas (Day 2)
1. Create `backend/app/schemas/asset.py`
   - AssetBase, AssetCreate, AssetUpdate, AssetResponse
   - BookingBase, BookingCreate, BookingUpdate, BookingResponse
   - AssetStatsResponse
   - AvailabilityResponse

2. Update `backend/app/schemas/__init__.py`
   - Export new schemas

**Files to Create:**
- `backend/app/schemas/asset.py`

**Files to Modify:**
- `backend/app/schemas/__init__.py`

### Step 3: Service Layer (Day 3)
1. Create `backend/app/services/asset_service.py`
   - Implement all business logic
   - Validation functions
   - Availability checking
   - Cost calculation

2. QR Code generation
   - Install `qrcode` package
   - Generate unique codes for each asset
   - Store QR data in database

**Files to Create:**
- `backend/app/services/asset_service.py`

**Dependencies:**
- `qrcode[pil]` (for QR code generation)

### Step 4: API Endpoints - Asset Management (Day 4)
1. Create `backend/app/api/v1/endpoints/assets.py`
   - Implement asset CRUD endpoints
   - Role-based permissions (admin only for create/update/delete)
   - List with pagination and filters
   - QR code generation endpoint

**Files to Create:**
- `backend/app/api/v1/endpoints/assets.py`

**Files to Modify:**
- `backend/app/api/v1/api.py` (register routes)

### Step 5: API Endpoints - Booking Management (Day 5)
1. Create `backend/app/api/v1/endpoints/bookings.py`
   - Create booking with validation
   - List bookings (user's own + admin sees all)
   - Update/cancel booking
   - Check-in/check-out endpoints
   - Availability check endpoint

**Files to Create:**
- `backend/app/api/v1/endpoints/bookings.py`

**Files to Modify:**
- `backend/app/api/v1/api.py` (register routes)

### Step 6: Testing (Day 6)
1. Create test files
   - `backend/tests/test_assets.py` (asset CRUD tests)
   - `backend/tests/test_bookings.py` (booking flow tests)

2. Test scenarios:
   - Create/update/delete assets (admin)
   - Create booking (valid time)
   - Create booking (conflict detection)
   - Cancel booking
   - Check-in/check-out flow
   - QR code generation
   - Availability checking
   - Role-based permissions

**Files to Create:**
- `backend/tests/test_assets.py`
- `backend/tests/test_bookings.py`

---

## 🔍 Business Logic & Validations

### Booking Validations
1. **Time Conflict Check**
   - No overlapping bookings for same asset
   - Consider buffer time between bookings (optional)

2. **Operating Hours Check**
   - Booking must be within asset operating hours
   - Cannot book past operating hours

3. **Advance Booking Limit**
   - Cannot book beyond `advance_booking_days`
   - Cannot book in the past

4. **Duration Limits**
   - Booking duration >= `min_booking_duration`
   - Booking duration <= `max_booking_duration`

5. **Capacity Check**
   - Number of guests <= asset capacity

6. **User Limits (Optional)**
   - Max bookings per user per month
   - Cooldown period between bookings

### Booking Status Workflow
```
pending → confirmed → completed
        ↓
    cancelled
        ↓
    no_show (if not checked in within X minutes)
```

### Cost Calculation
```python
duration_hours = duration_minutes / 60
base_cost = hourly_rate * duration_hours
total_cost = base_cost * (1 + tax_rate)
```

---

## 📝 Documentation Updates

### Files to Update
1. **backend/API_README.md**
   - Add asset management section
   - Document all new endpoints
   - Add request/response examples

2. **REFERENCE.md**
   - Add Asset and AssetBooking models
   - Document enums
   - List new endpoints

3. **backend/API_IMPLEMENTATION_PLAN.md**
   - Mark feature as completed
   - Update status and test count

4. **IMPLEMENTATION_CHECKLIST.md**
   - Add asset management items
   - Mark as completed

---

## 🧪 Testing Plan

### Unit Tests (pytest)

#### Asset Management Tests
- [x] Create asset (admin only)
- [x] List all assets
- [x] Get asset by ID
- [x] Update asset (admin only)
- [x] Delete/deactivate asset (admin only)
- [x] Non-admin cannot create asset (403)
- [x] Generate QR code

#### Booking Management Tests
- [x] Create valid booking
- [x] Create booking with conflict (400)
- [x] Create booking outside operating hours (400)
- [x] Create booking beyond advance limit (400)
- [x] List user's bookings
- [x] Admin lists all bookings
- [x] Cancel booking
- [x] Check-in to booking
- [x] Check-out from booking
- [x] Check availability

#### Edge Cases
- [x] Book at exact operating hours boundary
- [x] Book with min/max duration
- [x] Exceed capacity
- [x] Multiple concurrent bookings (race condition)

**Target:** 30+ test cases

### Manual Testing (Swagger UI)

#### Happy Path
1. Admin creates a gym asset
2. User views available assets
3. User checks availability for tomorrow 6-7 PM
4. User creates booking
5. User checks in at booking time
6. User checks out after workout
7. Admin views booking statistics

#### Error Handling
1. Try to book conflicting time
2. Try to book 100 days in advance
3. Try to book for 10 hours (exceeds max)
4. Non-admin tries to create asset

---

## 🔧 Configuration Changes

### Environment Variables (Optional)
```env
# Asset Management
DEFAULT_BOOKING_ADVANCE_DAYS=30
DEFAULT_MIN_BOOKING_MINUTES=60
DEFAULT_MAX_BOOKING_MINUTES=240
DEFAULT_HOURLY_RATE=100
```

### Database Indexes
Add indexes for:
- `assets.organization_id`
- `assets.is_active`
- `asset_bookings.asset_id`
- `asset_bookings.user_id`
- `asset_bookings.booking_date`
- `asset_bookings.status`

---

## 📦 Dependencies

### New Python Packages
```
qrcode[pil]==7.4.2  # QR code generation
```

Add to `backend/requirements.txt`

---

## 🚨 Rollback Plan

### If Issues Occur
1. **Database Rollback**
   ```bash
   cd backend
   alembic downgrade -1
   ```

2. **Code Rollback**
   - Remove new files:
     - `backend/app/models/asset.py`
     - `backend/app/schemas/asset.py`
     - `backend/app/services/asset_service.py`
     - `backend/app/api/v1/endpoints/assets.py`
     - `backend/app/api/v1/endpoints/bookings.py`
   
   - Revert changes to:
     - `backend/app/models/__init__.py`
     - `backend/app/schemas/__init__.py`
     - `backend/app/api/v1/api.py`

3. **Dependencies**
   - Remove `qrcode` from requirements.txt
   - Uninstall: `pip uninstall qrcode pillow`

---

## ✅ Success Criteria

- [x] All database models created and migrated
- [x] All API endpoints functional
- [x] Role-based permissions working
- [x] Booking conflict detection working
- [x] QR code generation working
- [x] Check-in/check-out flow working
- [x] 30+ test cases passing
- [x] Documentation updated
- [x] Manual testing successful

---

## 🔄 Future Enhancements (Phase 4+)

1. **Recurring Bookings**
   - Weekly/monthly recurring slots

2. **Waitlist Management**
   - Join waitlist if fully booked
   - Auto-notify on cancellation

3. **Payment Integration**
   - Online payment for bookings
   - Refund processing

4. **Maintenance Scheduling**
   - Automatic blocking during maintenance
   - Maintenance history tracking

5. **Usage Analytics**
   - Peak usage times
   - Popular facilities
   - Revenue reports

6. **Mobile App Integration**
   - QR code scanning in mobile app
   - Push notifications for bookings

7. **Dynamic Pricing**
   - Peak/off-peak pricing
   - Holiday pricing

---

**Plan Version:** 1.0  
**Created:** 2026-07-25  
**Status:** Ready for Implementation  
**Estimated Completion:** 2026-07-30
