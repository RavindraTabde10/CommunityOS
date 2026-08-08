# API & Service Reference

This document provides a comprehensive reference for all APIs, database schemas, environment variables, and service configurations in **CommunityOS.ai**.

---

## 📡 API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1` (Local)  
Documentation: `http://127.0.0.1:8000/api/docs` (Swagger UI)

### Authentication Endpoints

#### Register User

**Endpoint:** `POST /auth/register`

**Description:** Create a new user account. **Note:** All new registrations require admin approval before the user can login.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe",
  "phone": "+1234567890",
  "role": "resident",
  "unit_number": "A-101"
}
```

**Response:** `201 Created`
```json
{
  "id": "88dde233-eb46-4a5f-ba86-f9509c260607",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "role": "resident",
  "unit_number": "A-101",
  "is_active": false,
  "created_at": "2026-07-23T10:30:00Z",
  "updated_at": "2026-07-23T10:30:00Z"
}
```

**Notes:**
- New users are created with `is_active=false` (pending admin approval)
- User cannot login until an admin sets `is_active=true`
- Email format is automatically validated

**Errors:**
- `400` - Validation error (invalid email, weak password)
- `409` - Email already registered
- `422` - Invalid role value

**Validation Rules:**
- Email must be valid format
- Password minimum 8 characters
- Role must be one of: `resident`, `contractor`, `builder`, `admin`, `security`, `facility`

---

#### Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT token

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

**Note:** OAuth2 standard uses "username" field for email

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` - Invalid credentials
- `403` - Account pending admin approval (for new users)
- `422` - Missing username or password

**Token Details:**
- Access Token Expiry: 30 minutes
- Refresh Token Expiry: 7 days
- Algorithm: HS256

**Usage:**
```bash
# Store token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use in subsequent requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
```

---

#### Get Current User Profile

**Endpoint:** `GET /auth/me`

**Description:** Get authenticated user's profile information

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:** `200 OK`
```json
{
  "id": "88dde233-eb46-4a5f-ba86-f9509c260607",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "role": "resident",
  "unit_number": "A-101",
  "created_at": "2026-07-23T10:30:00Z",
  "updated_at": "2026-07-23T10:30:00Z"
}
```

**Errors:**
- `401` - Invalid or expired token
- `404` - User not found

---

### User Management Endpoints (Admin Only)

#### List Users

**Endpoint:** `GET /users`

**Description:** Get paginated list of all users with optional filters

**Authentication:** Required (Admin only)

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Number of records to return (default: 10, max: 100)
- `role` (string, optional): Filter by role (resident, contractor, builder, admin)
- `search` (string, optional): Search by name or email
- `is_active` (boolean, optional): Filter by approval status (true/false)

**Example - Get Pending Approvals:**
```bash
GET /users?is_active=false&limit=100
```

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": "user-uuid",
      "email": "newuser@example.com",
      "name": "New User",
      "phone": "1234567890",
      "role": "resident",
      "unit_number": "A-101",
      "is_active": false,
      "created_at": "2026-07-28T10:00:00Z",
      "updated_at": null
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Errors:**
- `401` - Not authenticated
- `403` - Not an admin user
- `400` - Invalid role parameter

---

#### Approve/Deactivate User

**Endpoint:** `PATCH /users/{user_id}/status`

**Description:** Activate or deactivate a user account (admin approval workflow)

**Authentication:** Required (Admin only)

**Path Parameters:**
- `user_id` (string): UUID of the user

**Request Body:**
```json
{
  "is_active": true
}
```

**Response:** `200 OK`
```json
{
  "id": "user-uuid",
  "email": "newuser@example.com",
  "name": "New User",
  "role": "resident",
  "is_active": true,
  "created_at": "2026-07-28T10:00:00Z",
  "updated_at": "2026-07-28T10:05:00Z"
}
```

**Notes:**
- Admin cannot deactivate themselves
- Setting `is_active=false` prevents user from logging in
- Setting `is_active=true` approves pending registrations

**Errors:**
- `401` - Not authenticated
- `403` - Not an admin user or trying to modify own status
- `404` - User not found

---

### Issue Management Endpoints

#### Create Issue

**Endpoint:** `POST /issues`

**Description:** Report a new issue in the society

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Broken elevator in Tower A",
  "description": "The elevator in Tower A has been making strange noises and stopped working this morning.",
  "category": "electrical",
  "priority": "high",
  "location": "Tower A, Floor 5",
  "unit_number": "A-501"
}
```

**Response:** `201 Created`
```json
{
  "id": "issue-123",
  "title": "Broken elevator in Tower A",
  "description": "The elevator in Tower A has been making strange noises...",
  "category": "electrical",
  "priority": "high",
  "status": "open",
  "location": "Tower A, Floor 5",
  "unit_number": "A-501",
  "reported_by": "88dde233-eb46-4a5f-ba86-f9509c260607",
  "assigned_to": null,
  "created_at": "2026-07-23T11:00:00Z",
  "updated_at": "2026-07-23T11:00:00Z",
  "resolved_at": null,
  "reporter": {
    "id": "88dde233-eb46-4a5f-ba86-f9509c260607",
    "name": "John Doe",
    "email": "user@example.com"
  },
  "assignee": null,
  "photos": []
}
```

**Validation:**
- `title`: Required, max 200 characters
- `description`: Optional, max 2000 characters
- `category`: Must be valid enum value
- `priority`: Must be valid enum value

**Category Options:**
- `electrical`
- `plumbing`
- `painting`
- `carpentry`
- `flooring`
- `civil`
- `other`

**Priority Options:**
- `low`
- `medium`
- `high`
- `critical`

**Errors:**
- `401` - Not authenticated
- `422` - Validation error

---

#### List Issues

**Endpoint:** `GET /issues`

**Description:** Get list of issues (filtered by user role)

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (int, default=0) - Pagination offset
- `limit` (int, default=100, max=1000) - Number of items to return
- `status` (string, optional) - Filter by status (open, in_progress, resolved, closed)
- `category` (string, optional) - Filter by category
- `priority` (string, optional) - Filter by priority

**Example:** `GET /issues?status=open&priority=high&limit=20`

**Response:** `200 OK`
```json
[
  {
    "id": "issue-123",
    "title": "Broken elevator in Tower A",
    "description": "The elevator in Tower A...",
    "category": "electrical",
    "priority": "high",
    "status": "open",
    "location": "Tower A, Floor 5",
    "unit_number": "A-501",
    "reported_by": "88dde233-eb46-4a5f-ba86-f9509c260607",
    "assigned_to": "contractor-456",
    "created_at": "2026-07-23T11:00:00Z",
    "updated_at": "2026-07-23T11:30:00Z",
    "resolved_at": null,
    "reporter": {
      "id": "88dde233-eb46-4a5f-ba86-f9509c260607",
      "name": "John Doe"
    },
    "assignee": {
      "id": "contractor-456",
      "name": "Mike Electrician"
    },
    "photos": []
  }
]
```

**Role-Based Filtering:**
- **Admin:** Sees all issues
- **Resident:** Sees only their own reported issues
- **Contractor:** Sees issues assigned to them
- **Builder/Security/Facility:** Custom filtering logic

**Errors:**
- `401` - Not authenticated

---

#### Get Issue by ID

**Endpoint:** `GET /issues/{issue_id}`

**Description:** Get detailed information about a specific issue

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": "issue-123",
  "title": "Broken elevator in Tower A",
  "description": "The elevator in Tower A has been making strange noises...",
  "category": "electrical",
  "priority": "high",
  "status": "in_progress",
  "location": "Tower A, Floor 5",
  "unit_number": "A-501",
  "reported_by": "88dde233-eb46-4a5f-ba86-f9509c260607",
  "assigned_to": "contractor-456",
  "created_at": "2026-07-23T11:00:00Z",
  "updated_at": "2026-07-23T12:00:00Z",
  "resolved_at": null,
  "reporter": {
    "id": "88dde233-eb46-4a5f-ba86-f9509c260607",
    "name": "John Doe",
    "email": "user@example.com"
  },
  "assignee": {
    "id": "contractor-456",
    "name": "Mike Electrician",
    "email": "mike@contractor.com"
  },
  "photos": [
    {
      "id": "photo-1",
      "photo_url": "https://s3.amazonaws.com/bucket/photo1.jpg",
      "uploaded_at": "2026-07-23T11:05:00Z"
    }
  ]
}
```

**Permission Check:**
- Admins can view any issue
- Residents can view their own issues
- Contractors can view assigned issues
- Other roles have custom permissions

**Errors:**
- `401` - Not authenticated
- `403` - Permission denied
- `404` - Issue not found

---

#### Update Issue

**Endpoint:** `PUT /issues/{issue_id}`

**Description:** Update issue details (admin or reporter only)

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "critical",
  "assigned_to": "contractor-456"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:** `200 OK`
```json
{
  "id": "issue-123",
  "title": "Updated title",
  "description": "Updated description",
  "category": "electrical",
  "priority": "critical",
  "status": "in_progress",
  "location": "Tower A, Floor 5",
  "unit_number": "A-501",
  "reported_by": "88dde233-eb46-4a5f-ba86-f9509c260607",
  "assigned_to": "contractor-456",
  "created_at": "2026-07-23T11:00:00Z",
  "updated_at": "2026-07-23T13:00:00Z",
  "resolved_at": null,
  "reporter": {...},
  "assignee": {...},
  "photos": [...]
}
```

**Permission Rules:**
- Admin: Can update any issue
- Reporter: Can update own issues only
- Others: Cannot update

**Special Behavior:**
- Setting `status` to `resolved` automatically sets `resolved_at` timestamp

**Errors:**
- `401` - Not authenticated
- `403` - Permission denied (not admin or reporter)
- `404` - Issue not found
- `422` - Validation error

---

#### Delete Issue

**Endpoint:** `DELETE /issues/{issue_id}`

**Description:** Delete an issue (admin or reporter only)

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "message": "Issue deleted successfully"
}
```

**Permission Rules:**
- Admin: Can delete any issue
- Reporter: Can delete own issues only
- Others: Cannot delete

**Errors:**
- `401` - Not authenticated
- `403` - Permission denied
- `404` - Issue not found

---

### Contractor Management

#### Create Contractor Profile

**Endpoint:** `POST /contractors/`

**Description:** Create a contractor profile (contractor role required)

**Authentication:** Required (Contractor role)

**Request Body:**
```json
{
  "company_name": "ABC Electricals",
  "gst_number": "29ABCDE1234F1Z5",
  "license_number": "LIC123456",
  "specializations": ["electrical", "plumbing"],
  "years_of_experience": 5
}
```

**Response:** `201 Created`
```json
{
  "id": "contractor-profile-id",
  "user_id": "user-id",
  "company_name": "ABC Electricals",
  "gst_number": "29ABCDE1234F1Z5",
  "license_number": "LIC123456",
  "specializations": ["electrical", "plumbing"],
  "years_of_experience": 5,
  "is_available": true,
  "availability_status": "available",
  "average_rating": 0.0,
  "total_jobs_completed": 0,
  "completion_rate": 0.0,
  "is_verified": false,
  "created_at": "2026-07-23T10:00:00Z"
}
```

**Errors:**
- `400` - Profile already exists or duplicate GST
- `403` - User is not a contractor

---

#### List Contractors

**Endpoint:** `GET /contractors/`

**Description:** List all contractors with optional filters

**Authentication:** Required

**Query Parameters:**
- `specialization` - Filter by specialization (e.g., "electrical")
- `is_available` - Filter by availability (true/false)
- `min_rating` - Minimum average rating (0.0-5.0)
- `is_verified` - Filter verified contractors (true/false)
- `skip` - Pagination offset (default: 0)
- `limit` - Page size (default: 50, max: 100)

**Example:** `GET /contractors/?specialization=electrical&is_verified=true&min_rating=4.0`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "contractor-1",
      "user_id": "user-1",
      "company_name": "ABC Electricals",
      "specializations": ["electrical", "plumbing"],
      "years_of_experience": 5,
      "is_available": true,
      "average_rating": 4.5,
      "total_jobs_completed": 25,
      "completion_rate": 95.0,
      "is_verified": true
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

#### Get Contractor Details

**Endpoint:** `GET /contractors/{contractor_id}`

**Description:** Get detailed contractor profile with user information

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": "contractor-1",
  "user_id": "user-1",
  "user": {
    "id": "user-1",
    "name": "John Contractor",
    "email": "john@contractor.com",
    "phone": "1234567890"
  },
  "company_name": "ABC Electricals",
  "gst_number": "29ABCDE1234F1Z5",
  "specializations": ["electrical", "plumbing"],
  "years_of_experience": 5,
  "is_available": true,
  "availability_status": "available",
  "average_rating": 4.5,
  "total_jobs_completed": 25,
  "completion_rate": 95.0,
  "is_verified": true,
  "verified_at": "2026-07-15T10:00:00Z",
  "created_at": "2026-07-01T10:00:00Z"
}
```

**Errors:**
- `404` - Contractor not found

---

#### Update Contractor Profile

**Endpoint:** `PUT /contractors/{contractor_id}`

**Description:** Update contractor profile (owner or admin only)

**Authentication:** Required

**Request Body:**
```json
{
  "company_name": "ABC Electricals & Plumbing",
  "specializations": ["electrical", "plumbing", "painting"],
  "is_available": false,
  "availability_status": "busy"
}
```

**Response:** `200 OK` (Updated profile)

**Permission Rules:**
- Contractor can update own profile
- Admin can update any profile

**Errors:**
- `403` - Permission denied
- `404` - Contractor not found

---

#### Get Contractor Statistics

**Endpoint:** `GET /contractors/{contractor_id}/stats`

**Description:** Get comprehensive contractor performance statistics

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "contractor_id": "contractor-1",
  "total_jobs": 30,
  "completed_jobs": 28,
  "in_progress_jobs": 2,
  "completion_rate": 93.33,
  "average_rating": 4.5,
  "total_ratings": 20,
  "rating_breakdown": {
    "5_star": 12,
    "4_star": 6,
    "3_star": 2,
    "2_star": 0,
    "1_star": 0
  },
  "jobs_by_category": {
    "electrical": 15,
    "plumbing": 10,
    "painting": 3
  },
  "recent_ratings": [
    {
      "rating": 5,
      "review_text": "Excellent work!",
      "created_at": "2026-07-20T10:00:00Z"
    }
  ]
}
```

---

#### Verify Contractor

**Endpoint:** `POST /contractors/{contractor_id}/verify`

**Description:** Verify contractor profile (admin only)

**Authentication:** Required (Admin role)

**Response:** `200 OK`
```json
{
  "id": "contractor-1",
  "is_verified": true,
  "verified_at": "2026-07-23T10:00:00Z",
  "verified_by": "admin-user-id"
}
```

**Errors:**
- `403` - Not an admin
- `404` - Contractor not found

---

#### Rate Contractor

**Endpoint:** `POST /contractors/{contractor_id}/rate`

**Description:** Rate a contractor after work completion (issue reporter only)

**Authentication:** Required

**Request Body:**
```json
{
  "issue_id": "issue-123",
  "rating": 5,
  "quality_rating": 5,
  "punctuality_rating": 4,
  "professionalism_rating": 5,
  "review_text": "Excellent work! Very professional and timely.",
  "work_photos": ["https://example.com/photo1.jpg"]
}
```

**Response:** `201 Created`
```json
{
  "id": "rating-1",
  "contractor_id": "contractor-1",
  "issue_id": "issue-123",
  "rated_by": "user-1",
  "rating": 5,
  "quality_rating": 5,
  "punctuality_rating": 4,
  "professionalism_rating": 5,
  "review_text": "Excellent work! Very professional and timely.",
  "created_at": "2026-07-23T10:00:00Z"
}
```

**Business Rules:**
- Only issue reporter can rate
- Requires completed and verified work
- One rating per issue per contractor
- Rating updates contractor's average_rating

**Errors:**
- `400` - Work not complete, duplicate rating, or validation error
- `403` - Not the issue reporter
- `404` - Contractor or issue not found

---

#### List Contractor Ratings

**Endpoint:** `GET /contractors/{contractor_id}/ratings`

**Description:** Get paginated list of contractor ratings

**Authentication:** Required

**Query Parameters:**
- `skip` - Pagination offset (default: 0)
- `limit` - Page size (default: 20, max: 100)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "rating-1",
      "contractor_id": "contractor-1",
      "issue_id": "issue-123",
      "rating": 5,
      "review_text": "Excellent work!",
      "reviewer": {
        "id": "user-1",
        "name": "John Doe"
      },
      "created_at": "2026-07-23T10:00:00Z"
    }
  ],
  "total": 20,
  "skip": 0,
  "limit": 20
}
```

---

#### Assign Issue to Contractor

**Endpoint:** `POST /issues/{issue_id}/assign`

**Description:** Assign an issue to a contractor (admin/facility only)

**Authentication:** Required (Admin/Facility role)

**Request Body:**
```json
{
  "contractor_id": "contractor-1",
  "notes": "Urgent - needs immediate attention"
}
```

**Response:** `200 OK`
```json
{
  "issue_id": "issue-123",
  "contractor_id": "contractor-1",
  "assigned_to": "contractor-user-id",
  "status": "in_progress",
  "assigned_at": "2026-07-23T10:00:00Z"
}
```

**Business Rules:**
- Only admin/facility can assign
- Contractor must have contractor role
- Issue status changes to "in_progress"
- Activity log created

**Errors:**
- `400` - User is not a contractor
- `403` - Not admin/facility
- `404` - Issue or contractor not found

---

#### Unassign Contractor from Issue

**Endpoint:** `DELETE /issues/{issue_id}/assign`

**Description:** Remove contractor assignment (admin/facility only)

**Authentication:** Required (Admin/Facility role)

**Response:** `200 OK`
```json
{
  "message": "Contractor unassigned successfully",
  "issue_id": "issue-123",
  "previous_assignee": "contractor-user-id",
  "status": "open"
}
```

**Business Rules:**
- Issue status resets to "open"
- Activity log created

**Errors:**
- `400` - Issue not assigned
- `403` - Not admin/facility
- `404` - Issue not found

---

#### Mark Work Complete

**Endpoint:** `POST /issues/{issue_id}/complete`

**Description:** Mark work as complete (assigned contractor only)

**Authentication:** Required (Contractor role)

**Request Body:**
```json
{
  "work_description": "Fixed electrical wiring and replaced circuit breaker",
  "materials_used": [
    {
      "name": "Wire 2.5mm",
      "quantity": 10,
      "unit": "meters",
      "cost": 250.00
    },
    {
      "name": "MCB 32A",
      "quantity": 1,
      "unit": "piece",
      "cost": 120.00
    }
  ],
  "labor_cost": 500.00,
  "total_cost": 870.00,
  "after_photos": ["https://example.com/photo1.jpg"]
}
```

**Response:** `201 Created`
```json
{
  "id": "work-completion-1",
  "issue_id": "issue-123",
  "contractor_id": "contractor-profile-1",
  "completed_at": "2026-07-23T10:00:00Z",
  "work_description": "Fixed electrical wiring and replaced circuit breaker",
  "total_cost": 870.00,
  "is_verified": false
}
```

**Business Rules:**
- Only assigned contractor can mark complete
- Issue status changes to "resolved"
- One completion per issue
- Captures before photos from issue

**Errors:**
- `403` - Not assigned contractor
- `404` - Issue not found
- `400` - Already marked complete

---

#### Verify Work Completion

**Endpoint:** `POST /work-completions/{completion_id}/verify`

**Description:** Verify or reject completed work (admin/facility only)

**Authentication:** Required (Admin/Facility role)

**Request Body:**
```json
{
  "is_approved": true,
  "verification_notes": "Work quality is excellent. All issues resolved."
}
```

**Response:** `200 OK`
```json
{
  "id": "work-completion-1",
  "issue_id": "issue-123",
  "is_verified": true,
  "verified_by": "admin-user-id",
  "verified_at": "2026-07-23T11:00:00Z",
  "verification_notes": "Work quality is excellent. All issues resolved."
}
```

**Business Rules:**
- If approved: Issue status changes to "closed", contractor metrics updated
- If rejected: Issue remains "resolved", contractor can rework
- Only admin/facility can verify

**Errors:**
- `403` - Not admin/facility
- `404` - Work completion not found

---

### Additional Live Endpoints

The following modules are fully implemented. Use Swagger UI at `http://127.0.0.1:8000/api/docs` for full interactive documentation on each.

| Module | Path Prefix | Key Operations |
|--------|-------------|----------------|
| Announcements | `/api/v1/announcements/` | CRUD, expiry date support |
| Events | `/api/v1/events/` | CRUD, event categories |
| Polls | `/api/v1/polls/` | CRUD, vote, auto-close via `active_till` |
| Committee | `/api/v1/committee/` | CRUD, role/tenure management |
| Assets | `/api/v1/assets/` | CRUD, QR code generation |
| Bookings | `/api/v1/bookings/` | CRUD, availability check |
| Issue Photos | `/api/v1/issues/{id}/photos` | Upload, list, delete |
| Comments | `/api/v1/issues/{id}/comments` | CRUD, activity log |
| Visitors | `/api/v1/visitors/` | CRUD, entry/exit tracking |
| Water Tanker | `/api/v1/water-tanker/` | CRUD, vehicle details, departure time |
| Security Guidelines | `/api/v1/guidelines/` | CRUD |
| Feedback | `/api/v1/feedback/` | CRUD |
| Reports | `/api/v1/reports/` | Issue analytics, asset reports, contractor reports, export |

---

### Health Check

#### API Health

**Endpoint:** `GET /health`

**Description:** Check API server health

**Authentication:** Not required

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-07-23T10:00:00Z"
}
```

---

## 🗄️ Database Schema

### Users Table

**Table Name:** `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PRIMARY KEY | Unique user identifier |
| `email` | String | UNIQUE, INDEX | User email (login username) |
| `password_hash` | String | NOT NULL | Bcrypt hashed password |
| `name` | String | NOT NULL | User's full name |
| `phone` | String | NULL | Contact phone number |
| `role` | Enum | NOT NULL | User role (see UserRole enum) |
| `unit_number` | String | NULL | Residential unit number |
| `created_at` | DateTime | NOT NULL | Account creation timestamp |
| `updated_at` | DateTime | NOT NULL | Last update timestamp |

**UserRole Enum Values:**
- `resident` - Residential unit owner/tenant
- `contractor` - External contractor
- `builder` - Builder/developer
- `admin` - System administrator
- `security` - Security personnel
- `facility` - Facility management

**Indexes:**
- `email` - For fast login lookups

**Relationships:**
- One-to-Many with `issues` (as reporter)
- One-to-Many with `issues` (as assignee)

---

### Issues Table

**Table Name:** `issues`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PRIMARY KEY | Unique issue identifier |
| `title` | String(200) | NOT NULL | Issue title |
| `description` | Text | NULL | Detailed description |
| `category` | Enum | NOT NULL | Issue category (see IssueCategory) |
| `priority` | Enum | NOT NULL, DEFAULT='medium' | Priority level |
| `status` | Enum | NOT NULL, DEFAULT='open' | Current status |
| `location` | String | NULL | Physical location |
| `unit_number` | String | NULL | Related unit number |
| `reported_by` | String | FK (users.id), NOT NULL | Reporter user ID |
| `assigned_to` | String | FK (users.id), NULL | Assignee user ID |
| `created_at` | DateTime | NOT NULL | Issue creation timestamp |
| `updated_at` | DateTime | NOT NULL | Last update timestamp |
| `resolved_at` | DateTime | NULL | Resolution timestamp |

**IssueCategory Enum:**
- `electrical` - Electrical problems
- `plumbing` - Water, drainage issues
- `painting` - Paint, wall issues
- `carpentry` - Wooden fixtures
- `flooring` - Floor damage
- `civil` - Structural issues
- `other` - Miscellaneous

**IssuePriority Enum:**
- `low` - Non-urgent
- `medium` - Normal priority
- `high` - Urgent
- `critical` - Emergency

**IssueStatus Enum:**
- `open` - Newly reported
- `in_progress` - Being worked on
- `resolved` - Fixed, pending verification
- `closed` - Verified and closed

**Indexes:**
- `reported_by` - For user's issues lookup
- `assigned_to` - For contractor's tasks
- `status` - For filtering
- `category` - For filtering

**Relationships:**
- Many-to-One with `users` (reporter)
- Many-to-One with `users` (assignee)
- One-to-Many with `issue_photos`

---

### Issue Photos Table

**Table Name:** `issue_photos`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PRIMARY KEY | Unique photo identifier |
| `issue_id` | String | FK (issues.id), NOT NULL | Related issue ID |
| `photo_url` | String | NOT NULL | S3/storage URL |
| `uploaded_at` | DateTime | NOT NULL | Upload timestamp |

**Indexes:**
- `issue_id` - For fetching issue photos

**Relationships:**
- Many-to-One with `issues`

**Storage:**
- Photos stored in AWS S3 or Supabase Storage
- URL format: `https://bucket.s3.region.amazonaws.com/path/to/photo.jpg`

---

### Contractor Profiles Table

**Table Name:** `contractor_profiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PRIMARY KEY | Unique contractor profile ID |
| `user_id` | String | FK (users.id), UNIQUE, NOT NULL | Associated user account |
| `company_name` | String | NULL | Company/business name |
| `gst_number` | String | UNIQUE, NULL | GST registration number |
| `license_number` | String | NULL | Professional license number |
| `specializations` | JSON | NOT NULL | Array of specializations |
| `years_of_experience` | Integer | NULL | Years of professional experience |
| `is_available` | Boolean | DEFAULT=True | Currently available for work |
| `availability_status` | Enum | DEFAULT='available' | Detailed availability status |
| `total_jobs_completed` | Integer | DEFAULT=0 | Total completed jobs |
| `average_rating` | Numeric(3,2) | DEFAULT=0.00 | Average rating (0.00-5.00) |
| `total_ratings` | Integer | DEFAULT=0 | Total number of ratings |
| `response_time_avg` | Integer | NULL | Average response time (hours) |
| `completion_rate` | Numeric(5,2) | DEFAULT=0.00 | Completion rate percentage |
| `is_verified` | Boolean | DEFAULT=False | Admin verified status |
| `verified_by` | String | FK (users.id), NULL | Verifying admin ID |
| `verified_at` | DateTime | NULL | Verification timestamp |
| `is_active` | Boolean | DEFAULT=True | Profile active status |
| `created_at` | DateTime | NOT NULL | Profile creation timestamp |
| `updated_at` | DateTime | NOT NULL | Last update timestamp |

**AvailabilityStatus Enum:**
- `available` - Ready for new assignments
- `busy` - Currently working on projects
- `on_leave` - Temporarily unavailable
- `inactive` - Not accepting work

**Specializations (JSON Array):**
- `electrical`, `plumbing`, `painting`, `carpentry`, `flooring`, `civil`, `hvac`, `landscaping`, `pest_control`, `cleaning`, `other`

**Indexes:**
- `user_id` - For profile lookup
- `gst_number` - For uniqueness check
- `is_verified` - For filtering verified contractors

**Relationships:**
- One-to-One with `users`
- One-to-Many with `contractor_ratings`
- One-to-Many with `work_completions`

---

### Contractor Ratings Table

**Table Name:** `contractor_ratings`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PRIMARY KEY | Unique rating identifier |
| `contractor_id` | String | FK (contractor_profiles.id), NOT NULL | Rated contractor |
| `issue_id` | String | FK (issues.id), NULL | Related issue (if applicable) |
| `rated_by` | String | FK (users.id), NOT NULL | User who gave rating |
| `rating` | Integer | CHECK (1-5), NOT NULL | Overall rating (1-5 stars) |
| `quality_rating` | Integer | CHECK (1-5), NULL | Work quality rating |
| `punctuality_rating` | Integer | CHECK (1-5), NULL | Punctuality rating |
| `professionalism_rating` | Integer | CHECK (1-5), NULL | Professionalism rating |
| `review_text` | Text | NULL | Written review |
| `work_photos` | JSON | NULL | Array of work photo URLs |
| `created_at` | DateTime | NOT NULL | Rating timestamp |

**Indexes:**
- `contractor_id` - For contractor's ratings lookup
- `issue_id` - For issue-based rating lookup

**Relationships:**
- Many-to-One with `contractor_profiles`
- Many-to-One with `issues`
- Many-to-One with `users` (rater)

**Business Rules:**
- Only issue reporter can rate contractor for that issue
- One rating per issue per contractor
- Rating requires completed work verification

---

### Work Completions Table

**Table Name:** `work_completions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PRIMARY KEY | Unique work completion ID |
| `issue_id` | String | FK (issues.id), UNIQUE, NOT NULL | Related issue |
| `contractor_id` | String | FK (contractor_profiles.id), NOT NULL | Contractor who completed work |
| `completed_at` | DateTime | NOT NULL | Work completion timestamp |
| `work_description` | Text | NULL | Description of work done |
| `materials_used` | JSON | NULL | Array of materials used |
| `labor_cost` | Numeric | NULL | Labor cost amount |
| `total_cost` | Numeric | NULL | Total cost (labor + materials) |
| `before_photos` | JSON | NULL | Array of before photos |
| `after_photos` | JSON | NULL | Array of after photos |
| `is_verified` | Boolean | DEFAULT=False | Admin verification status |
| `verified_by` | String | FK (users.id), NULL | Verifying admin ID |
| `verified_at` | DateTime | NULL | Verification timestamp |
| `verification_notes` | Text | NULL | Admin verification notes |

**Indexes:**
- `issue_id` - For issue completion lookup (unique)
- `contractor_id` - For contractor's work history

**Relationships:**
- One-to-One with `issues`
- Many-to-One with `contractor_profiles`
- Many-to-One with `users` (verifier)

**Business Rules:**
- One completion record per issue
- Only assigned contractor can mark work complete
- Admin/facility can verify or reject completion
- Verified completions enable rating

---

## 🔐 Authentication & Security

### JWT Token Structure

**Access Token Payload:**
```json
{
  "sub": "88dde233-eb46-4a5f-ba86-f9509c260607",  // User ID
  "email": "user@example.com",
  "role": "resident",
  "exp": 1627048200  // Expiration timestamp
}
```

**Refresh Token Payload:**
```json
{
  "sub": "88dde233-eb46-4a5f-ba86-f9509c260607",
  "type": "refresh",
  "exp": 1627653000  // 7 days from issue
}
```

**Token Generation:**
- Algorithm: HS256
- Secret Key: From `SECRET_KEY` environment variable
- Access Token TTL: 30 minutes
- Refresh Token TTL: 7 days

**Token Usage:**
```bash
# In Authorization header
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Password Security

**Hashing:**
- Algorithm: bcrypt
- Rounds: 12 (default)
- Salt: Automatically generated per password

**Validation Rules:**
- Minimum length: 8 characters
- Recommended: Include uppercase, lowercase, numbers, symbols

**Storage:**
- Never store plaintext passwords
- Only `password_hash` stored in database
- Original password never logged or transmitted in responses

---

### CORS Configuration

**Allowed Origins:**
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev port)
- Production URL (to be configured)

**Allowed Methods:**
- GET
- POST
- PUT
- DELETE
- OPTIONS

**Allowed Headers:**
- Authorization
- Content-Type

---

## ⚙️ Environment Variables

### Required Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `DATABASE_URL` | String | Database connection string | `sqlite:///./society_app.db` |
| `SECRET_KEY` | String | JWT secret key (generated) | `IMf5xFvoXnTMW0fRCygX5S0G_NRgESfNdr24OlXHx4k` |
| `CORS_ORIGINS` | String | Comma-separated allowed origins | `http://localhost:5173,http://localhost:3000` |

### Optional Variables

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ALGORITHM` | String | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Int | Access token TTL | `30` |
| `AWS_ACCESS_KEY_ID` | String | AWS S3 access key | None |
| `AWS_SECRET_ACCESS_KEY` | String | AWS S3 secret key | None |
| `AWS_REGION` | String | AWS region | `us-east-1` |
| `S3_BUCKET_NAME` | String | S3 bucket for file uploads | None |
| `SUPABASE_URL` | String | Supabase project URL | None |
| `SUPABASE_PUBLISHABLE_KEY` | String | Supabase anon/public key | None |
| `RESEND_API_KEY` | String | Resend email API key | None |

### Generating SECRET_KEY

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
# Output: IMf5xFvoXnTMW0fRCygX5S0G_NRgESfNdr24OlXHx4k
```

### Environment File Example

**`.env`** (never commit this file):
```bash
# Database
DATABASE_URL=sqlite:///./society_app.db

# Security
SECRET_KEY=IMf5xFvoXnTMW0fRCygX5S0G_NRgESfNdr24OlXHx4k
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=society-app-files

# Supabase (optional)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_PUBLISHABLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Email (optional)
RESEND_API_KEY=re_xxxxxxxxxxxxx
```

---

## 🛠️ Service Configurations

### Database Configuration

**SQLite (Development):**
- File location: `backend/society_app.db`
- Connection pool: Not applicable for SQLite
- WAL mode: Enabled for concurrent reads
- Foreign keys: Enabled

**PostgreSQL (Production - Future):**
```
DATABASE_URL=postgresql://user:password@host:5432/database
```
- Connection pooling: 10-20 connections
- SSL mode: require
- Statement timeout: 30 seconds

---

### File Upload Service ✅ (Live)

**AWS S3:**
```python
# Configuration
AWS_ACCESS_KEY_ID = "your-key"
AWS_SECRET_ACCESS_KEY = "your-secret"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "society-app-files"

# Upload path structure
uploads/
  ├── issues/
  │   ├── {issue_id}/
  │   │   ├── photo1.jpg
  │   │   └── photo2.jpg
```

**Supabase Storage:**
```python
# Configuration
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGci..."

# Bucket structure
society-app-files/
  ├── issues/
  │   ├── {issue_id}/
```

---

### Email Service ✅ (Live)

**Resend Integration:**
```python
RESEND_API_KEY = "re_xxxxxxxxxxxxx"

# Email templates
- Issue Created: Notify admins
- Issue Assigned: Notify contractor
- Issue Resolved: Notify reporter
- Password Reset: Send reset link
```

---

## 📊 API Response Formats

### Success Response

**Standard Success:**
```json
{
  "id": "resource-id",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2026-07-23T10:00:00Z"
}
```

**List Response:**
```json
[
  {
    "id": "item-1",
    "field": "value"
  },
  {
    "id": "item-2",
    "field": "value"
  }
]
```

**Message Response:**
```json
{
  "message": "Operation successful",
  "detail": "Additional information"
}
```

---

### Error Response

**Standard Error Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Permission Error (403):**
```json
{
  "detail": "Not enough permissions"
}
```

**Not Found Error (404):**
```json
{
  "detail": "Resource not found"
}
```

---

## 🧪 Testing Reference

### Manual Testing via Swagger UI

**Access:** http://127.0.0.1:8000/api/docs

**Steps:**
1. Expand endpoint
2. Click "Try it out"
3. Fill request body
4. Click "Execute"
5. View response

**For Protected Endpoints:**
1. Login to get token
2. Click "Authorize" button (top right)
3. Enter: `Bearer <your-token>`
4. Click "Authorize"
5. Now all requests include auth header

---

### Testing with curl

**Register:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "role": "resident"
  }'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "password123"
  }'
```

**Get Profile:**
```bash
TOKEN="your-token-here"

curl -X GET http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Create Issue:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/issues \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Issue",
    "description": "This is a test",
    "category": "electrical",
    "priority": "medium"
  }'
```

---

## 📈 API Rate Limits (Future)

**Planned Limits:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Admin: Unlimited

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1627048200
```

---

## 🔄 API Versioning

**Current Version:** v1

**URL Structure:** `/api/v1/endpoint`

**Version Headers:**
```
API-Version: 1.0
```

**Deprecation Policy:**
- New version released: v1 supported for 6 months
- Breaking changes: Major version bump
- Feature additions: Minor version bump

---

## 📝 Summary

### Quick Stats
- **Total Endpoints:** 40+ across 17 modules
- **Authentication Endpoints:** 5 (register, login, me, change-password, password-reset)
- **Issue Endpoints:** 6 (CRUD + filters + issue-number)
- **Additional Modules:** Announcements, Events, Polls, Committee, Assets, Bookings, Contractors, Visitors, Water Tanker, Guidelines, Feedback, Reports, Photos, Comments, Users, Work Completions
- **Database Tables:** 18 (users, issues, issue_photos, comments, activities, announcements, assets, bookings, committee_members, contractor_profiles, contractor_ratings, work_completions, events, feedback, guidelines, organizations, polls, visitors, water_tanker_orders)
- **Migrations:** 28 applied
- **Middleware:** Rate Limiter, Logging, Security Headers, GZip, CORS

### Key URLs
- **API Base:** http://127.0.0.1:8000/api/v1
- **Swagger Docs:** http://127.0.0.1:8000/api/docs
- **ReDoc:** http://127.0.0.1:8000/api/redoc

### Important Notes
- All timestamps in UTC
- All IDs are strings (UUID format)
- All responses use snake_case field names
- File uploads: live (S3/Supabase)
- Rate limiting: live (per-IP)
- Security headers: live (OWASP-aligned)

---

**Last Updated:** 2026-08-07  
**API Version:** 2.0  
**Schema Version:** 1.0
