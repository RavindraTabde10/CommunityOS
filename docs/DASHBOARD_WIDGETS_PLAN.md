# Dashboard Widgets Implementation Plan

## Overview
Add role-based widgets to the lower-left section of the dashboard to enhance community engagement and administrative efficiency.

**Date:** 2026-07-29  
**Status:** Planning Phase

---

## Role-Based Widget Configuration

### For Residents:
1. **Upcoming Events Calendar** - Shows next community events
2. **Payment Reminders** - Shows pending dues and payments

### For Admins:
1. **Pending Approvals Widget** - Quick view of items awaiting approval
2. **Recent Notices** - Latest official notices/circulars

---

## Phase 1: Backend Implementation

### 1.1 Database Models

#### **Model 1: Event**
**File:** `backend/app/models/event.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class EventType(str, enum.Enum):
    MEETING = "meeting"
    FESTIVAL = "festival"
    MAINTENANCE = "maintenance"
    SOCIAL = "social"
    SPORTS = "sports"
    OTHER = "other"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    venue = Column(String(200), nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_by = Column(Integer, nullable=False)  # Admin user ID
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### **Model 2: Payment**
**File:** `backend/app/models/payment.py`

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class PaymentType(str, enum.Enum):
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    EVENT = "event"
    FINE = "fine"
    OTHER = "other"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    description = Column(String(500), nullable=True)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
```

#### **Model 3: Notice**
**File:** `backend/app/models/notice.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.sql import func
import enum
from app.db.base import Base

class NoticeCategory(str, enum.Enum):
    MAINTENANCE = "maintenance"
    BILLING = "billing"
    RULES = "rules"
    GENERAL = "general"
    URGENT = "urgent"

class Notice(Base):
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(NoticeCategory), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher = more important
    
    created_by = Column(Integer, nullable=False)  # Admin user ID
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

### 1.2 Database Migration
**File:** `backend/alembic/versions/XXXXX_add_dashboard_widgets.py`
- Create events table
- Create payments table
- Create notices table
- Add relationship to users table for payments

### 1.3 Pydantic Schemas

#### **Events Schemas**
**File:** `backend/app/schemas/event.py`
- `EventBase` - Base fields
- `EventCreate` - For creating events
- `EventUpdate` - For updating events
- `EventInDB` - Database representation
- `EventResponse` - API response

#### **Payments Schemas**
**File:** `backend/app/schemas/payment.py`
- `PaymentBase` - Base fields
- `PaymentCreate` - For creating payments
- `PaymentUpdate` - For updating payments
- `PaymentInDB` - Database representation
- `PaymentResponse` - API response with user info

#### **Notices Schemas**
**File:** `backend/app/schemas/notice.py`
- `NoticeBase` - Base fields
- `NoticeCreate` - For creating notices
- `NoticeUpdate` - For updating notices
- `NoticeInDB` - Database representation
- `NoticeResponse` - API response

### 1.4 Services

#### **Event Service**
**File:** `backend/app/services/event_service.py`
- `get_upcoming_events(db, limit=5)` - Get next upcoming events
- `create_event(db, event_data, user_id)` - Admin only
- `update_event(db, event_id, event_data)` - Admin only
- `delete_event(db, event_id)` - Admin only
- `get_event_by_id(db, event_id)` - Get single event

#### **Payment Service**
**File:** `backend/app/services/payment_service.py`
- `get_user_pending_payments(db, user_id)` - Get user's pending payments
- `create_payment(db, payment_data)` - Admin only
- `update_payment_status(db, payment_id, status)` - Mark as paid/cancelled
- `get_overdue_payments(db, user_id=None)` - Get overdue payments

#### **Notice Service**
**File:** `backend/app/services/notice_service.py`
- `get_recent_notices(db, limit=5)` - Get latest notices
- `create_notice(db, notice_data, user_id)` - Admin only
- `update_notice(db, notice_id, notice_data)` - Admin only
- `delete_notice(db, notice_id)` - Admin only

### 1.5 API Endpoints

#### **Events Endpoints**
**File:** `backend/app/api/v1/events.py`
```
GET    /api/v1/events/upcoming          - Get upcoming events (all users)
POST   /api/v1/events                   - Create event (admin only)
GET    /api/v1/events/{id}              - Get event details (all users)
PUT    /api/v1/events/{id}              - Update event (admin only)
DELETE /api/v1/events/{id}              - Delete event (admin only)
GET    /api/v1/events                   - Get all events with filters (all users)
```

#### **Payments Endpoints**
**File:** `backend/app/api/v1/payments.py`
```
GET    /api/v1/payments/my-payments     - Get current user's payments (residents)
POST   /api/v1/payments                 - Create payment record (admin only)
PUT    /api/v1/payments/{id}/status     - Update payment status (admin/resident)
GET    /api/v1/payments/overdue         - Get overdue payments (admin only)
GET    /api/v1/payments                 - Get all payments (admin only)
```

#### **Notices Endpoints**
**File:** `backend/app/api/v1/notices.py`
```
GET    /api/v1/notices/recent           - Get recent notices (all users)
POST   /api/v1/notices                  - Create notice (admin only)
GET    /api/v1/notices/{id}             - Get notice details (all users)
PUT    /api/v1/notices/{id}             - Update notice (admin only)
DELETE /api/v1/notices/{id}             - Delete notice (admin only)
GET    /api/v1/notices                  - Get all notices with filters (all users)
```

#### **Approvals Endpoints Enhancement**
**File:** `backend/app/api/v1/approvals.py` (if exists) or create new
```
GET    /api/v1/approvals/pending-count  - Get count of pending approvals (admin only)
GET    /api/v1/approvals/summary        - Get approval summary by category (admin only)
```

---

## Phase 2: Frontend Implementation

### 2.1 API Client Functions

#### **Events API**
**File:** `frontend/src/api/events.js`
```javascript
export const eventsAPI = {
  getUpcoming: (limit = 5) => api.get(`/events/upcoming?limit=${limit}`),
  create: (data) => api.post('/events', data),
  getById: (id) => api.get(`/events/${id}`),
  update: (id, data) => api.put(`/events/${id}`, data),
  delete: (id) => api.delete(`/events/${id}`),
  getAll: (filters) => api.get('/events', { params: filters }),
}
```

#### **Payments API**
**File:** `frontend/src/api/payments.js`
```javascript
export const paymentsAPI = {
  getMyPayments: () => api.get('/payments/my-payments'),
  create: (data) => api.post('/payments', data),
  updateStatus: (id, status) => api.put(`/payments/${id}/status`, { status }),
  getOverdue: () => api.get('/payments/overdue'),
  getAll: (filters) => api.get('/payments', { params: filters }),
}
```

#### **Notices API**
**File:** `frontend/src/api/notices.js`
```javascript
export const noticesAPI = {
  getRecent: (limit = 5) => api.get(`/notices/recent?limit=${limit}`),
  create: (data) => api.post('/notices', data),
  getById: (id) => api.get(`/notices/${id}`),
  update: (id, data) => api.put(`/notices/${id}`, data),
  delete: (id) => api.delete(`/notices/${id}`),
  getAll: (filters) => api.get('/notices', { params: filters }),
}
```

### 2.2 Dashboard Widget Components

#### **Component 1: UpcomingEvents**
**File:** `frontend/src/components/dashboard/UpcomingEvents.jsx`
- Displays next 5 upcoming events
- Color-coded by event type
- Shows: title, date, time, venue
- Click to view full details
- "View All Events" link at bottom

#### **Component 2: PaymentReminders**
**File:** `frontend/src/components/dashboard/PaymentReminders.jsx`
- Shows pending and overdue payments
- Displays: amount, type, due date
- Visual indicator for overdue (red)
- "Pay Now" button (future feature)
- "View All Payments" link

#### **Component 3: PendingApprovals**
**File:** `frontend/src/components/dashboard/PendingApprovals.jsx`
- Shows count of pending items
- Categories: New residents, contractor access, bookings
- Click to navigate to specific approval section
- Visual urgency indicators

#### **Component 4: RecentNotices**
**File:** `frontend/src/components/dashboard/RecentNotices.jsx`
- Shows latest 4 notices
- Displays: title, category, date
- Category badges with colors
- Click to read full notice
- "View All Notices" link

### 2.3 Full Pages (Future)

#### **Events Page**
**File:** `frontend/src/pages/Events.jsx`
- Calendar view of all events
- Filter by event type
- Admin: Create/Edit/Delete events
- Resident: View only

#### **Payments Page**
**File:** `frontend/src/pages/Payments.jsx`
- Payment history table
- Filter by status, date
- Admin: Create payment records
- Resident: View own payments, mark as paid

#### **Notices Page**
**File:** `frontend/src/pages/Notices.jsx`
- List of all notices
- Filter by category
- Admin: Create/Edit/Delete notices
- Resident: View only

### 2.4 Dashboard Integration
**File:** `frontend/src/pages/Dashboard.jsx`
- Integrate widgets into the lower-left section (red box area)
- Role-based rendering:
  - Resident: Show UpcomingEvents + PaymentReminders
  - Admin: Show PendingApprovals + RecentNotices
- Maintain responsive 2-column grid layout

### 2.5 Routes Configuration
**File:** `frontend/src/utils/constants.js`
Add new routes:
```javascript
EVENTS: '/events',
PAYMENTS: '/payments',
NOTICES: '/notices',
```

**File:** `frontend/src/App.jsx`
Add route definitions for new pages

### 2.6 Navigation Updates
**File:** `frontend/src/components/layout/Sidebar.jsx`
Add new menu items:
- Events (for all users)
- Payments (residents see "My Payments", admins see "All Payments")
- Notices (for all users)

---

## Phase 3: Testing & Validation

### 3.1 Backend Testing
- Test all API endpoints with Swagger UI
- Verify role-based access control
- Test database relationships
- Validate data constraints

### 3.2 Frontend Testing
- Test widget rendering for different roles
- Verify API integration
- Test responsive layout
- Validate user interactions

### 3.3 Integration Testing
- End-to-end user workflows
- Payment creation and status updates
- Event creation and display
- Notice creation and distribution

---

## Implementation Order

### **Step 1: Events Feature** (Highest Priority)
1. Backend: Event model, schema, service, API
2. Database migration
3. Frontend: UpcomingEvents widget
4. Frontend: Events page (basic)
5. Test and validate

### **Step 2: Notices Feature**
1. Backend: Notice model, schema, service, API
2. Database migration
3. Frontend: RecentNotices widget
4. Frontend: Notices page (basic)
5. Test and validate

### **Step 3: Payments Feature**
1. Backend: Payment model, schema, service, API
2. Database migration
3. Frontend: PaymentReminders widget
4. Frontend: Payments page (basic)
5. Test and validate

### **Step 4: Pending Approvals Enhancement**
1. Backend: Approval summary endpoints
2. Frontend: PendingApprovals widget
3. Test and validate

### **Step 5: Dashboard Integration**
1. Integrate all widgets
2. Role-based rendering
3. Layout optimization
4. Final testing

---

## Files to Create/Modify

### Backend (New Files: 12)
- `backend/app/models/event.py`
- `backend/app/models/payment.py`
- `backend/app/models/notice.py`
- `backend/app/schemas/event.py`
- `backend/app/schemas/payment.py`
- `backend/app/schemas/notice.py`
- `backend/app/services/event_service.py`
- `backend/app/services/payment_service.py`
- `backend/app/services/notice_service.py`
- `backend/app/api/v1/events.py`
- `backend/app/api/v1/payments.py`
- `backend/app/api/v1/notices.py`

### Backend (Modified Files: 3)
- `backend/app/main.py` - Register new routers
- `backend/app/models/__init__.py` - Import new models
- `backend/alembic/versions/XXXXX_add_dashboard_widgets.py` - Migration

### Frontend (New Files: 8)
- `frontend/src/api/events.js`
- `frontend/src/api/payments.js`
- `frontend/src/api/notices.js`
- `frontend/src/components/dashboard/UpcomingEvents.jsx`
- `frontend/src/components/dashboard/PaymentReminders.jsx`
- `frontend/src/components/dashboard/PendingApprovals.jsx`
- `frontend/src/components/dashboard/RecentNotices.jsx`
- `frontend/src/pages/Events.jsx` (future)
- `frontend/src/pages/Payments.jsx` (future)
- `frontend/src/pages/Notices.jsx` (future)

### Frontend (Modified Files: 4)
- `frontend/src/pages/Dashboard.jsx` - Integrate widgets
- `frontend/src/App.jsx` - Add routes
- `frontend/src/utils/constants.js` - Add route constants
- `frontend/src/components/layout/Sidebar.jsx` - Add menu items

---

## Design Considerations

### UI/UX Guidelines
1. **Compact Layout:** Widgets must fit in available space without scrolling
2. **Color Coding:** Use consistent colors for event types, payment status, notice categories
3. **Responsive:** Works on different screen sizes
4. **Loading States:** Show skeleton loaders while fetching data
5. **Empty States:** Clear messages when no data available
6. **Error Handling:** Graceful error messages

### Color Scheme
- **Events:**
  - Meeting: Blue (#1976d2)
  - Festival: Purple (#9c27b0)
  - Maintenance: Orange (#ff9800)
  - Social: Green (#4caf50)
  - Sports: Teal (#009688)

- **Payments:**
  - Pending: Blue
  - Paid: Green
  - Overdue: Red

- **Notices:**
  - Urgent: Red
  - Maintenance: Orange
  - Billing: Blue
  - Rules: Purple
  - General: Gray

---

## Timeline Estimate

- **Phase 1 (Events):** 3-4 hours
- **Phase 2 (Notices):** 2-3 hours
- **Phase 3 (Payments):** 3-4 hours
- **Phase 4 (Approvals):** 1-2 hours
- **Phase 5 (Integration):** 1-2 hours
- **Total:** 10-15 hours

---

## Notes
- Start with Events feature as it's most engaging
- Payment processing (actual payment gateway) is future scope
- Pending Approvals widget reuses existing approval system
- All features support future mobile app integration
- Consider adding notification system later

---

## Success Criteria
✅ Residents see relevant events and payment reminders  
✅ Admins see pending approvals and recent notices  
✅ All widgets fit in dashboard without scrolling  
✅ Role-based access control working correctly  
✅ Clean, intuitive UI with proper loading/error states  
✅ Full CRUD operations working for admins  
✅ Database properly normalized and indexed  

---

**Ready to proceed with Step 1: Events Feature Implementation?**
