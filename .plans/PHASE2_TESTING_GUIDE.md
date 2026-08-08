# Phase 2.1 & 2.2 Testing Guide

**Quick testing steps to verify the new dashboard and issue list functionality.**

---

## ✅ Pre-Testing Checklist

1. Backend running on port 8000 ✅
2. Frontend running on port 5173 ✅
3. Logged in as Test User ✅

---

## 🧪 Test Scenarios

### Test 1: Dashboard Statistics

**Steps:**
1. Navigate to http://localhost:5173/dashboard
2. Observe the statistics cards

**Expected Results:**
- ✅ Four statistics cards displayed
- ✅ Cards show: Total Issues, Open Issues, In Progress, Resolved
- ✅ Each card has an icon and colored background
- ✅ Cards lift on hover
- ✅ If no issues exist, all counts show 0

**What to Check:**
- Do the numbers look correct?
- Do the colors match status (Red=Open, Orange=InProgress, Green=Resolved)?
- Do cards respond to hover?

---

### Test 2: Recent Issues

**Steps:**
1. Scroll down to "Recent Issues" section on dashboard
2. Observe the issue cards

**Expected Results:**
- ✅ Shows up to 5 recent issues (if available)
- ✅ Each card shows: issue number, title, description, status, priority, category
- ✅ "View All" chip in header
- ✅ If no issues: "No issues found" message

**What to Check:**
- Can you read the issue information clearly?
- Are status badges color-coded?
- Does the date format look good?

---

### Test 3: Click Navigation

**Steps:**
1. On dashboard, click on an issue card
2. Should navigate to issue detail page

**Expected Results:**
- ✅ URL changes to /issues/:id
- ✅ Issue detail page loads (with placeholder message for now)
- ✅ "Back to Issues" button visible

**Steps:**
1. Click "Back to Issues" button

**Expected Results:**
- ✅ Returns to issue list page

---

### Test 4: Quick Actions

**Steps:**
1. On dashboard, find "Quick Actions" section
2. Click "Create Issue" button

**Expected Results:**
- ✅ Navigates to /issues/new
- ✅ Shows placeholder page (Phase 2.3 not implemented yet)

**Steps:**
1. Click browser back button
2. Click "View All Issues" button

**Expected Results:**
- ✅ Navigates to /issues
- ✅ Issue list page loads

---

### Test 5: Issue List Page

**Steps:**
1. Navigate to http://localhost:5173/issues
2. Observe the page layout

**Expected Results:**
- ✅ Title: "All Issues"
- ✅ Filter panel with Search, Status, Category dropdowns
- ✅ Issue count displayed (e.g., "Found 0 issue(s)")
- ✅ Issue cards in grid (2 columns on desktop)
- ✅ Empty state if no issues

**What to Check:**
- Is the layout responsive?
- Are filters visible and functional?

---

### Test 6: Search Functionality

**Steps:**
1. On issue list page, type in the search box
2. Try searching for issue title, description, or issue number

**Expected Results:**
- ✅ Issues filter in real-time as you type
- ✅ Issue count updates
- ✅ Shows "No issues found" if no matches

**Try:**
- Type a partial word
- Type an issue number
- Type a category name
- Clear the search

---

### Test 7: Status Filter

**Steps:**
1. Click the "Status" dropdown
2. Select "Open"

**Expected Results:**
- ✅ Only open issues displayed
- ✅ Issue count updates
- ✅ Filter persists during search

**Try:**
- Switch to "In Progress"
- Switch to "Resolved"
- Switch back to "All Status"

---

### Test 8: Category Filter

**Steps:**
1. Click the "Category" dropdown
2. Select a category (e.g., "Electrical")

**Expected Results:**
- ✅ Only issues with that category displayed
- ✅ Issue count updates
- ✅ Filters stack (status + category)

**Try:**
- Different categories
- Combine with status filter
- Combine with search

---

### Test 9: Combined Filtering

**Steps:**
1. Select Status: "Open"
2. Select Category: "Plumbing"
3. Type search: "leak"

**Expected Results:**
- ✅ Only open plumbing issues with "leak" in title/description
- ✅ All three filters active simultaneously
- ✅ Issue count accurate

---

### Test 10: Click-to-Filter from Dashboard

**Steps:**
1. Navigate to dashboard
2. Click on "Open Issues" card (red card)

**Expected Results:**
- ✅ Navigates to /issues?status=open
- ✅ Issue list shows only open issues
- ✅ Status filter pre-selected to "open"

**Try:**
- Click "In Progress" card
- Click "Resolved" card

---

### Test 11: Sidebar Navigation

**Steps:**
1. Click sidebar "My Issues" menu item

**Expected Results:**
- ✅ Navigates to /issues
- ✅ Menu item highlighted

**Steps:**
1. Click sidebar "Create Issue" menu item

**Expected Results:**
- ✅ Navigates to /issues/new
- ✅ Placeholder page shown

---

### Test 12: Responsive Design

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (mobile view)
3. Test on different sizes:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)

**Expected Results:**
- ✅ Dashboard cards stack on mobile (1 column)
- ✅ Issue cards stack on mobile (1 column)
- ✅ Filter dropdowns full width on mobile
- ✅ Sidebar becomes drawer on mobile
- ✅ Text readable at all sizes

---

### Test 13: Loading States

**Steps:**
1. Open browser DevTools
2. Go to Network tab
3. Set throttling to "Slow 3G"
4. Refresh dashboard

**Expected Results:**
- ✅ Skeleton loaders appear while loading
- ✅ Cards fade in when data arrives
- ✅ No flash of empty content
- ✅ Smooth transition

---

### Test 14: Error Handling

**Steps:**
1. Stop the backend server
2. Refresh the dashboard

**Expected Results:**
- ✅ Error toast notification appears
- ✅ Red alert banner with error message
- ✅ "Failed to load dashboard data" message
- ✅ No console errors causing app crash

**Steps:**
1. Start backend again
2. Refresh page

**Expected Results:**
- ✅ Data loads successfully
- ✅ Error cleared

---

### Test 15: Empty States

**Steps:**
1. Ensure database has no issues
2. Navigate to dashboard

**Expected Results:**
- ✅ All statistics show 0
- ✅ "No issues found. Create your first issue to get started!" message

**Steps:**
1. Navigate to /issues

**Expected Results:**
- ✅ "No issues found" message
- ✅ Helpful text: "Create your first issue to get started"

---

## 🐛 Common Issues & Solutions

### Issue: "No issues found" even though issues exist

**Solution:**
- Check backend is running: `netstat -ano | findstr :8000`
- Check browser console for API errors
- Verify API_BASE_URL in .env: `http://localhost:8000/api/v1`

### Issue: Statistics show 0 but issues exist in list

**Solution:**
- Check the status field values in database
- Verify status values match: 'open', 'in_progress', 'resolved', 'closed'

### Issue: Search not working

**Solution:**
- Search is case-insensitive and searches: title, description, issue_number
- Try typing slowly to see real-time filtering
- Check browser console for errors

### Issue: Click on issue card does nothing

**Solution:**
- Check browser console for routing errors
- Verify React Router is properly configured
- Check that IssueDetail page is imported in App.jsx

### Issue: 401 Unauthorized errors

**Solution:**
- Token may have expired
- Log out and log back in
- Check localStorage has 'access_token'

---

## ✅ Test Results

Record your findings:

- [ ] Dashboard loads with statistics
- [ ] Recent issues display correctly
- [ ] Navigation works (sidebar, cards, buttons)
- [ ] Issue list page functional
- [ ] Search filters issues in real-time
- [ ] Status filter works
- [ ] Category filter works
- [ ] Combined filters work
- [ ] Click-to-filter from dashboard works
- [ ] Responsive on mobile
- [ ] Loading states show
- [ ] Error handling works
- [ ] Empty states display
- [ ] No console errors

---

## 📸 Screenshots to Capture

If testing for documentation:

1. Dashboard with statistics (populated)
2. Dashboard with recent issues
3. Issue list page (grid view)
4. Issue list with filters applied
5. Empty state (no issues)
6. Mobile view (dashboard and list)
7. Loading state (skeleton loaders)

---

## 🎯 Success Criteria

**Phase 2.1 & 2.2 is successful if:**

✅ Dashboard shows real-time issue statistics  
✅ Recent issues display with proper formatting  
✅ Issue list page loads all issues  
✅ Search functionality filters correctly  
✅ Status and category filters work independently and combined  
✅ Navigation between pages works smoothly  
✅ Responsive design works on all screen sizes  
✅ Loading and error states handle gracefully  
✅ No console errors  
✅ Performance is smooth (no lag)

---

**Happy Testing! 🧪**

If you find any bugs or issues, please document them and we'll fix them before moving to Phase 2.3.
