# Phase 1 Testing Guide - Riverdale Connect

**Purpose:** Verify all Phase 1 authentication features work correctly  
**Time Required:** 15-20 minutes  
**Status:** Ready for Testing

---

## 🚀 Quick Start Testing

### Prerequisites
- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:5173
- [ ] All npm packages installed

---

## Test 1: Registration Flow ✅

**URL:** http://localhost:5173/register

### Steps:
1. Navigate to registration page
2. Fill in the form:
   - **Name:** `Test User`
   - **Email:** `test@example.com`
   - **Password:** `Test1234`
   - **Confirm Password:** `Test1234`
   - **Role:** Select `RESIDENT`
   - **Phone:** `1234567890` (optional)
   - **Unit Number:** `A-101` (optional)
3. Click "Create Account"

### Expected Results:
- ✅ Form validates all fields
- ✅ Success toast notification appears
- ✅ Redirects to login page
- ✅ Can see "Account created successfully" message

### Test Validation Errors:
- Try empty email → "Email is required"
- Try invalid email → "Invalid email address"
- Try weak password → Password strength messages
- Try mismatched passwords → "Passwords don't match"

---

## Test 2: Login Flow ✅

**URL:** http://localhost:5173/login

### Steps:
1. Navigate to login page
2. Enter credentials:
   - **Email:** `test@example.com`
   - **Password:** `Test1234`
3. Click "Sign In"

### Expected Results:
- ✅ Loading spinner appears during login
- ✅ Success toast: "Login successful!"
- ✅ Redirects to `/dashboard`
- ✅ Can see user name in top-right corner
- ✅ Token stored in localStorage

### Verify Token Storage:
1. Open browser DevTools (F12)
2. Go to "Application" → "Local Storage" → http://localhost:5173
3. Check for `access_token` key
4. Check for `user` key with user data

### Test Invalid Login:
- Try wrong password → "Login failed" error
- Try non-existent email → "Login failed" error
- Verify error messages display clearly

---

## Test 3: Protected Routes ✅

### Test Authenticated Access:
1. While logged in, navigate to:
   - http://localhost:5173/dashboard ✅ Should work
   - http://localhost:5173/profile ✅ Should work

### Test Unauthenticated Access:
1. Click "Logout" from user menu
2. Try to access protected routes:
   - http://localhost:5173/dashboard → Redirects to `/login`
   - http://localhost:5173/profile → Redirects to `/login`

### Expected Results:
- ✅ Logged in users can access protected pages
- ✅ Logged out users redirected to login
- ✅ After login, redirects back to intended page

---

## Test 4: Navigation & Layout ✅

### AppBar:
- ✅ Logo/title visible in top-left
- ✅ Menu icon visible on mobile
- ✅ User menu in top-right

### Sidebar:
- ✅ Shows appropriate menu items based on role
- ✅ Active route highlighted
- ✅ Icons displayed correctly
- ✅ Collapses on mobile (< 600px)

### User Menu:
1. Click user avatar/name in top-right
2. Check dropdown shows:
   - User name
   - User email
   - "Profile" link
   - "Logout" button

### Test Menu Navigation:
- Click "Dashboard" → Goes to dashboard
- Click "Profile" → Goes to profile page
- Click each menu item to verify routing

---

## Test 5: Logout Flow ✅

### Steps:
1. Click user menu (top-right)
2. Click "Logout"

### Expected Results:
- ✅ Tokens cleared from localStorage
- ✅ Redirects to `/login`
- ✅ Cannot access protected routes
- ✅ Sidebar/AppBar no longer visible
- ✅ Success toast: "Logged out successfully"

### Verify Token Cleared:
1. Open DevTools (F12)
2. Application → Local Storage
3. Check `access_token` is removed
4. Check `user` is removed

---

## Test 6: Password Reset Flow ✅

### Forgot Password:
**URL:** http://localhost:5173/forgot-password

1. Enter email: `test@example.com`
2. Click "Send Reset Link"
3. Check backend logs for reset token

### Expected Results:
- ✅ Success message: "Password reset email sent"
- ✅ No errors in console
- ✅ Token generated in backend logs

### Reset Password (Manual Test):
**URL:** http://localhost:5173/reset-password?token=YOUR_TOKEN

1. Get reset token from backend logs
2. Navigate to reset password page with token
3. Enter new password: `NewTest1234`
4. Confirm password: `NewTest1234`
5. Click "Reset Password"

### Expected Results:
- ✅ Success message displayed
- ✅ Redirects to login
- ✅ Can login with new password
- ✅ Old password no longer works

---

## Test 7: Responsive Design ✅

### Desktop (> 960px):
- ✅ Sidebar always visible
- ✅ Full navigation menu
- ✅ Wide layout

### Tablet (600px - 960px):
- ✅ Sidebar toggleable
- ✅ Menu icon appears
- ✅ Content adapts to width

### Mobile (< 600px):
- ✅ Sidebar hidden by default
- ✅ Menu icon in AppBar
- ✅ Sidebar opens as drawer
- ✅ Touch interactions work
- ✅ Forms stack vertically
- ✅ Buttons full-width

### How to Test:
1. Open DevTools (F12)
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Try different screen sizes:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1920px)

---

## Test 8: Form Validation ✅

### Email Validation:
- Empty → "Email is required"
- Invalid format → "Invalid email address"
- Valid → No error

### Password Validation:
- Empty → "Password is required"
- < 8 chars → "Password must be at least 8 characters"
- No uppercase → "Must contain at least one uppercase letter"
- No lowercase → "Must contain at least one lowercase letter"
- No number → "Must contain at least one number"
- Valid → No error

### Name Validation:
- Empty → "Name is required"
- < 2 chars → "Name must be at least 2 characters"
- > 100 chars → "Name must not exceed 100 characters"
- Valid → No error

### Phone Validation (Optional):
- Invalid format → "Phone number must be 10 digits"
- Valid 10 digits → No error
- Empty → Allowed (optional)

---

## Test 9: Error Handling ✅

### Network Errors:
1. Stop backend server
2. Try to login
3. Expected: Toast error "Network error" or "Failed to login"

### API Errors:
1. Try to register with duplicate email
2. Expected: Error message from API
3. Verify error toast displays

### Token Expiration:
1. Login successfully
2. Manually clear `access_token` from localStorage
3. Try to access protected route
4. Expected: Redirects to login

---

## Test 10: Browser Compatibility ✅

Test the application in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Safari (latest, if available)

### Check:
- ✅ All features work
- ✅ No console errors
- ✅ Layout looks correct
- ✅ Forms work properly

---

## 🐛 Common Issues & Solutions

### Issue 1: Backend not running
**Symptom:** Network error on login  
**Solution:**
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Issue 2: CORS error
**Symptom:** CORS policy error in browser console  
**Solution:** Check backend `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue 3: Packages not installed
**Symptom:** Module not found errors  
**Solution:**
```bash
cd frontend
npm install
```

### Issue 4: Port already in use
**Symptom:** "Port 5173 is already in use"  
**Solution:**
```bash
# Kill the process or use different port
npm run dev -- --port 3000
```

### Issue 5: Token not persisting
**Symptom:** Logged out after refresh  
**Solution:** Check browser localStorage is enabled

---

## ✅ Test Results Checklist

After completing all tests, verify:

- [ ] ✅ Registration works with validation
- [ ] ✅ Login works and stores token
- [ ] ✅ Protected routes redirect correctly
- [ ] ✅ Navigation menu displays properly
- [ ] ✅ Logout clears session
- [ ] ✅ Password reset flow works
- [ ] ✅ Responsive on mobile/tablet/desktop
- [ ] ✅ Form validation works correctly
- [ ] ✅ Error handling displays messages
- [ ] ✅ No console errors or warnings

---

## 📊 Test Summary Template

After testing, document results:

```markdown
## Test Results - [Date]

**Tester:** [Your Name]
**Environment:** 
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Browser: [Chrome/Firefox/Safari]

### Passed Tests:
- [x] Registration flow
- [x] Login flow
- [x] Protected routes
- [x] Navigation
- [x] Logout
- [x] Password reset
- [x] Responsive design
- [x] Form validation
- [x] Error handling

### Failed Tests:
- [ ] None

### Bugs Found:
- None

### Notes:
All Phase 1 features working as expected!
```

---

## 🎯 Next Steps

After Phase 1 testing is complete:

1. **Fix any bugs found**
2. **Document issues in GitHub Issues**
3. **Proceed to Phase 2: Issue Management**
4. **Update IMPLEMENTATION_CHECKLIST.md**

---

## 📚 References

- [Phase 1 Status](./PHASE1_STATUS.md)
- [Frontend Development Plan](./FRONTEND_DEVELOPMENT_PLAN.md)
- [Backend API Documentation](../backend/API_README.md)
- [Quick Start Guide](./QUICKSTART_FRONTEND.md)

---

**Happy Testing! 🚀**
