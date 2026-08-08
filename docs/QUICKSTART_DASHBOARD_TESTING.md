# Quick Start: Testing Dashboard Redesign

**Feature:** Society-Focused Dashboard with Committee Members  
**Status:** ✅ Implementation Complete - Ready for Testing

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Apply Database Migration

The backend server is currently running. You need to apply the migration:

**Option A: Stop backend and run migration**
```bash
# Stop the uvicorn server (Ctrl+C in the uvicorn terminal)
cd backend
alembic upgrade head
# Restart backend
uvicorn app.main:app --reload
```

**Option B: Use a new terminal (recommended)**
```bash
cd backend
# On Windows cmd (if PowerShell execution policy blocks):
python -m alembic upgrade head

# Or try activating venv first:
.venv\Scripts\activate
alembic upgrade head
```

### Step 2: Verify Migration Applied
Check for success message:
```
INFO  [alembic.runtime.migration] Running upgrade 5764acf143c7 -> 8c9d0e1f2g3h, add_committee_members_table
```

### Step 3: Refresh Frontend
Open browser: http://localhost:5173
- Hard refresh (Ctrl+F5 or Ctrl+Shift+R)
- Should see new dashboard layout

---

## 🧪 What You Should See

### ✅ New Dashboard Layout:
1. **Welcome Header**
   - "Welcome to Riverdale Connect!"
   - Your name and unit number

2. **Announcement Marquee**
   - Your existing announcement should still be scrolling

3. **Community Overview** (4 stats cards)
   - 👥 Total Residents
   - 🏠 Total Units (100)
   - 🐛 Active Issues
   - ✅ Resolved Issues

4. **Committee Members Section**
   - Empty state: "No committee members assigned yet."
   - This is expected - you haven't added any members yet!

5. **Quick Actions**
   - Same as before (Create Issue, View All Issues)

6. **Recent Activity**
   - Your recent issues (reduced from 5 to 4)

---

## 👥 Adding Your First Committee Member

### Using Swagger UI:

1. Open: http://127.0.0.1:8000/api/docs

2. Scroll to **"Committee"** section

3. Click **POST /api/v1/committee** → "Try it out"

4. Replace the request body with:
```json
{
  "user_id": 1,
  "role": "president",
  "position_name": "Society President",
  "responsibilities": "Oversees all society operations and community welfare",
  "contact_email": "president@riverdale.com",
  "contact_phone": "+91-9876543210",
  "display_order": 1,
  "term_start_date": "2026-01-01T00:00:00",
  "term_end_date": "2027-12-31T23:59:59"
}
```

5. Click **Execute**

6. Should get **201 Created** response

7. **Refresh your dashboard** - you should now see 1 committee member card!

---

## 📊 Test Different Committee Roles

Add more members with different roles:

### Secretary:
```json
{
  "user_id": 2,
  "role": "secretary",
  "position_name": "Society Secretary",
  "responsibilities": "Maintains records and handles correspondence",
  "contact_email": "secretary@riverdale.com",
  "contact_phone": "+91-9876543211",
  "display_order": 2
}
```

### Treasurer:
```json
{
  "user_id": 3,
  "role": "treasurer",
  "position_name": "Society Treasurer",
  "responsibilities": "Manages finances and accounts",
  "contact_email": "treasurer@riverdale.com",
  "contact_phone": "+91-9876543212",
  "display_order": 3
}
```

### Vice President:
```json
{
  "user_id": 4,
  "role": "vice_president",
  "position_name": "Vice President",
  "responsibilities": "Assists president and manages events",
  "contact_email": "vp@riverdale.com",
  "contact_phone": "+91-9876543213",
  "display_order": 4
}
```

**Note:** Make sure the `user_id` values correspond to actual users in your database.

---

## 🎨 What to Test

### Visual Testing:
- [ ] Committee member cards display with avatars
- [ ] Role badges show correct emojis (👑, 📝, 💰, etc.)
- [ ] Hover effects work (card lifts up)
- [ ] Contact buttons appear if email/phone provided
- [ ] Community stats show correct numbers
- [ ] Layout is responsive (resize browser window)

### Functional Testing:
- [ ] Click email button → Opens email client
- [ ] Click phone button → Opens phone dialer
- [ ] Load dashboard → No console errors
- [ ] Refresh page → Data persists
- [ ] Empty committee → Shows "No committee members" message

### Mobile Testing:
- [ ] Resize to mobile width (< 600px)
- [ ] Committee cards stack vertically
- [ ] Stats cards stack (2x2 grid)
- [ ] All text readable
- [ ] No horizontal scroll

---

## 🐛 Troubleshooting

### Migration Error: "alembic: command not found"
**Solution:** Make sure you're in the backend directory and virtual environment is activated.

### Frontend Error: "committeeService is not defined"
**Solution:** Hard refresh browser (Ctrl+F5). Vite should hot-reload automatically.

### No Committee Members Showing
**Solution:** 
1. Check Swagger UI: GET /api/v1/committee/active
2. Verify members were created successfully
3. Check browser console for API errors
4. Verify backend is running on port 8000

### Stats Show 0 for Everything
**Solution:** This is normal if you have no users/issues. Create some test data:
1. Register a few users
2. Create some issues
3. Resolve some issues
4. Refresh dashboard

### Backend 500 Error
**Solution:** 
1. Check backend terminal for error details
2. Most likely: Migration not applied
3. Run: `alembic upgrade head`

---

## ✅ Success Checklist

After testing, you should have:
- [x] Dashboard loads without errors
- [x] Community statistics visible
- [x] Committee members section exists
- [x] At least 1 committee member added
- [x] Committee member card displays correctly
- [x] Contact buttons work
- [x] Responsive design verified
- [x] No console errors

---

## 📸 Expected Screenshots

### Desktop View:
```
┌─────────────────────────────────────────────────────────┐
│  Welcome to Riverdale Connect!                          │
│  Hello, [Your Name]                                     │
│  Role: admin • Unit: 404                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  📢 [Scrolling Announcement]                            │
└─────────────────────────────────────────────────────────┘

📊 Community Overview
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 👥 Total     │ 🏠 Total     │ 🐛 Active    │ ✅ Resolved  │
│ Residents    │ Units        │ Issues       │ Issues       │
│      5       │    100       │      1       │      0       │
└──────────────┴──────────────┴──────────────┴──────────────┘

🏛️ Committee Members
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   [Avatar]   │   [Avatar]   │   [Avatar]   │   [Avatar]   │
│  President   │  Secretary   │  Treasurer   │ Vice Pres.   │
│  📧 📞       │  📧 📞       │  📧 📞       │  📧 📞       │
└──────────────┴──────────────┴──────────────┴──────────────┘

[Create Issue] [View All Issues]

🔔 Recent Activity
┌─────────────────────────────────────────────────────────┐
│  RGTS-00001 - Issue with flat 404 leakage              │
│  Status: OPEN | Priority: HIGH | 2 days ago            │
└─────────────────────────────────────────────────────────┘
```

---

## 🎉 Next Steps After Testing

Once you've verified everything works:

1. **Add More Committee Members**
   - Assign real users to committee roles
   - Use actual email addresses
   - Add real phone numbers

2. **Customize Labels**
   - Edit `constants/committee.js` to change role labels
   - Modify emoji icons if needed

3. **Future Enhancements**
   - Build admin UI for committee management
   - Add committee member photos/avatars
   - Add term expiration notifications
   - Add committee meeting schedules

4. **Move to Next Feature**
   - Asset management (Phase 4)
   - Reports & analytics (Phase 5)
   - Admin features (Phase 6)

---

## 📞 Need Help?

If you encounter issues:
1. Check the detailed [DASHBOARD_REDESIGN_IMPLEMENTATION_SUMMARY.md](./DASHBOARD_REDESIGN_IMPLEMENTATION_SUMMARY.md)
2. Review the original plan: [DASHBOARD_REDESIGN_PLAN.md](./DASHBOARD_REDESIGN_PLAN.md)
3. Check backend terminal for error logs
4. Check browser console for frontend errors
5. Verify both servers are running (uvicorn on 8000, vite on 5173)

---

**Happy Testing! 🚀**

**Remember:** This is a MAJOR improvement - your dashboard is now a community hub, not just an issue tracker!
