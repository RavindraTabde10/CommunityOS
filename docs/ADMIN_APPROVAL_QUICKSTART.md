# Admin Approval - Quick Start Guide

## 🚀 Quick Setup

### 1. Create Initial Admin (One-Time Setup)
```bash
cd backend
.venv\Scripts\python.exe create_admin.py
```

Follow the prompts:
- **Email**: admin@riverdale.com (or your preferred email)
- **Name**: System Admin (or your preferred name)
- **Password**: Minimum 8 characters

---

## 📝 User Registration Flow

### New User Registration
1. User goes to `/register`
2. Sees notice: "All new registrations require admin approval"
3. Fills registration form with:
   - Full Name
   - Email (validated automatically)
   - Password (min 8 chars, uppercase, lowercase, number)
   - Role (Resident/Contractor/Builder)
   - Phone (optional)
   - Unit Number (optional)
4. Clicks "Create Account"
5. Sees success message: "Your account is pending admin approval"
6. **Status**: User created with `is_active=false`

### User Tries to Login
1. User enters email and password
2. Clicks "Login"
3. **Result**: Error message "Your account is pending approval"
4. User must wait for admin approval

---

## 👨‍💼 Admin Approval Process

### Step 1: Login as Admin
```
Email: admin@riverdale.com
Password: [Your admin password]
```

### Step 2: Navigate to Pending Approvals
- Click **"Pending Approvals"** in the sidebar
- Or go to: `/admin/pending-users`

### Step 3: Review Pending Users
You'll see a table with:
- Name
- Email
- Role
- Unit Number
- Phone
- Registration Date
- Actions (Approve/Reject)

### Step 4: Approve User
1. Click **"Approve"** button next to user
2. User is activated (`is_active=true`)
3. User removed from pending list
4. User can now login

---

## 🔧 API Testing with Swagger

### Open Swagger UI
```
http://127.0.0.1:8000/api/docs
```

### Test Registration
**Endpoint**: `POST /api/v1/auth/register`

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "Password123",
  "name": "New User",
  "role": "resident",
  "phone": "1234567890",
  "unit_number": "A-101"
}
```

**Response**: 200 OK (user created with `is_active=false`)

### Test Login (Should Fail)
**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "Password123"
}
```

**Response**: 403 Forbidden
```json
{
  "detail": "Your account is pending approval. Please contact an administrator or wait for approval."
}
```

### List Pending Users (Admin Only)
**Endpoint**: `GET /api/v1/users?is_active=false`

**Headers**: 
```
Authorization: Bearer {admin_access_token}
```

**Response**:
```json
{
  "users": [
    {
      "id": "user-uuid",
      "email": "newuser@example.com",
      "name": "New User",
      "role": "resident",
      "is_active": false,
      "created_at": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Approve User (Admin Only)
**Endpoint**: `PATCH /api/v1/users/{user_id}/status`

**Headers**: 
```
Authorization: Bearer {admin_access_token}
```

**Request**:
```json
{
  "is_active": true
}
```

**Response**: User object with `is_active=true`

### Test Login Again (Should Succeed)
**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "Password123"
}
```

**Response**: 200 OK with access token

---

## 🎯 Common Scenarios

### Scenario 1: First Time Setup
1. Run `create_admin.py` to create admin
2. Login as admin
3. No pending users yet
4. Wait for user registrations

### Scenario 2: Multiple Pending Users
1. Users register throughout the day
2. Admin logs in once daily
3. Reviews all pending approvals
4. Approves legitimate users
5. Rejects/ignores suspicious registrations

### Scenario 3: Approve Specific Roles First
1. Filter by role (future enhancement)
2. Approve all residents first
3. Review contractors carefully
4. Verify builder credentials

---

## 🛠️ Troubleshooting

### Problem: Can't create admin user
**Solution**: Check database connection
```bash
cd backend
.venv\Scripts\python.exe test_local_db.py
```

### Problem: Admin can't login
**Check**:
1. Is `is_active=true` for admin?
2. Password correct?
3. Email correct?

**Fix**:
```sql
UPDATE users SET is_active = 1 WHERE email = 'admin@riverdale.com';
```

### Problem: User not appearing in pending list
**Check**:
1. User registration successful?
2. Using correct admin token?
3. Filter parameter: `is_active=false`

### Problem: Approved user still can't login
**Check**:
1. Approval successful?
2. User using correct password?
3. Check user status in database:
```sql
SELECT email, is_active FROM users WHERE email = 'user@example.com';
```

---

## 📊 Database Queries

### View All Pending Users
```sql
SELECT 
    id, 
    name, 
    email, 
    role, 
    created_at 
FROM users 
WHERE is_active = 0 
ORDER BY created_at DESC;
```

### View All Active Users
```sql
SELECT 
    id, 
    name, 
    email, 
    role, 
    created_at 
FROM users 
WHERE is_active = 1 
ORDER BY created_at DESC;
```

### Manually Approve User
```sql
UPDATE users 
SET is_active = 1, updated_at = CURRENT_TIMESTAMP 
WHERE email = 'user@example.com';
```

### Count Pending vs Active
```sql
SELECT 
    is_active,
    COUNT(*) as count 
FROM users 
GROUP BY is_active;
```

---

## 🔐 Security Notes

### Email Validation
✅ **Format**: Validated on frontend and backend
✅ **Uniqueness**: Checked in database
❌ **Verification**: Not implemented (email is not verified)

**Recommendation**: Add email verification in future
- Send OTP to email
- Verify email before approval
- Prevents fake email registrations

### Password Security
✅ **Hashing**: bcrypt with salt
✅ **Minimum Length**: 8 characters
✅ **Complexity**: Uppercase, lowercase, number required

### Admin Protection
✅ **Manual Approval**: Required for all users
✅ **Admin Can't Deactivate Self**: Protected
✅ **Admin Can't Change Own Role**: Protected

---

## 📝 Admin Best Practices

### 1. Review Registrations Daily
- Check pending approvals at least once per day
- Respond promptly to legitimate users

### 2. Verify User Information
- Check email domain (company email?)
- Verify unit number exists
- Cross-check with resident database

### 3. Role Verification
- **Residents**: Should have unit number
- **Contractors**: Verify company
- **Builders**: Verify authorization

### 4. Document Rejections
- Keep record of rejected users
- Note reason for rejection
- Watch for repeat attempts

### 5. Security Monitoring
- Watch for suspicious email patterns
- Monitor registration frequency
- Report unusual activity

---

## 🚦 Status Indicators

### User Registration States
1. **Pending** (`is_active=false`)
   - Just registered
   - Waiting for approval
   - Cannot login

2. **Active** (`is_active=true`)
   - Approved by admin
   - Can login
   - Full access

3. **Deactivated** (`is_active=false` + existing user)
   - Previously active
   - Deactivated by admin
   - Cannot login

---

## 📞 User Communication

### What to tell pending users:
> "Your registration is pending admin approval. You will be able to login once an administrator reviews and approves your account. This typically takes 1-2 business days."

### What to tell approved users:
> "Your account has been approved! You can now login with your registered email and password."

### What to tell rejected users:
> "Your registration could not be approved. Please contact the society administration for more information."

---

## 🎓 Training Materials

### For New Admins
1. Login to system
2. Navigate to "Pending Approvals"
3. Review user details
4. Click "Approve" for legitimate users
5. Contact user if information is unclear

### For Users
1. Register on the platform
2. Wait for approval notification
3. Login once approved
4. Contact admin if waiting > 2 days

---

**Quick Links**:
- **Full Documentation**: [ADMIN_APPROVAL_FEATURE.md](./ADMIN_APPROVAL_FEATURE.md)
- **API Documentation**: http://127.0.0.1:8000/api/docs
- **Project Summary**: [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
