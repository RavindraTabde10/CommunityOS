# Phase 2.3-2.5 Testing Guide

**Quick testing guide for Create Issue, Issue Detail, and Edit Issue features**

---

## ✅ Pre-Testing Checklist

1. Backend running on port 8000 ✅
2. Frontend running on port 5173 ✅
3. Logged in as a user ✅
4. No console errors ✅

---

## 🧪 Test Phase 2.3: Create Issue

### Test 1: Navigate to Create Issue

**Steps:**
1. Click sidebar "Create Issue" OR
2. Dashboard → Click "Create Issue" button OR
3. Navigate to http://localhost:5173/issues/new

**Expected:**
- ✅ Create Issue page loads
- ✅ Form displays with all fields
- ✅ "Back to Issues" button visible
- ✅ No errors in console

---

### Test 2: Form Validation - Required Fields

**Steps:**
1. Leave all fields empty
2. Click "Create Issue" button

**Expected:**
- ✅ Form does NOT submit
- ✅ Red error messages appear under required fields
- ✅ Title error: "Title must be at least 10 characters"
- ✅ Description error: "Description must be at least 20 characters"
- ✅ Category error: "Category is required"

---

### Test 3: Form Validation - Minimum Length

**Steps:**
1. Title: Type "Short" (5 chars)
2. Description: Type "Too short" (9 chars)
3. Category: Select "Electrical"
4. Priority: Leave as "Medium"
5. Click "Create Issue"

**Expected:**
- ✅ Title error: "Title must be at least 10 characters"
- ✅ Description error: "Description must be at least 20 characters"

---

### Test 4: Form Validation - Maximum Length

**Steps:**
1. Title: Type 201 characters
2. Description: Type normally (valid)
3. Category: Select any
4. Click "Create Issue"

**Expected:**
- ✅ Title error: "Title must not exceed 200 characters"
- ✅ Character counter would be helpful (future enhancement)

---

### Test 5: Valid Issue Creation (No Photos)

**Steps:**
1. Title: "Water leakage in bathroom ceiling"
2. Description: "There is water dripping from the bathroom ceiling, possibly from the flat above. The leak started yesterday evening."
3. Category: "Plumbing"
4. Priority: "High"
5. Location: "Building A, 3rd Floor"
6. Unit Number: "A-301"
7. Click "Create Issue"

**Expected:**
- ✅ "Create Issue" button shows "Saving..."
- ✅ Toast notification: "Issue created successfully!"
- ✅ Redirect to issue detail page
- ✅ Issue displays correctly
- ✅ All fields populated

---

### Test 6: Photo Upload - Select Photos

**Steps:**
1. Fill form with valid data
2. Click "Upload Photos" button
3. Select 2-3 images from your computer

**Expected:**
- ✅ Photo preview grid appears
- ✅ Each photo shows thumbnail
- ✅ Photo names displayed
- ✅ Delete button on each photo
- ✅ Upload count shows (e.g., "3 photos")

---

### Test 7: Photo Upload - Remove Photo

**Steps:**
1. Upload 3 photos
2. Click delete button on middle photo

**Expected:**
- ✅ Photo removed from preview
- ✅ Count updates to 2 photos
- ✅ Other photos remain

---

### Test 8: Photo Upload - Size Validation

**Steps:**
1. Try to upload a file larger than 5MB

**Expected:**
- ✅ Error message: "Each file must be under 5MB"
- ✅ Photo not added to preview

---

### Test 9: Photo Upload - Maximum Count

**Steps:**
1. Try to upload 11 photos

**Expected:**
- ✅ Error message: "Maximum 10 photos allowed"
- ✅ Only first 10 photos added

---

### Test 10: Create Issue with Photos

**Steps:**
1. Fill form with valid data
2. Upload 2-3 photos
3. Click "Create Issue"

**Expected:**
- ✅ Issue created successfully
- ✅ Photos uploaded
- ✅ Redirect to detail page
- ✅ Photos display in gallery

---

## 🧪 Test Phase 2.4: Issue Detail

### Test 11: View Issue Detail

**Steps:**
1. From issue list, click any issue card

**Expected:**
- ✅ Issue detail page loads
- ✅ Issue number displayed at top
- ✅ Title large and bold
- ✅ Description shows full text
- ✅ Status badge (colored)
- ✅ Priority badge (colored)
- ✅ Category chip
- ✅ Location displays (if set)
- ✅ Unit number displays (if set)
- ✅ Created date formatted nicely
- ✅ "Back to Issues" button works

---

### Test 12: Photo Gallery

**Steps:**
1. View issue with photos

**Expected:**
- ✅ "Photos (X)" section displays
- ✅ Photos in grid (4 columns desktop, 2 mobile)
- ✅ Each photo clickable
- ✅ Hover effect on photos

---

### Test 13: Photo Lightbox

**Steps:**
1. Click any photo in gallery

**Expected:**
- ✅ Lightbox opens (full-screen dialog)
- ✅ Photo displays full-size
- ✅ Close button (X) in top-right
- ✅ Click outside to close
- ✅ Clicking X closes lightbox

---

### Test 14: Edit Button Visibility

**Steps:**
1. View YOUR OWN issue
2. Check for Edit button

**Expected:**
- ✅ Edit button visible in top-right
- ✅ Delete button visible

**Steps:**
1. View SOMEONE ELSE'S issue (if available)

**Expected:**
- ✅ Edit/Delete buttons NOT visible (unless you're admin)

---

### Test 15: Delete Issue

**Steps:**
1. View your own issue
2. Click "Delete" button

**Expected:**
- ✅ Confirmation dialog appears
- ✅ Dialog title: "Delete Issue?"
- ✅ Warning message
- ✅ Cancel and Delete buttons

**Steps:**
1. Click "Delete"

**Expected:**
- ✅ Issue deleted
- ✅ Toast: "Issue deleted successfully"
- ✅ Redirect to issue list
- ✅ Issue no longer in list

---

## 🧪 Test Phase 2.5: Edit Issue

### Test 16: Navigate to Edit

**Steps:**
1. View your own issue
2. Click "Edit" button

**Expected:**
- ✅ Edit page loads
- ✅ Form pre-populated with existing data
- ✅ Title field has original title
- ✅ Description has original text
- ✅ Category selected correctly
- ✅ Priority selected correctly
- ✅ Location filled (if set)
- ✅ Unit number filled (if set)
- ✅ "Back to Issue" button visible
- ✅ Submit button says "Update Issue"

---

### Test 17: Edit Issue - Change Title

**Steps:**
1. Change title to "Updated: [original title]"
2. Click "Update Issue"

**Expected:**
- ✅ Button shows "Saving..."
- ✅ Toast: "Issue updated successfully!"
- ✅ Redirect to detail page
- ✅ New title displays

---

### Test 18: Edit Issue - Change Multiple Fields

**Steps:**
1. Change title
2. Change description
3. Change priority
4. Click "Update Issue"

**Expected:**
- ✅ All changes saved
- ✅ Detail page shows updated values

---

### Test 19: Edit Issue - Add Photos

**Steps:**
1. Open edit page
2. Upload 2 new photos
3. Click "Update Issue"

**Expected:**
- ✅ Issue updated
- ✅ New photos uploaded
- ✅ Old photos remain (not replaced)
- ✅ Detail page shows all photos

---

### Test 20: Edit Issue - Validation

**Steps:**
1. Change title to 5 characters
2. Click "Update Issue"

**Expected:**
- ✅ Validation error
- ✅ Form does not submit
- ✅ Error message displays

---

### Test 21: Edit Someone Else's Issue

**Steps:**
1. Try to navigate to /issues/{someone-else-id}/edit directly in URL

**Expected:**
- ✅ Error message: "You do not have permission to edit this issue"
- ✅ Form not displayed
- ✅ Back button available

---

## 🧪 Integration Tests

### Test 22: Full Workflow

**Steps:**
1. Create issue with photos
2. View issue detail
3. Edit issue (change title, add photo)
4. View updated issue
5. Delete issue

**Expected:**
- ✅ All steps complete successfully
- ✅ Data consistent throughout
- ✅ No errors at any step

---

### Test 23: Navigation Flow

**Steps:**
1. Dashboard → Create Issue → Create → Detail → Back to Issues → List
2. Dashboard → Recent Issue Card → Detail → Edit → Update → Detail
3. Sidebar → Create Issue → Back → My Issues → Issue Card → Detail

**Expected:**
- ✅ All navigation works
- ✅ No broken links
- ✅ Browser back button works

---

### Test 24: Error Handling - Network

**Steps:**
1. Stop backend server
2. Try to create issue

**Expected:**
- ✅ Error toast appears
- ✅ Form does not submit
- ✅ User stays on page
- ✅ Can retry after backend restarts

---

### Test 25: Error Handling - Invalid Data

**Steps:**
1. Use browser DevTools to modify form
2. Send invalid category value
3. Submit form

**Expected:**
- ✅ Backend returns error
- ✅ Frontend displays error message
- ✅ No app crash

---

## 🧪 Responsive Design Tests

### Test 26: Mobile View (375px)

**Steps:**
1. Open DevTools
2. Set viewport to iPhone SE (375px)
3. Test create issue form

**Expected:**
- ✅ Form fields full-width
- ✅ All inputs accessible
- ✅ Dropdowns work on mobile
- ✅ Photo upload works
- ✅ Buttons full-width

---

### Test 27: Tablet View (768px)

**Steps:**
1. Set viewport to iPad (768px)
2. Test issue detail

**Expected:**
- ✅ Layout adapts
- ✅ Photo grid 2-3 columns
- ✅ Buttons appropriately sized
- ✅ No horizontal scroll

---

### Test 28: Desktop View (1920px)

**Steps:**
1. Set viewport to desktop
2. Test all pages

**Expected:**
- ✅ Content centered in container
- ✅ Photo grid 4 columns
- ✅ Forms not too wide (max 600px)
- ✅ Good spacing and padding

---

## 🧪 Accessibility Tests

### Test 29: Keyboard Navigation

**Steps:**
1. Use Tab key to navigate form
2. Use Enter to submit
3. Use Escape to close dialogs

**Expected:**
- ✅ All fields reachable with Tab
- ✅ Focus indicators visible
- ✅ Enter submits form
- ✅ Escape closes lightbox/dialogs

---

### Test 30: Screen Reader

**Steps:**
1. Use screen reader (NVDA/JAWS/VoiceOver)
2. Navigate create issue form

**Expected:**
- ✅ Labels read correctly
- ✅ Error messages announced
- ✅ Helper text accessible
- ✅ Buttons have clear labels

---

## 🐛 Common Issues & Solutions

### Issue: Photos not uploading

**Check:**
- File size under 5MB?
- Image format (jpg, png, etc.)?
- Backend S3/storage configured?
- Network tab shows upload request?

### Issue: Form validation not working

**Check:**
- Browser console for errors?
- Zod schema imported correctly?
- React Hook Form configured?

### Issue: Permission errors

**Check:**
- User logged in?
- Token valid (not expired)?
- User ID matches issue owner?

### Issue: Photos not displaying

**Check:**
- Photo URLs valid?
- CORS headers correct?
- Image file still exists?
- Network tab shows image requests?

---

## ✅ Test Results Checklist

Record your findings:

**Phase 2.3: Create Issue**
- [ ] Form loads correctly
- [ ] Validation works (required, min/max)
- [ ] All fields functional
- [ ] Photo upload works
- [ ] Issue creation succeeds
- [ ] Redirect works
- [ ] Error handling works

**Phase 2.4: Issue Detail**
- [ ] Detail view loads
- [ ] All fields display
- [ ] Photo gallery works
- [ ] Lightbox works
- [ ] Edit button shows (permission)
- [ ] Delete works with confirmation
- [ ] Back navigation works

**Phase 2.5: Edit Issue**
- [ ] Edit form loads
- [ ] Pre-population works
- [ ] Changes save correctly
- [ ] Photo addition works
- [ ] Validation works
- [ ] Permission checks work
- [ ] Redirect works

**Integration:**
- [ ] Full workflow works
- [ ] Navigation consistent
- [ ] Error handling robust
- [ ] Responsive on all devices
- [ ] No console errors

---

## 🎯 Success Criteria

**Phase 2.3-2.5 is successful if:**

✅ Users can create issues with all fields  
✅ Photo upload works (up to 10, 5MB each)  
✅ Form validation prevents invalid data  
✅ Issue detail shows complete information  
✅ Photo gallery and lightbox functional  
✅ Edit button shows for owners/admins only  
✅ Edit form pre-populates correctly  
✅ Updates save successfully  
✅ Delete works with confirmation  
✅ Permission checks enforce access control  
✅ Navigation flows smoothly  
✅ Error handling is graceful  
✅ Responsive design works  
✅ No console errors  
✅ Performance is smooth

---

**Happy Testing! 🧪**

Found issues? Document them and we'll fix before moving to Phase 3.
