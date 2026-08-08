# Phase 3: Enhanced Features - Testing Guide

**Date:** 2026-07-28  
**Status:** Ready for Testing  
**Components:** Comments, Activity Timeline, Profile Management

---

## 🚀 Quick Start

### Prerequisites
1. Backend server running on `http://127.0.0.1:8000`
2. Frontend dev server running on `http://localhost:5173`
3. User account created and logged in

### Start Servers

**Terminal 1 - Backend:**
```powershell
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## 🧪 Testing Scenarios

### 1. Comments System Testing

#### Test 1.1: Add Comment
1. Navigate to any issue detail page
2. Scroll to Comments section
3. Type a comment in the text field
4. Verify character counter updates
5. Click "Comment" button
6. ✅ Verify comment appears in list
7. ✅ Verify "just now" timestamp
8. ✅ Verify success toast notification

#### Test 1.2: Edit Comment
1. Hover over your own comment
2. Click Edit icon (pencil)
3. Modify the comment text
4. Click "Save"
5. ✅ Verify comment updates
6. ✅ Verify "Edited" badge appears
7. ✅ Verify success toast

#### Test 1.3: Delete Comment
1. Click Delete icon (trash) on your comment
2. Confirm deletion in dialog
3. ✅ Verify comment is removed
4. ✅ Verify success toast

#### Test 1.4: Character Limit
1. Type more than 2000 characters
2. ✅ Verify character count turns red
3. ✅ Verify "Comment" button is disabled
4. ✅ Verify validation error shows

#### Test 1.5: Permissions
1. Login as different user
2. View issue with comments
3. ✅ Verify can only edit/delete own comments
4. Login as admin
5. ✅ Verify admin can delete any comment

#### Test 1.6: Empty State
1. View issue with no comments
2. ✅ Verify empty state message shows
3. ✅ Verify "Be the first to comment!" text

---

### 2. Activity Timeline Testing

#### Test 2.1: View Timeline
1. Navigate to any issue detail page
2. Scroll to Activity Timeline section
3. ✅ Verify timeline shows in chronological order
4. ✅ Verify icons display for each activity type
5. ✅ Verify connecting lines between items

#### Test 2.2: Activity Types
1. Create a new issue
2. ✅ Verify "Issue created" activity with green icon
3. Edit the issue
4. ✅ Verify "Issue updated" activity with blue icon
5. Add a comment
6. ✅ Verify "Comment added" activity with primary icon
7. Upload a photo
8. ✅ Verify "Photo uploaded" activity

#### Test 2.3: Field Changes
1. Edit an issue and change status
2. View activity timeline
3. ✅ Verify old value shown with strikethrough
4. ✅ Verify arrow between old and new
5. ✅ Verify new value shown in chip

#### Test 2.4: Timestamps
1. Check activity timestamps
2. ✅ Verify relative format (e.g., "2 hours ago")
3. Wait and refresh
4. ✅ Verify timestamps update correctly

---

### 3. Profile Management Testing

#### Test 3.1: View Profile
1. Click on "Profile" in sidebar
2. ✅ Verify large avatar displays
3. ✅ Verify name and role shown
4. ✅ Verify "Member since" displays
5. ✅ Verify all info fields show correctly
6. ✅ Verify Edit and Change Password buttons

#### Test 3.2: Edit Profile
1. Click "Edit Profile" button
2. ✅ Verify form pre-populates with current data
3. Change name to "Test User Updated"
4. Change phone to "+1234567890"
5. Change unit_number to "B-202"
6. Click "Save Changes"
7. ✅ Verify success toast
8. ✅ Verify redirected to profile page
9. ✅ Verify changes reflected immediately
10. ✅ Verify name in app bar updates

#### Test 3.3: Edit Profile - Read-only Fields
1. Click "Edit Profile"
2. ✅ Verify email field is disabled
3. ✅ Verify role field is disabled
4. ✅ Verify helper text shows "cannot be changed"

#### Test 3.4: Edit Profile - Validation
1. Click "Edit Profile"
2. Clear name field
3. Try to save
4. ✅ Verify validation error shows
5. Enter invalid phone (e.g., "abc")
6. ✅ Verify validation error shows
7. Enter valid data and save
8. ✅ Verify saves successfully

#### Test 3.5: Change Password
1. Click "Change Password" button
2. Enter current password: (your password)
3. Enter new password: "NewPassword123"
4. Enter confirm password: "NewPassword123"
5. ✅ Verify password strength indicator shows
6. ✅ Verify strength changes (weak → medium → strong)
7. ✅ Verify progress bar color changes
8. Click "Change Password"
9. ✅ Verify success toast
10. Logout
11. Login with new password
12. ✅ Verify login successful
13. Try login with old password
14. ✅ Verify login fails

#### Test 3.6: Change Password - Validation
1. Click "Change Password"
2. Enter mismatched passwords
3. ✅ Verify "Passwords don't match" error
4. Enter weak password (e.g., "abc")
5. ✅ Verify validation errors show
6. ✅ Verify strength indicator shows "Weak" in red

#### Test 3.7: Password Visibility Toggle
1. In Change Password form
2. Click eye icon on current password
3. ✅ Verify password becomes visible
4. Click again
5. ✅ Verify password hidden
6. Repeat for new password and confirm password fields

---

## 📱 Responsive Testing

### Desktop (1024px+)
- [ ] Comments display in full width
- [ ] Activity timeline has proper spacing
- [ ] Profile info in 2-column grid
- [ ] All buttons properly sized

### Tablet (768px-1023px)
- [ ] Comments maintain readability
- [ ] Activity timeline adapts
- [ ] Profile info in 2-column grid
- [ ] Navigation accessible

### Mobile (320px-767px)
- [ ] Comments stack vertically
- [ ] Edit/delete buttons not cut off
- [ ] Activity timeline compact but readable
- [ ] Profile info in single column
- [ ] Forms fill screen width
- [ ] Keyboard doesn't obscure inputs

---

## 🐛 Known Issues to Watch For

### Comments
- [ ] Check for duplicate comment IDs
- [ ] Verify pagination if > 50 comments
- [ ] Check comment refresh after edit
- [ ] Verify comment ordering (newest first)

### Activity Timeline
- [ ] Check for duplicate activities
- [ ] Verify all activity types have icons
- [ ] Check field change display for all fields
- [ ] Verify timeline doesn't break with long descriptions

### Profile
- [ ] Check profile refresh after update
- [ ] Verify phone validation accepts international formats
- [ ] Check password change with special characters
- [ ] Verify token doesn't expire during profile edit

---

## ✅ Success Criteria

### Functionality
- ✅ All CRUD operations work for comments
- ✅ Activity timeline displays all events correctly
- ✅ Profile updates save successfully
- ✅ Password changes work and are validated
- ✅ Permissions enforced correctly

### User Experience
- ✅ Clear feedback for all actions (toasts)
- ✅ Loading states show during operations
- ✅ Error messages are helpful
- ✅ Forms validate in real-time
- ✅ Navigation is intuitive

### Performance
- ✅ Comments load in < 1 second
- ✅ Activity timeline loads in < 1 second
- ✅ No lag when typing comments
- ✅ No console errors or warnings

### Design
- ✅ Consistent with existing UI
- ✅ Responsive on all devices
- ✅ Proper spacing and alignment
- ✅ Icons are meaningful and clear

---

## 🔧 Troubleshooting

### Comments Not Loading
1. Check backend is running
2. Check browser console for errors
3. Verify issue ID is correct
4. Check network tab for 404/500 errors

### Cannot Edit/Delete Comments
1. Verify you own the comment
2. Check user role (admin can delete all)
3. Check token is valid (not expired)
4. Check backend permissions

### Profile Update Not Saving
1. Check form validation passes
2. Check backend is running
3. Check network tab for error response
4. Verify token is valid

### Password Change Fails
1. Verify current password is correct
2. Check new password meets requirements
3. Check passwords match
4. Check backend validation response

---

## 📊 Test Results Template

```
Date: ____________________
Tester: __________________
Browser: _________________

Comments System:
[ ] Add comment: ___________
[ ] Edit comment: __________
[ ] Delete comment: ________
[ ] Character limit: _______
[ ] Permissions: ___________
[ ] Empty state: ___________

Activity Timeline:
[ ] View timeline: _________
[ ] Activity types: ________
[ ] Field changes: _________
[ ] Timestamps: ____________

Profile Management:
[ ] View profile: __________
[ ] Edit profile: __________
[ ] Change password: _______
[ ] Validation: ____________
[ ] Password strength: _____

Responsive:
[ ] Desktop: _______________
[ ] Tablet: ________________
[ ] Mobile: ________________

Overall: [ ] PASS [ ] FAIL
Notes: _____________________
____________________________
____________________________
```

---

## 🚀 Next Steps After Testing

1. Fix any bugs found
2. Optimize performance if needed
3. Complete Phase 3.4 (Photo Gallery)
4. Run final testing checklist
5. Update documentation
6. Proceed to Phase 4

---

**Testing Guide Version:** 1.0  
**Last Updated:** 2026-07-28  
**For:** Phase 3 - Enhanced Features
