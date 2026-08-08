# 🤖 CommunityOS.ai - The Intelligent Operating System for Communities

**Status:** Backend Complete ✅ | Frontend Complete ✅  
**Version:** 2.0.0  
**Last Updated:** 2026-08-07

---

## 📖 Overview

**CommunityOS.ai** is an AI-powered SaaS platform designed to manage residential societies (100+ units) from possession through post-formation. The platform serves multiple organizations with complete data isolation, subscription-based billing, and intelligent automation.

### Vision
**"The Intelligent Operating System for Residential Communities"**

A complete operating system for residential societies — eliminating communication gaps, tracking issues efficiently, managing assets, events, polls, visitor logs, water tanker requests, and ensuring smooth community operations at scale.

---

## ✨ Implemented Features

### Backend ✅ COMPLETE
- ✅ **Authentication** — Registration, login, JWT tokens, password reset, admin approval workflow
- ✅ **Issue Management** — Full CRUD, status tracking, priority, category, issue numbers
- ✅ **Photo Upload** — Attach photos to issues (AWS S3 / Supabase Storage)
- ✅ **Comments & Activity** — Per-issue discussions and full activity audit trail
- ✅ **User Management** — Profiles, roles, pending approval queue, activation
- ✅ **Announcements** — Society-wide announcements with expiry
- ✅ **Events** — Create, edit, and manage community events
- ✅ **Polls** — Create polls, cast votes, auto-close via `active_till`
- ✅ **Committee Members** — Manage elected/appointed committee with roles
- ✅ **Asset & Facility Management** — Asset register, QR codes, facility bookings
- ✅ **Contractor Management** — Contractor profiles, assignments, work completions
- ✅ **Visitor Logs** — Visitor entry/exit tracking with host linkage
- ✅ **Water Tanker Orders** — Order management with vehicle details and departure time
- ✅ **Security Guidelines** — Post and manage safety/security notices
- ✅ **Feedback** — Resident feedback submissions
- ✅ **Reports** — Issue analytics, asset reports, contractor reports, CSV/PDF export
- ✅ **Audit Logs** — System-wide audit logging
- ✅ **Rate Limiting** — Per-IP rate limiter middleware
- ✅ **Security Headers** — OWASP-aligned response headers middleware

### Frontend ✅ COMPLETE
- ✅ **Authentication** — Login, Register, Forgot Password, Reset Password
- ✅ **Dashboard** — Stats cards, quick actions, announcement marquee, upcoming events, active polls, committee cards
- ✅ **Issue Management** — Issue list (filters/search), issue detail, create/edit issues
- ✅ **Announcements** — Browse and manage society announcements
- ✅ **Events** — Event listing, create/edit events
- ✅ **Polls** — Poll listing, vote, create/edit polls
- ✅ **Asset Management** — Asset list, asset detail, QR scanner
- ✅ **Facility Bookings** — My Bookings view
- ✅ **Reports** — Dashboard, issue analytics, asset reports, contractor reports, export
- ✅ **Admin Panel** — User management, pending approvals, committee management, asset management
- ✅ **Resident Directory** — Browse all residents
- ✅ **Security Page & Visitor Approval** — Security personnel view, visitor approvals
- ✅ **Water Tanker** — Order and track water tanker requests
- ✅ **Feedback** — Submit feedback
- ✅ **Profile** — View/edit profile, change password

---

## 🏗️ Architecture

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   React + Vite  │ ────> │ FastAPI (Python)  │ ────> │ SQLite / PG     │
│   Material-UI   │       │ SQLAlchemy ORM    │       │ (Supabase)      │
│   Redux Toolkit │       │ Alembic Migrations│       └─────────────────┘
└─────────────────┘       └──────────────────┘
     Frontend                   Backend               ┌─────────────────┐
                                    │                 │  AWS S3 /       │
                                    ├───────────────> │  Supabase Storage│
                                    │                 └─────────────────┘
                                    │                 ┌─────────────────┐
                                    └───────────────> │  Resend / SES   │
                                                      │  (Email)        │
                                                      └─────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend Framework | React 18 + Vite 5 |
| UI Components | Material-UI (MUI) v5 |
| State Management | Redux Toolkit |
| HTTP Client | Axios |
| Forms | React Hook Form + Zod |
| Charts | Recharts |
| QR Code | html5-qrcode, react-qr-code |
| Backend Framework | FastAPI (Python 3.12) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT (python-jose) |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL (Supabase) |
| File Storage | AWS S3 / Supabase Storage |
| Email | Resend / Amazon SES |
| Hosting (frontend) | Vercel |
| Hosting (backend) | Railway / AWS / GCP |

---

## 📁 Repository Structure

```
society_management_app/
├── readme.md                         # This file
├── AGENTS.md                         # AI agent guidance
├── ARCHITECTURE.md                   # System architecture
├── DEVELOPMENT_PLAN.md               # Project roadmap
├── IMPLEMENTATION_CHECKLIST.md       # Feature completion tracker
├── INDEX.md                          # Folder & service index
├── PROJECT_SUMMARY.md                # High-level overview
├── QUICKSTART.md                     # Setup guide
├── REFERENCE.md                      # API & schema reference
├── WORKFLOW.md                       # Development workflow
├── CONTRIBUTING.md                   # Contribution guidelines
│
├── backend/                          # FastAPI REST API
│   ├── app/
│   │   ├── main.py                   # Application entry point & middleware stack
│   │   ├── api/v1/
│   │   │   ├── api.py                # Router aggregation
│   │   │   ├── events.py             # Events router
│   │   │   ├── polls.py              # Polls router
│   │   │   └── endpoints/
│   │   │       ├── auth.py           # /auth/*
│   │   │       ├── users.py          # /users/*
│   │   │       ├── issues.py         # /issues/*
│   │   │       ├── photos.py         # /issues/{id}/photos
│   │   │       ├── comments.py       # /issues/{id}/comments
│   │   │       ├── announcements.py  # /announcements/*
│   │   │       ├── assets.py         # /assets/*
│   │   │       ├── bookings.py       # /bookings/*
│   │   │       ├── committee.py      # /committee/*
│   │   │       ├── contractors.py    # /contractors/*
│   │   │       ├── feedback.py       # /feedback/*
│   │   │       ├── guidelines.py     # /guidelines/*
│   │   │       ├── reports.py        # /reports/*
│   │   │       ├── visitors.py       # /visitors/*
│   │   │       ├── water_tanker.py   # /water-tanker/*
│   │   │       └── work_completions.py
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── issue.py
│   │   │   ├── comment.py
│   │   │   ├── activity.py
│   │   │   ├── announcement.py
│   │   │   ├── asset.py
│   │   │   ├── audit_log.py
│   │   │   ├── committee_member.py
│   │   │   ├── contractor.py
│   │   │   ├── event.py
│   │   │   ├── feedback.py
│   │   │   ├── guideline.py
│   │   │   ├── organization.py
│   │   │   ├── poll.py
│   │   │   ├── settings.py
│   │   │   ├── subscription.py
│   │   │   ├── visitor.py
│   │   │   └── water_tanker.py
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                 # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── announcement_service.py
│   │   │   ├── asset_service.py
│   │   │   ├── audit_service.py
│   │   │   ├── committee_service.py
│   │   │   ├── contractor_service.py
│   │   │   ├── email_service.py
│   │   │   ├── event_service.py
│   │   │   ├── feedback_service.py
│   │   │   ├── guideline_service.py
│   │   │   ├── poll_service.py
│   │   │   ├── report_service.py
│   │   │   ├── s3_service.py
│   │   │   └── visitor_service.py
│   │   ├── core/                     # Config, security, dependencies
│   │   ├── db/                       # Database session & base
│   │   └── middleware/
│   │       ├── security_headers.py   # OWASP security headers
│   │       ├── logging_middleware.py # Request/response logging
│   │       └── rate_limiter.py       # Per-IP rate limiting
│   ├── alembic/versions/             # 28 migration files
│   ├── tests/                        # Pytest test suite
│   │   ├── test_auth.py
│   │   ├── test_issues.py
│   │   ├── test_users.py
│   │   ├── test_photos.py
│   │   ├── test_comments.py
│   │   ├── test_bookings.py
│   │   ├── test_contractors.py
│   │   └── test_assets.py
│   └── requirements.txt
│
├── frontend/                         # React + Vite SPA
│   ├── src/
│   │   ├── App.jsx                   # Root component & route definitions
│   │   ├── main.jsx                  # Entry point
│   │   ├── theme.js                  # MUI theme configuration
│   │   ├── api/                      # Axios service layer
│   │   │   ├── client.js             # Axios instance with auth interceptors
│   │   │   ├── authService.js
│   │   │   ├── issueService.js
│   │   │   ├── userService.js
│   │   │   ├── assetService.js
│   │   │   ├── commentService.js
│   │   │   ├── announcementService.js
│   │   │   ├── committeeService.js
│   │   │   ├── events.js
│   │   │   ├── polls.js
│   │   │   ├── feedbackService.js
│   │   │   ├── guidelineService.js
│   │   │   ├── reportService.js
│   │   │   ├── visitorService.js
│   │   │   ├── waterTankerService.js
│   │   │   └── activityService.js
│   │   ├── store/                    # Redux state (authSlice)
│   │   ├── pages/
│   │   │   ├── auth/                 # Login, Register, ForgotPassword, ResetPassword
│   │   │   ├── Dashboard.jsx
│   │   │   ├── issues/               # IssueList, IssueDetail, CreateIssue, EditIssue
│   │   │   ├── assets/               # AssetList, AssetDetail, QRScanner
│   │   │   ├── bookings/             # MyBookings
│   │   │   ├── reports/              # ReportsDashboard, IssueAnalytics, AssetReports,
│   │   │   │                         #   ContractorReports, ExportReports
│   │   │   ├── admin/                # Users, PendingUsers, CommitteeManagement,
│   │   │   │                         #   AssetManagement
│   │   │   ├── AnnouncementManagement.jsx
│   │   │   ├── Events.jsx / CreateEvent.jsx / EditEvent.jsx
│   │   │   ├── Polls.jsx / CreatePoll.jsx / EditPoll.jsx
│   │   │   ├── ResidentDirectory.jsx
│   │   │   ├── SecurityPage.jsx
│   │   │   ├── VisitorApproval.jsx
│   │   │   ├── WaterTanker.jsx
│   │   │   ├── Feedback.jsx
│   │   │   └── Profile.jsx / EditProfile.jsx / ChangePassword.jsx
│   │   └── components/
│   │       ├── layout/               # MainLayout, AuthLayout, AppBar, Sidebar, UserMenu
│   │       ├── dashboard/            # StatCard, QuickActions, AnnouncementMarquee,
│   │       │                         #   UpcomingEvents, ActivePollWidget,
│   │       │                         #   CommitteeMemberCard, CommunityStats,
│   │       │                         #   ContactsSection, IssuePreviewCard
│   │       ├── common/               # Shared UI components
│   │       ├── forms/                # Form components
│   │       ├── comments/             # Comments thread
│   │       ├── activity/             # Activity feed
│   │       ├── profile/              # Profile components
│   │       └── admin/                # Admin-only components
│   └── package.json
│
└── docs/                             # Extended documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**API:** http://127.0.0.1:8000  
**Swagger UI:** http://127.0.0.1:8000/api/docs  
**ReDoc:** http://127.0.0.1:8000/api/redoc

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

**App:** http://localhost:5173

See [QUICKSTART.md](QUICKSTART.md) for detailed setup including environment variables.

---

## 📊 Current Status

### Backend ✅ COMPLETE
- **40+ API endpoints** across 17 endpoint modules
- **28 Alembic migrations** applied
- **8 test modules** covering auth, issues, users, photos, comments, bookings, contractors, assets
- Middleware stack: Rate Limiter → Logging → Security Headers → GZip → CORS

### Frontend ✅ COMPLETE
- **20+ pages** fully implemented
- **9 component groups** with reusable UI
- **16 API service modules** covering all backend endpoints
- Redux Toolkit for auth state; Axios interceptors for token handling

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | Setup guide |
| [REFERENCE.md](REFERENCE.md) | Full API & schema reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & decisions |
| [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) | Project roadmap |
| [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) | Feature completion tracker |
| [INDEX.md](INDEX.md) | Folder & service index |
| [backend/API_README.md](backend/API_README.md) | Backend API documentation |
| [backend/API_IMPLEMENTATION_PLAN.md](backend/API_IMPLEMENTATION_PLAN.md) | Backend build plan |
| [AGENTS.md](AGENTS.md) | AI agent guidance |
| [WORKFLOW.md](WORKFLOW.md) | Development workflow |

---

## 🎯 Modules Overview

| Module | Backend | Frontend |
|--------|---------|---------|
| Authentication | ✅ | ✅ |
| Issue Management | ✅ | ✅ |
| Photo Upload | ✅ | ✅ |
| Comments & Activity | ✅ | ✅ |
| User Management | ✅ | ✅ |
| Announcements | ✅ | ✅ |
| Events | ✅ | ✅ |
| Polls & Voting | ✅ | ✅ |
| Committee Members | ✅ | ✅ |
| Asset & Facility Mgmt | ✅ | ✅ |
| Facility Bookings | ✅ | ✅ |
| Contractor Management | ✅ | ✅ |
| Visitor Logs | ✅ | ✅ |
| Water Tanker Orders | ✅ | ✅ |
| Security Guidelines | ✅ | ✅ |
| Feedback | ✅ | ✅ |
| Reports & Analytics | ✅ | ✅ |
| Audit Logs | ✅ | — |
| QR Code Scanning | ✅ | ✅ |

---

## 👥 User Roles

| Role | Description |
|------|-------------|
| `RESIDENT` | Report issues, view own data, participate in polls/events |
| `CONTRACTOR` | View assigned issues, submit work completions |
| `BUILDER` | Manage all issues, view reports |
| `ADMIN` | Full access — user management, all modules |
| `SECURITY` | Visitor logs, security guidelines, entry management |
| `FACILITY` | Manage assets, bookings, and common areas |

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

Tests cover: authentication, issue CRUD, user management, photo upload, comments, bookings, contractors, assets.

---
## 🤖 Agent-Based Development Guide

This project is designed for AI-assisted development via GitHub Copilot (agent mode). Follow this workflow to add any new feature without breaking existing functionality.

### How It Works

```
You (fill plan) → Agent (implements code + updates docs) → You (verify & commit)
```

### Step 1 — Create a feature plan

```bash
# Copy the canonical template
cp .plans/FEATURE_TEMPLATE.md .plans/[feature-name].md
```

Fill in **every section** of the plan:

| Section | What to fill |
|---------|-------------|
| **1. Objective** | What it does, user stories, out-of-scope |
| **2. Backward Compatibility Gate** | Confirm nothing existing will break |
| **3. Backend** | Models, migration, schemas, service functions, endpoint table |
| **4. Frontend** | Pages, routes, API service functions, sidebar nav item |
| **5. Agent Execution Order** | Pre-filled — do not change |
| **6–7. Verification + Docs** | Pre-filled checklists |

### Step 2 — Start agent mode in VS Code

Open Copilot Chat → switch to **Agent mode** → paste this prompt:

```
Read `AGENTS.md` first, then implement everything described in
`.plans/[feature-name].md` following the Agent Execution Order in Section 5.
After implementation, run all verifications in Section 6 and update all
documentation listed in Section 7.
```

### Step 3 — Agent executes in 4 phases (automatically)

```
Phase 1 — Backend Foundation
  model → migration → alembic upgrade head
  ✅ VERIFY: uvicorn app.main:app --reload starts

Phase 2 — Backend API
  schemas → service → endpoint file → register in api.py
  ✅ VERIFY: new endpoints in Swagger UI

Phase 3 — Frontend
  API service → pages → routes in App.jsx → sidebar item
  ✅ VERIFY: npm run dev compiles, pages load

Phase 4 — Documentation
  REFERENCE.md → AGENTS.md → IMPLEMENTATION_CHECKLIST.md → INDEX.md
  ✅ VERIFY: no stale "Planned" text in updated docs
```

### Rules the agent must follow (encoded in [AGENTS.md](AGENTS.md))

- Never rename or remove an existing endpoint path — add new ones only
- Never edit existing Alembic migration files — always create a new one
- Never remove a Pydantic response field — only add `Optional` fields
- Never change a frontend route — add new routes alongside existing ones
- Verify backend starts before touching frontend
- Verify frontend compiles before updating documentation

### Key files

| File | Purpose |
|------|---------|
| [AGENTS.md](AGENTS.md) | Full agent rules, live endpoint/page tables |
| [.plans/FEATURE_TEMPLATE.md](.plans/FEATURE_TEMPLATE.md) | Feature plan template |
| [WORKFLOW.md](WORKFLOW.md) | Step-by-step development workflow |
| [REFERENCE.md](REFERENCE.md) | All API endpoints and schemas |

---
## 🚀 Deployment

### Backend
- **Platform:** Railway, AWS, GCP, or Heroku
- **Database:** Supabase PostgreSQL or AWS RDS
- **Storage:** AWS S3 or Supabase Storage
- **Build:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Frontend
- **Platform:** Vercel (recommended)
- **Build:** `npm run build`
- **Output:** `dist/`

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Git workflow:**
1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit: `git commit -m 'feat: description'`
3. Push & open Pull Request

> **Note:** Agents must never run git commands without explicit user instruction — see [AGENTS.md](AGENTS.md).

---

## 📄 License

Proprietary software. All rights reserved.

---

## 🙏 Acknowledgments

Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [Material-UI](https://mui.com/), [Vite](https://vitejs.dev/), [Supabase](https://supabase.com/), and [AWS S3](https://aws.amazon.com/s3/).

