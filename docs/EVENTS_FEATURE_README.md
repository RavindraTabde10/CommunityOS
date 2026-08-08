# Events Feature - Migration Instructions

## ✅ Backend Implementation Complete

The following backend files have been created for the Events feature:

1. **Model:** `backend/app/models/event.py` - Event database model
2. **Schema:** `backend/app/schemas/event.py` - Pydantic validation schemas
3. **Service:** `backend/app/services/event_service.py` - Business logic
4. **API:** `backend/app/api/v1/events.py` - REST API endpoints
5. **Migration:** `backend/alembic/versions/9d0e1f2g3h4i_add_events_table.py` - Database migration

## ✅ Frontend Implementation Complete

The following frontend files have been created:

1. **API Client:** `frontend/src/api/events.js` - API integration
2. **Component:** `frontend/src/components/dashboard/UpcomingEvents.jsx` - Events widget
3. **Dashboard Updated:** Integrated UpcomingEvents into Dashboard.jsx

---

## 🔧 Required Action: Apply Database Migration

To activate the Events feature, you need to apply the database migration:

### Option 1: Using PowerShell (Recommended)

```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Apply migration
python -m alembic upgrade head

# Restart backend server (if running)
```

### Option 2: From VS Code Terminal

1. Open a new PowerShell terminal in VS Code
2. Navigate to the backend folder
3. Activate the virtual environment
4. Run: `python -m alembic upgrade head`

### Verification

After applying the migration, you should see:
- ✅ A new `events` table in your database
- ✅ The backend server restarts without errors
- ✅ New events endpoints available in Swagger UI at http://127.0.0.1:8000/api/docs

---

## 📝 Testing the Feature

### 1. Check API Endpoints (Swagger UI)

Visit: http://127.0.0.1:8000/api/docs

You should see new endpoints under "Events":
- `GET /api/v1/events/upcoming` - Get upcoming events
- `POST /api/v1/events` - Create event (admin only)
- `GET /api/v1/events` - Get all events
- `GET /api/v1/events/{id}` - Get event details
- `PUT /api/v1/events/{id}` - Update event (admin only)
- `DELETE /api/v1/events/{id}` - Delete event (admin only)

### 2. Create Test Events (Admin Only)

Use Swagger UI to create test events:

**Example: Committee Meeting**
```json
{
  "title": "Annual Committee Meeting held at 31 August",
  "description": "Discuss society maintenance and future plans",
  "event_type": "meeting",
  "venue": "Clubhouse Main Hall",
  "start_datetime": "2026-08-31T18:00:00",
  "end_datetime": "2026-08-31T20:00:00",
  "is_active": true
}
```

**Example: Festival Celebration**
```json
{
  "title": "Diwali Celebration 2026",
  "description": "Community Diwali celebration with cultural programs",
  "event_type": "festival",
  "venue": "Community Garden",
  "start_datetime": "2026-11-01T17:00:00",
  "end_datetime": "2026-11-01T22:00:00",
  "is_active": true
}
```

**Example: Maintenance Schedule**
```json
{
  "title": "Water Tank Cleaning",
  "description": "Annual water tank cleaning and sanitization",
  "event_type": "maintenance",
  "venue": "Building A, B, C Roof",
  "start_datetime": "2026-09-15T08:00:00",
  "end_datetime": "2026-09-15T16:00:00",
  "is_active": true
}
```

### 3. View Events on Dashboard

1. Refresh the frontend dashboard
2. The "Upcoming Events" widget should appear in the lower-left section
3. You should see the test events displayed with:
   - Event type badge with icon and color
   - Event title
   - Date and time
   - Venue

---

## 🎨 Event Type Colors

The events widget uses color-coding for different event types:

- 📋 **Meeting** - Blue (#1976d2)
- 🎉 **Festival** - Purple (#9c27b0)
- 🔧 **Maintenance** - Orange (#ff9800)
- 🎊 **Social** - Green (#4caf50)
- ⚽ **Sports** - Teal (#009688)
- 📅 **Other** - Gray (#757575)

---

## 🚀 Next Steps

After verifying the Events feature works:

1. **Step 2:** Implement Notices feature (Recent Notices widget for admins)
2. **Step 3:** Implement Payments feature (Payment Reminders widget for residents)
3. **Step 4:** Implement Pending Approvals widget (for admins)
4. **Step 5:** Add full Events management page

---

## 🐛 Troubleshooting

### Migration fails
- Ensure you're in the backend directory
- Verify virtual environment is activated
- Check that alembic is installed: `pip list | findstr alembic`
- If needed, reinstall: `pip install alembic`

### Events widget shows "Failed to load events"
- Verify backend server is running
- Check browser console for API errors
- Ensure migration was applied successfully
- Verify you're logged in

### No events showing
- Create test events using Swagger UI (admin account required)
- Events must have `is_active=true` and `start_datetime` in the future

---

## 📋 Implementation Checklist

- [x] Backend model created
- [x] Backend schema created
- [x] Backend service created
- [x] Backend API endpoints created
- [x] Database migration created
- [ ] **Database migration applied** ⬅️ **ACTION REQUIRED**
- [x] Frontend API client created
- [x] Frontend UpcomingEvents widget created
- [x] Dashboard integration complete
- [ ] Test events created
- [ ] Feature verified working

---

**Status:** Ready for testing after migration is applied ✅
