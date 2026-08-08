# Frontend Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- Backend API running on http://localhost:8000
- Git (optional)

---

## Setup Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
```

**Additional packages needed:**
```bash
npm install react-hook-form zod @hookform/resolvers react-toastify
```

### 2. Environment Configuration

Create `.env` file in `frontend/` directory:

```bash
# Copy from example
cp .env.example .env
```

**Default `.env` content:**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Riverdale Connect
VITE_APP_VERSION=1.0.0
VITE_ENV=development
```

### 3. Start Backend (Required)

The frontend needs the backend API running:

```bash
# In a separate terminal
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

uvicorn app.main:app --reload
```

Backend will run on: **http://localhost:8000**  
API docs available at: **http://localhost:8000/api/docs**

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will run on: **http://localhost:5173**

---

## First Time Usage

### 1. Register a New User

1. Navigate to http://localhost:5173
2. You'll be redirected to `/login`
3. Click **"Sign up"** to go to registration
4. Fill in the form:
   - **Name:** Your full name
   - **Email:** Valid email address
   - **Password:** Must meet requirements (8+ chars, uppercase, lowercase, number)
   - **Role:** Select RESIDENT, CONTRACTOR, or BUILDER
   - **Phone:** (Optional) 10-digit number
   - **Unit Number:** (Optional)
5. Click **"Create Account"**
6. You'll be redirected to login page

### 2. Login

1. Enter your email and password
2. Click **"Sign In"**
3. You'll be redirected to the dashboard

### 3. Explore

- **Dashboard:** Overview (placeholder)
- **Sidebar:** Navigation menu
- **User Menu:** Click your avatar (top-right)
- **Profile:** View your profile
- **Logout:** From user menu

---

## Available Routes

### Public Routes (No Auth Required)
- `/login` - Login page
- `/register` - Registration page
- `/forgot-password` - Password reset request
- `/reset-password` - Password reset (with token)

### Protected Routes (Auth Required)
- `/dashboard` - Main dashboard
- `/issues` - Issue list (placeholder)
- `/issues/new` - Create new issue (placeholder)
- `/profile` - User profile
- `/admin/users` - User management (admin only, placeholder)
- `/admin/reports` - Reports (admin only, placeholder)

---

## NPM Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

---

## Common Issues & Solutions

### Issue: npm not found
**Solution:** Install Node.js from https://nodejs.org

### Issue: Backend connection failed
**Solution:** 
1. Check backend is running on port 8000
2. Check `VITE_API_BASE_URL` in `.env`
3. Check CORS settings in backend

### Issue: Login fails
**Solution:**
1. Check backend is running
2. Verify user exists in database
3. Check browser console for errors
4. Check backend logs

### Issue: Port 5173 already in use
**Solution:**
```bash
# Kill process on Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3000
```

### Issue: White screen / blank page
**Solution:**
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Clear browser cache and reload

---

## Testing Accounts

After registration, you can create test accounts:

**Admin Account:**
- Email: admin@riverdale.com
- Password: Admin@123
- Role: ADMIN

**Resident Account:**
- Email: resident@riverdale.com
- Password: Resident@123
- Role: RESIDENT

**Contractor Account:**
- Email: contractor@riverdale.com
- Password: Contractor@123
- Role: CONTRACTOR

---

## File Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── api/            # API services
│   ├── components/     # React components
│   ├── constants/      # Constants
│   ├── hooks/          # Custom hooks
│   ├── pages/          # Page components
│   ├── store/          # Redux store
│   ├── utils/          # Utilities
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── theme.js        # MUI theme
├── .env                # Environment variables (create this)
├── .env.example        # Environment template
├── package.json        # Dependencies
└── vite.config.js      # Vite configuration
```

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

## Development Tips

### Hot Reload
- Changes to `.jsx` files auto-reload
- Changes to `.env` require restart

### Redux DevTools
Install Redux DevTools extension for debugging:
- Chrome: https://chrome.google.com/webstore/detail/redux-devtools
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/

### React DevTools
Install React DevTools for component inspection:
- Chrome: https://chrome.google.com/webstore/detail/react-developer-tools
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/react-devtools/

---

## Next Steps

1. **Explore the UI** - Navigate through all pages
2. **Test Authentication** - Login, logout, password reset
3. **Check Responsive Design** - Test on mobile sizes
4. **Review Code** - Understand the architecture
5. **Prepare for Phase 2** - Issue management features

---

## Need Help?

- **Documentation:** Check `PHASE1_IMPLEMENTATION.md`
- **Backend API:** http://localhost:8000/api/docs
- **Console Logs:** Check browser DevTools
- **Network Tab:** Monitor API calls

---

**Version:** 1.0.0  
**Last Updated:** 2024-07-23  
**Status:** Phase 1 Complete ✅
