# 📁 CommunityOS.ai - Complete Project Index

**Last Updated:** 2026-08-07  
**Version:** 2.0.0

This document provides a comprehensive map of the CommunityOS.ai codebase, describing the purpose and contents of each directory and key file.

---

## 📁 Root Directory

```
society_management_app/
├── backend/              # FastAPI REST API server
├── frontend/             # React + Vite web application
├── .plans/               # Implementation plans and notes
├── docs/                 # Additional documentation
├── AGENTS.md             # Agent guidance for assisted coding
├── WORKFLOW.md           # Development workflow procedures
├── INDEX.md              # This file - project structure map
├── REFERENCE.md          # API and service reference
├── PROJECT_SUMMARY.md    # High-level project overview
├── ARCHITECTURE.md       # System architecture documentation
├── DEVELOPMENT_PLAN.md   # Overall project roadmap
├── QUICKSTART.md         # Quick setup guide
├── IMPLEMENTATION_CHECKLIST.md  # Feature completion tracker
├── README.md             # Main project README
└── .gitignore            # Git ignore rules
```

### Purpose of Root-Level Documents

| File | Purpose |
|------|---------|
| `AGENTS.md` | Guidance for GitHub Copilot agent-assisted development |
| `WORKFLOW.md` | Mandatory workflow for all code changes |
| `INDEX.md` | This file - complete project structure map |
| `REFERENCE.md` | API endpoints, schemas, and service configurations |
| `PROJECT_SUMMARY.md` | High-level overview of project goals and scope |
| `ARCHITECTURE.md` | System design, technology choices, patterns |
| `DEVELOPMENT_PLAN.md` | Long-term roadmap and milestones |
| `IMPLEMENTATION_CHECKLIST.md` | Track completed and pending features |
| `QUICKSTART.md` | Get started in 5 minutes guide |

---

## 🔧 Backend Directory (`backend/`)

**Purpose:** FastAPI-based REST API for society management operations

```
backend/
├── app/                  # Main application code
│   ├── __init__.py       # App initialization
│   ├── main.py           # FastAPI application entry point
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configurations
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response models
│   └── services/         # Business logic layer
├── alembic/              # Database migration system
│   ├── versions/         # Migration scripts
│   ├── env.py            # Alembic configuration
│   └── script.py.mako    # Migration template
├── tests/                # Test suite (8 test modules ✅)
├── .env                  # Environment variables (not in git)
├── .env.template         # Environment variables template
├── alembic.ini           # Alembic configuration file
├── requirements.txt      # Python dependencies
├── test_db_connection.py # Database connection test
├── API_README.md         # Complete API documentation
├── API_IMPLEMENTATION_PLAN.md  # Detailed backend roadmap
├── QUICK_REFERENCE.md    # Quick command cheat sheet
└── README.md             # Backend setup guide
```

### Backend Structure Details

#### `app/` - Main Application

```
app/
├── __init__.py           # Package initialization
└── main.py               # FastAPI app creation, CORS, routers
```

**`main.py`** - Application Entry Point
- Creates FastAPI application instance
- Configures CORS middleware
- Includes API routers
- Defines health check endpoint
- **Key Components:**
  - `app = FastAPI(title="Society Management API")`
  - `app.add_middleware(CORSMiddleware)`
  - `app.include_router(api_router, prefix="/api/v1")`

---

#### `app/api/` - API Routes

```
app/api/
├── __init__.py
└── v1/                   # API version 1
    ├── __init__.py
    ├── api.py            # Main router aggregation
    ├── events.py         # Events router
    ├── polls.py          # Polls router
    └── endpoints/        # Individual endpoint modules
        ├── __init__.py
        ├── auth.py           # /auth/*
        ├── users.py          # /users/*
        ├── issues.py         # /issues/*
        ├── photos.py         # /issues/{id}/photos
        ├── comments.py       # /issues/{id}/comments
        ├── announcements.py  # /announcements/*
        ├── assets.py         # /assets/*
        ├── bookings.py       # /bookings/*
        ├── committee.py      # /committee/*
        ├── contractors.py    # /contractors/*
        ├── feedback.py       # /feedback/*
        ├── guidelines.py     # /guidelines/*
        ├── reports.py        # /reports/*
        ├── visitors.py       # /visitors/*
        ├── water_tanker.py   # /water-tanker/*
        └── work_completions.py
```

**`app/api/v1/api.py`** - Router Aggregation
- Combines all endpoint routers
- **Purpose:** Central API router configuration

**`app/api/v1/endpoints/auth.py`** - Authentication
- **Endpoints:**
  - `POST /auth/register` - User registration
  - `POST /auth/login` - User login (returns JWT)
  - `GET /auth/me` - Get current user profile
- **Dependencies:** `get_current_user` (JWT validation)
- **Services Used:** `AuthService` (password hashing, token generation)

**`app/api/v1/endpoints/issues.py`** - Issue Management
- **Endpoints:**
  - `POST /issues` - Create new issue (auth required)
  - `GET /issues` - List issues (filtered by user role)
  - `GET /issues/{issue_id}` - Get specific issue
  - `PUT /issues/{issue_id}` - Update issue (permission check)
  - `DELETE /issues/{issue_id}` - Delete issue (admin/reporter only)
- **Dependencies:** `get_current_user`
- **Role-Based Filtering:**
  - Admins: See all issues
  - Residents: See only own issues
  - Others: Custom filtering logic

---

#### `app/core/` - Core Configuration

```
app/core/
├── __init__.py
└── config.py             # Application settings
```

**`app/core/config.py`** - Settings Management
- **Purpose:** Centralized configuration using Pydantic BaseSettings
- **Key Settings:**
  - `DATABASE_URL` - Database connection string
  - `SECRET_KEY` - JWT secret key
  - `ALGORITHM` - JWT algorithm (HS256)
  - `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (30 mins)
  - `CORS_ORIGINS` - Allowed origins for CORS
  - Optional external services (Supabase, AWS, Resend)
- **Usage:** `from app.core.config import settings`

---

#### `app/db/` - Database Setup

```
app/db/
├── __init__.py
├── base.py               # SQLAlchemy declarative base
└── session.py            # Database session management
```

**`app/db/base.py`** - Declarative Base
- **Purpose:** SQLAlchemy base class for all models
- **Code:** `Base = declarative_base()`
- **Important:** Does NOT import models (to avoid circular imports)
- Models imported in `alembic/env.py` instead

**`app/db/session.py`** - Session Management
- **Purpose:** Database session factory and dependency
- **Key Functions:**
  - `get_db()` - FastAPI dependency for database sessions
  - `SessionLocal` - SQLAlchemy session maker
- **Usage in endpoints:**
  ```python
  @router.post("/endpoint")
  def create_resource(db: Session = Depends(get_db)):
      # Use db session
  ```

---

#### `app/models/` - Database Models

```
app/models/
├── __init__.py           # Exports all models
├── user.py               # User model
├── issue.py              # Issue and IssuePhoto models
├── comment.py            # Comment model
├── activity.py           # Activity log model
├── announcement.py       # Announcement model
├── asset.py              # Asset & booking models
├── audit_log.py          # Audit log model
├── committee_member.py   # Committee member model
├── contractor.py         # Contractor profile & ratings models
├── event.py              # Event model
├── feedback.py           # Feedback model
├── guideline.py          # Security guideline model
├── organization.py       # Organization/tenant model
├── poll.py               # Poll & vote models
├── settings.py           # Settings model
├── subscription.py       # Subscription model
├── visitor.py            # Visitor log model
└── water_tanker.py       # Water tanker order model
```

**`app/models/user.py`** - User Model
- **Purpose:** User authentication and authorization
- **Fields:**
  - `id` (String, primary key)
  - `email` (String, unique, index)
  - `password_hash` (String)
  - `name` (String)
  - `phone` (String, optional)
  - `role` (Enum: resident, contractor, builder, admin, security, facility)
  - `unit_number` (String, optional)
  - `created_at`, `updated_at` (DateTime)
- **Relationships:**
  - `reported_issues` - Issues reported by user
  - `assigned_issues` - Issues assigned to user

**`app/models/issue.py`** - Issue Model
- **Purpose:** Issue tracking for society problems
- **Fields:**
  - `id` (String, primary key)
  - `title` (String)
  - `description` (Text)
  - `category` (Enum: electrical, plumbing, painting, carpentry, flooring, civil, other)
  - `priority` (Enum: low, medium, high, critical)
  - `status` (Enum: open, in_progress, resolved, closed)
  - `location` (String, optional)
  - `unit_number` (String, optional)
  - `reported_by` (FK to users)
  - `assigned_to` (FK to users, optional)
  - `created_at`, `updated_at`, `resolved_at` (DateTime)
- **Relationships:**
  - `reporter` - User who reported issue
  - `assignee` - User assigned to fix issue
  - `photos` - List of IssuePhoto objects

**`app/models/issue.py`** - IssuePhoto Model
- **Purpose:** Store issue photo metadata
- **Fields:**
  - `id` (String, primary key)
  - `issue_id` (FK to issues)
  - `photo_url` (String) - S3/storage URL
  - `uploaded_at` (DateTime)

---

#### `app/schemas/` - Pydantic Schemas

```
app/schemas/
├── __init__.py
├── user.py               # User request/response schemas
└── issue.py              # Issue request/response schemas
```

**`app/schemas/user.py`** - User Schemas
- **Purpose:** Request validation and response serialization
- **Schemas:**
  - `UserBase` - Common user fields
  - `UserCreate` - Registration request (includes password)
  - `UserResponse` - API response (excludes password_hash)
  - `UserLogin` - Login request
  - `Token` - JWT token response
  - `TokenData` - Token payload structure

**`app/schemas/issue.py`** - Issue Schemas
- **Purpose:** Issue request/response models
- **Schemas:**
  - `IssueBase` - Common issue fields
  - `IssueCreate` - Create issue request
  - `IssueUpdate` - Update issue request
  - `IssueResponse` - API response with relationships
  - `IssuePhotoResponse` - Photo metadata response

---

#### `app/services/` - Business Logic

```
app/services/
├── __init__.py
├── auth_service.py        # Authentication & JWT logic
├── announcement_service.py
├── asset_service.py
├── audit_service.py
├── committee_service.py
├── contractor_service.py
├── email_service.py
├── event_service.py
├── feedback_service.py
├── guideline_service.py
├── poll_service.py
├── report_service.py
├── s3_service.py          # File upload to S3/Supabase
└── visitor_service.py
```

**`app/services/auth_service.py`** - Authentication Service
- **Purpose:** Password hashing and JWT operations
- **Functions:**
  - `verify_password(plain, hashed)` - Check password
  - `get_password_hash(password)` - Hash password with bcrypt
  - `create_access_token(data, expires_delta)` - Generate JWT (30 min expiry)
  - `create_refresh_token(data)` - Generate refresh JWT (7 days)
  - `decode_token(token)` - Validate and decode JWT
- **Dependencies:** Uses `settings.SECRET_KEY` and `settings.ALGORITHM`

**`app/services/s3_service.py`** - File Upload Service
- **Purpose:** Handle file uploads to S3 or Supabase Storage
- **Status:** ✅ Live
- **Functions:**
  - `upload_file(file, bucket, key)`
  - `delete_file(bucket, key)`
  - `generate_presigned_url(bucket, key)`

---

#### `alembic/` - Database Migrations

```
alembic/
├── versions/             # Migration scripts
│   └── [timestamp]_initial_migration.py
├── env.py                # Alembic environment config
└── script.py.mako        # Migration script template
```

**`alembic/env.py`** - Migration Configuration
- **Purpose:** Configure Alembic for autogeneration
- **Key Setup:**
  - Imports all models (User, Issue, IssuePhoto)
  - Sets `target_metadata = Base.metadata`
  - Configures database URL
- **Important:** This is where models are imported (not in base.py)

**`alembic/versions/`** - Migration History
- **Purpose:** Version-controlled schema changes
- **Naming:** `[timestamp]_description.py`
- **Commands:**
  - Create: `alembic revision --autogenerate -m "description"`
  - Apply: `alembic upgrade head`
  - Rollback: `alembic downgrade -1`

---

#### Backend Configuration Files

**`requirements.txt`** - Python Dependencies
```
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pydantic==2.5.3
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.2
python-multipart==0.0.6
```

**`.env.template`** - Environment Variables Template
```bash
# Database
DATABASE_URL=sqlite:///./society_app.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
S3_BUCKET_NAME=

# Optional: Supabase
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=

# Optional: Email (Resend)
RESEND_API_KEY=
```

**`alembic.ini`** - Alembic Configuration
- Database URL (can be overridden by env.py)
- Migration script location
- Logging configuration

---

## 🎨 Frontend Directory (`frontend/`)

**Purpose:** React-based web application for society management

```
frontend/
├── src/
│   ├── App.jsx               # Root component with routing
│   ├── main.jsx              # React DOM entry point
│   ├── theme.js              # Material-UI theme configuration
│   ├── index.css             # Global styles
│   ├── api/                  # Axios service layer
│   │   ├── client.js           # Axios instance with auth interceptors
│   │   ├── authService.js
│   │   ├── issueService.js
│   │   ├── userService.js
│   │   ├── assetService.js
│   │   ├── commentService.js
│   │   ├── announcementService.js
│   │   ├── committeeService.js
│   │   ├── events.js
│   │   ├── polls.js
│   │   ├── feedbackService.js
│   │   ├── guidelineService.js
│   │   ├── reportService.js
│   │   ├── visitorService.js
│   │   ├── waterTankerService.js
│   │   └── activityService.js
│   ├── store/                # Redux state management
│   │   ├── index.js
│   │   └── authSlice.js
│   ├── pages/
│   │   ├── auth/               # Login, Register, ForgotPassword, ResetPassword
│   │   ├── Dashboard.jsx
│   │   ├── issues/             # IssueList, IssueDetail, CreateIssue, EditIssue
│   │   ├── assets/             # AssetList, AssetDetail, QRScanner
│   │   ├── bookings/           # MyBookings
│   │   ├── reports/            # ReportsDashboard, IssueAnalytics, AssetReports,
│   │   │                   #   ContractorReports, ExportReports
│   │   ├── admin/              # Users, PendingUsers, CommitteeManagement,
│   │   │                   #   AssetManagement
│   │   ├── AnnouncementManagement.jsx
│   │   ├── Events.jsx / CreateEvent.jsx / EditEvent.jsx
│   │   ├── Polls.jsx / CreatePoll.jsx / EditPoll.jsx
│   │   ├── ResidentDirectory.jsx
│   │   ├── SecurityPage.jsx
│   │   ├── VisitorApproval.jsx
│   │   ├── WaterTanker.jsx
│   │   ├── Feedback.jsx
│   │   └── Profile.jsx / EditProfile.jsx / ChangePassword.jsx
│   └── components/
│       ├── layout/             # MainLayout, AuthLayout, AppBar, Sidebar, UserMenu
│       ├── dashboard/          # StatCard, QuickActions, AnnouncementMarquee,
│       │                   #   UpcomingEvents, ActivePollWidget,
│       │                   #   CommitteeMemberCard, CommunityStats,
│       │                   #   ContactsSection, IssuePreviewCard
│       ├── common/             # Shared UI components
│       ├── forms/              # Form components
│       ├── comments/           # Comments thread
│       ├── activity/           # Activity feed
│       ├── profile/            # Profile components
│       └── admin/              # Admin-only components
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

### Frontend Structure Details

#### `src/api/` — Axios Service Layer

Each service module wraps a domain's API calls and is imported directly by page components. Do not rename or remove functions — pages depend on them by name.

| File | Calls |
|------|-------|
| `client.js` | Base Axios instance with JWT interceptor |
| `authService.js` | `/auth/*` |
| `issueService.js` | `/issues/*` |
| `userService.js` | `/users/*` |
| `assetService.js` | `/assets/*`, `/bookings/*` |
| `commentService.js` | `/issues/{id}/comments` |
| `announcementService.js` | `/announcements/*` |
| `committeeService.js` | `/committee/*` |
| `events.js` | `/events/*` |
| `polls.js` | `/polls/*` |
| `feedbackService.js` | `/feedback/*` |
| `guidelineService.js` | `/guidelines/*` |
| `reportService.js` | `/reports/*` |
| `visitorService.js` | `/visitors/*` |
| `waterTankerService.js` | `/water-tanker/*` |
| `activityService.js` | `/issues/{id}/activity` |

#### `src/store/` — Redux State

- `authSlice.js` — Auth state (user, token, isAuthenticated). Consumed by every protected page. Do not change field names without updating all consumers.
- `index.js` — Redux store configuration

#### `src/theme.js` — Material-UI Theme

Centralised MUI theme: primary/secondary colours, typography, and component overrides. Change here to apply globally.

---

#### Frontend Configuration Files

**`package.json`** - Node Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@mui/material": "^5.14.0",
    "axios": "^1.6.0",
    "redux": "^5.0.0",
    "react-redux": "^9.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

**`vite.config.js`** - Vite Configuration
```javascript
export default {
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
}
```

---

## 📂 Additional Directories

### `.plans/` - Implementation Plans

**Purpose:** Store detailed implementation plans and design documents

```
.plans/
├── auth_implementation.md
├── file_upload_plan.md
├── user_management_plan.md
└── release_notes/
    ├── v1.0.0.md
    └── v1.1.0.md
```

**Usage:**
- Create plan before implementing features
- Document design decisions
- Track implementation progress

### `docs/` - Additional Documentation

**Purpose:** Extended documentation, guides, and tutorials

```
docs/
├── api_guide.md
├── deployment_guide.md
├── security_guide.md
└── troubleshooting.md
```

---

## 🗂️ Key File Relationships

### Backend Data Flow

```
Request → main.py (FastAPI app)
         ↓
      api/v1/endpoints/*.py (Route handlers)
         ↓
      services/*.py (Business logic)
         ↓
      models/*.py (Database ORM)
         ↓
      db/session.py (Database connection)
         ↓
      SQLite Database
```

### Authentication Flow

```
POST /auth/register
  → endpoints/auth.py (register)
  → services/auth_service.py (hash_password)
  → models/user.py (User.create)
  → Database

POST /auth/login
  → endpoints/auth.py (login)
  → services/auth_service.py (verify_password, create_token)
  → Return JWT token

GET /protected-endpoint
  → endpoints/*.py (depends on get_current_user)
  → services/auth_service.py (decode_token)
  → models/user.py (fetch user)
  → Execute endpoint logic
```

### Database Migration Flow

```
1. Modify models/*.py (change schema)
2. Run: alembic revision --autogenerate -m "description"
3. Review: alembic/versions/[new_file].py
4. Apply: alembic upgrade head
5. Test: python test_db_connection.py
```

---

## 📊 File Purpose Quick Reference

### Must Read Before Backend Changes
- `backend/API_IMPLEMENTATION_PLAN.md` - Feature roadmap
- `WORKFLOW.md` - Development procedures
- `backend/API_README.md` - API documentation

### Must Read Before Frontend Changes
- `frontend/README.md` - Setup and structure
- `ARCHITECTURE.md` - Design decisions

### Must Read Before Database Changes
- `backend/app/models/` - Current schema
- `backend/alembic/versions/` - Migration history

### Must Update After Changes
- `REFERENCE.md` - If APIs or schemas change
- `IMPLEMENTATION_CHECKLIST.md` - Mark features complete
- Relevant README files - If setup changes

---

## 🔍 Finding Things Quickly

### I Want To...

**Add a new API endpoint:**
1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Add schema in `backend/app/schemas/`
3. Update `backend/app/api/v1/api.py` to include router
4. Update `REFERENCE.md` with endpoint details

**Add a new database table:**
1. Create model in `backend/app/models/`
2. Export from `backend/app/models/__init__.py`
3. Import in `backend/alembic/env.py`
4. Run `alembic revision --autogenerate`
5. Review and apply migration

**Add business logic:**
1. Create service in `backend/app/services/`
2. Use service in endpoint handlers
3. Add tests in `backend/tests/`

**Add a new page:**
1. Create component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Create API calls in relevant service

**Configure settings:**
1. Add to `backend/app/core/config.py`
2. Add to `backend/.env.template`
3. Document in README

---

## 📝 Summary

### Directory Count
- **Backend Modules:** 7 directories, 20+ files
- **Frontend Modules:** 6 directories, 15+ files
- **Documentation:** 12+ markdown files
- **Configuration:** 8+ config files

### Key Locations
- **API Endpoints:** `backend/app/api/v1/endpoints/`
- **Database Models:** `backend/app/models/`
- **Business Logic:** `backend/app/services/`
- **React Components:** `frontend/src/components/`
- **API Client:** `frontend/src/api/`

### Important Files
1. `backend/app/main.py` - Application entry
2. `backend/app/core/config.py` - Configuration
3. `backend/alembic/env.py` - Migration setup
4. `frontend/src/App.jsx` - Frontend routing
5. `REFERENCE.md` - API reference

---

**Last Updated:** 2026-07-23  
**Version:** 1.0
