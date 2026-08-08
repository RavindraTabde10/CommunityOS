# Committee Admin UI - Quick Testing Guide

**Status:** ✅ Implementation Complete - Ready for Testing  
**Date:** 2026-07-29

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Refresh Frontend
The frontend should auto-reload, but if not:
- Go to browser: http://localhost:5173
- Press Ctrl+F5 (hard refresh)

### Step 2: Access Committee Management
1. Make sure you're logged in as **admin**
2. Look at the sidebar navigation
3. You should now see **"Committee"** menu item with 👥 icon
4. Click "Committee" → Opens `/admin/committee` page

### Step 3: First Look
You should see:
- **Page Header:** "Committee Management" with blue background
- **"Add Member" button** on the top right
- **Empty table** with message: "No committee members found"
- **Subtext:** "Click Add Member to create your first committee member"

---

## 🧪 Testing Scenario 1: Create Your First Committee Member

### Step 1: Open Create Dialog
1. Click **"Add Member"** button
2. Dialog opens: "➕ Add Committee Member"

### Step 2: Fill the Form
**Required fields:**
- **User:** Select yourself or any user from dropdown
- **Role:** Select "President" 
- **Position Name:** Enter "Society President"

**Optional fields (recommended):**
- **Responsibilities:** "Oversees all society operations"
- **Contact Email:** Your email
- **Contact Phone:** Your phone number
- **Display Order:** 1 (appears first)
- **Term Start Date:** Select today's date
- **Term End Date:** Select one year from now
- **Active:** Keep checkbox checked

### Step 3: Save
1. Click **"Add Member"** button
2. You should see:
   - ✅ Green notification: "Committee member added successfully"
   - Dialog closes
   - Table refreshes
   - One row appears with your data

### Step 4: Verify on Dashboard
1. Click "Dashboard" in sidebar
2. Scroll to **"Committee Members"** section
3. You should see **your committee member card** with:
   - Avatar with first letter
   - Name and unit
   - 👑 President badge
   - Position name
   - Email and phone buttons

---

## 🧪 Testing Scenario 2: Add Multiple Members

Add 3 more members with different roles:

### Member 2: Secretary
1. Click "Add Member"
2. Select user
3. Role: **Secretary**
4. Position: "Society Secretary"
5. Display Order: 2
6. Save

### Member 3: Treasurer
1. Click "Add Member"
2. Select user
3. Role: **Treasurer**
4. Position: "Society Treasurer"
5. Display Order: 3
6. Save

### Member 4: Vice President
1. Click "Add Member"
2. Select user
3. Role: **Vice President**
4. Position: "Vice President"
5. Display Order: 4
6. Save

**Result:** Table should now show 4 committee members with different role badges and emojis.

---

## 🧪 Testing Scenario 3: Edit a Member

### Edit the Secretary:
1. Find "Society Secretary" row in table
2. Click **Edit button (✏️)**
3. Dialog opens with pre-filled data
4. Notice: **User field is disabled** (cannot change user)
5. Change **Position Name** to "Chief Secretary"
6. Add **Responsibilities:** "Maintains all records"
7. Click **"Save Changes"**
8. You should see:
   - ✅ Green notification: "Committee member updated successfully"
   - Table refreshes with updated data
   - Position name changed to "Chief Secretary"

---

## 🧪 Testing Scenario 4: Toggle Active Status

### Make a Member Inactive:
1. Click Edit on any member
2. **Uncheck "Active"** checkbox
3. Save
4. Go to Dashboard
5. That member should **NOT appear** on dashboard anymore
6. Return to Committee Management
7. Table still shows the member with **"Inactive" gray chip**

### Make Member Active Again:
1. Click Edit on the inactive member
2. **Check "Active"** checkbox
3. Save
4. Go to Dashboard
5. Member should **reappear** on dashboard

---

## 🧪 Testing Scenario 5: Delete a Member

### Delete a Member:
1. Click **Delete button (🗑️)** on any member
2. **Confirmation dialog appears:**
   - ⚠️ Warning icon
   - "Confirm Deletion" title
   - Message: "Are you sure you want to remove [Name] from the committee?"
   - "This action cannot be undone"
3. Click **"Delete"** button (red)
4. You should see:
   - ✅ Green notification: "Committee member removed successfully"
   - Table refreshes
   - Member removed from table
5. Go to Dashboard
6. Member should be gone from dashboard too

---

## 🧪 Testing Scenario 6: Form Validation

### Test Required Fields:
1. Click "Add Member"
2. Click "Add Member" button **without filling form**
3. Should see error: "Please select a user"
4. Select user only
5. Click "Add Member" button
6. Should see error: "Please select a role"
7. Select role only
8. Click "Add Member" button
9. Should see error: "Position name is required"

### Test Email Validation:
1. Fill required fields
2. Enter **invalid email:** "notanemail"
3. Click "Add Member" button
4. Should see error: "Invalid email format"
5. Fix email or clear it
6. Save should work now

### Test Date Validation:
1. Fill required fields
2. Set **Term Start Date:** 2027-01-01
3. Set **Term End Date:** 2026-01-01 (before start!)
4. Click "Add Member" button
5. Should see error: "Term end date must be after start date"
6. Fix dates or clear them
7. Save should work now

---

## 🧪 Testing Scenario 7: Contact Buttons

### Test Email Button:
1. Make sure a member has contact email
2. Find member in table
3. Click **📧 Email icon** button
4. Should open your email client with "To:" pre-filled

### Test Phone Button:
1. Make sure a member has contact phone
2. Find member in table
3. Click **📞 Phone icon** button
4. Should trigger phone dialer (mobile) or show phone number (desktop)

### Test Missing Contact:
1. Edit a member
2. Clear both email and phone
3. Save
4. Table should show: "No contact info" text
5. No email/phone buttons

---

## 🧪 Testing Scenario 8: Access Control

### Test Non-Admin Access:
1. **Log out** (if you have another user)
2. **Log in as resident** (non-admin user)
3. Check sidebar
4. "Committee" menu item should **NOT be visible**
5. Try accessing directly: http://localhost:5173/admin/committee
6. Should be **redirected** to dashboard or login

### Test Admin Access:
1. Log in as **admin**
2. Sidebar shows "Committee" menu
3. Can access page normally
4. Can perform all CRUD operations

---

## 🧪 Testing Scenario 9: UI/UX

### Test Table Features:
- [ ] Row hover effect (row highlights on hover)
- [ ] Role badges show correct emojis
- [ ] Status chips show correct colors
- [ ] Avatar shows first letter
- [ ] Actions buttons clickable
- [ ] Scrolls if many members

### Test Dialogs:
- [ ] Dialog opens smoothly
- [ ] All fields render correctly
- [ ] Form is scrollable if needed
- [ ] Cancel button closes dialog
- [ ] X button closes dialog
- [ ] Clicking outside does NOT close (by default)

### Test Notifications:
- [ ] Success: Green with checkmark
- [ ] Error: Red with X
- [ ] Auto-closes after 6 seconds
- [ ] Can close manually
- [ ] Appears bottom-right

---

## 🧪 Testing Scenario 10: Responsive Design

### Test Desktop View:
1. Full screen browser
2. Table should show all columns clearly
3. Dialog should be centered
4. Buttons sized appropriately

### Test Tablet View:
1. Resize browser to ~768px width
2. Table still readable
3. Columns may stack
4. Dialog adapts

### Test Mobile View:
1. Resize browser to ~375px width
2. Table has horizontal scroll
3. Dialog is full-width
4. Buttons stack vertically
5. All text readable

---

## ✅ Success Checklist

After testing, verify all of these work:

### Create:
- [ ] Can open create dialog
- [ ] User dropdown populated
- [ ] Role dropdown has 5 options
- [ ] Required validation works
- [ ] Email validation works
- [ ] Date validation works
- [ ] Success notification shows
- [ ] Table refreshes
- [ ] Member appears on dashboard

### Edit:
- [ ] Can open edit dialog
- [ ] Form pre-filled with data
- [ ] User field disabled
- [ ] Can modify all other fields
- [ ] Validation works
- [ ] Success notification shows
- [ ] Table refreshes
- [ ] Dashboard updates

### Delete:
- [ ] Confirmation dialog appears
- [ ] Shows correct member name
- [ ] Cancel works
- [ ] Delete removes member
- [ ] Success notification shows
- [ ] Table refreshes
- [ ] Dashboard updates

### Navigation:
- [ ] "Committee" menu in admin sidebar
- [ ] Menu NOT visible for non-admins
- [ ] Clicking navigates correctly
- [ ] URL shows /admin/committee

### UI:
- [ ] Page header displays nicely
- [ ] Table renders correctly
- [ ] Empty state shows
- [ ] Loading state works
- [ ] Icons and badges correct
- [ ] Colors and styling good
- [ ] Responsive design works

---

## 🐛 If Something Doesn't Work

### Frontend Not Refreshing:
1. Press Ctrl+F5 (hard refresh)
2. Clear browser cache
3. Check browser console for errors
4. Check if frontend server running (port 5173)

### Menu Item Not Showing:
1. Make sure you're logged in as **admin**
2. Check user role in profile
3. Hard refresh browser
4. Check console for errors

### API Errors (500, 404):
1. Make sure backend server running (port 8000)
2. Check backend terminal for errors
3. Verify migration applied (committee_members table exists)
4. Check browser DevTools → Network tab for failed requests

### Dialog Not Opening:
1. Check browser console for JavaScript errors
2. Hard refresh browser
3. Check if component imported correctly

### Success, But No Data Showing:
1. Check if member is marked "Active"
2. Verify display_order is set
3. Check backend logs
4. Reload page

---

## 📸 What Success Looks Like

### Committee Management Page (With 4 Members):
```
┌─────────────────────────────────────────────────────────────────┐
│  🏛️ Committee Management                      [+ Add Member]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────┬─────────┬──────────┬──────────┬──────────┬────────┐  │
│  │Avatar│ Name    │ Role     │ Position │ Contact  │ Status │  │
│  ├──────┼─────────┼──────────┼──────────┼──────────┼────────┤  │
│  │  J   │ John    │ 👑 PRES │President │ 📧 📞   │ Active │  │
│  │      │ Smith   │          │          │          │ [✏️][🗑️]│  │
│  ├──────┼─────────┼──────────┼──────────┼──────────┼────────┤  │
│  │  S   │ Sarah   │ 📝 SEC  │Secretary │ 📧 📞   │ Active │  │
│  │      │ Jones   │          │          │          │ [✏️][🗑️]│  │
│  ├──────┼─────────┼──────────┼──────────┼──────────┼────────┤  │
│  │  M   │ Mike    │ 💰 TREAS│Treasurer │ 📧 📞   │ Active │  │
│  │      │ Taylor  │          │          │          │ [✏️][🗑️]│  │
│  ├──────┼─────────┼──────────┼──────────┼──────────┼────────┤  │
│  │  L   │ Lisa    │ 🥈 VP   │Vice Pres │ 📧      │ Active │  │
│  │      │ Brown   │          │          │          │ [✏️][🗑️]│  │
│  └──────┴─────────┴──────────┴──────────┴──────────┴────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard (Committee Members Section):
```
🏛️ Committee Members
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   [Avatar]   │   [Avatar]   │   [Avatar]   │   [Avatar]   │
│     John     │    Sarah     │     Mike     │     Lisa     │
│   Smith      │    Jones     │    Taylor    │    Brown     │
│              │              │              │              │
│ 👑 President │ 📝 Secretary │ 💰 Treasurer│ 🥈 Vice Pres │
│              │              │              │              │
│ Oversees all │ Maintains    │ Manages      │ Assists      │
│ operations   │ records      │ finances     │ president    │
│              │              │              │              │
│  📧 📞       │  📧 📞       │  📧 📞       │  📧          │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 🎉 You're All Set!

**Your committee management admin UI is fully functional!**

Enjoy managing your society committee with ease! 🚀

---

**Need Help?**
- Check [COMMITTEE_ADMIN_UI_IMPLEMENTATION_SUMMARY.md](./COMMITTEE_ADMIN_UI_IMPLEMENTATION_SUMMARY.md) for detailed documentation
- Review [COMMITTEE_ADMIN_UI_PLAN.md](./COMMITTEE_ADMIN_UI_PLAN.md) for architecture details
- Check browser console for any JavaScript errors
- Check backend terminal for API errors
