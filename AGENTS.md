# CommunityOS.ai - Agent Guidance

## What This Workspace Is

**CommunityOS.ai** (formerly Riverdale Connect) is an AI-powered SaaS platform for managing residential society operations from possession through post-formation. It's a multi-tenant application designed to scale to serve multiple societies with 100+ units each. It consists of:

- **Backend:** FastAPI-based REST API with SQLAlchemy ORM and SQLite/PostgreSQL database
- **Frontend:** React + Vite application with Material-UI
- **Architecture:** Monorepo structure with independent backend and frontend folders

---

## Specification & Planning

### Development is Specification-Driven

All development follows documented specifications and plans:

- **Primary Documents:**
  - [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - High-level project overview
  - [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture and design decisions
  - [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) - Overall project roadmap
  - [backend/API_IMPLEMENTATION_PLAN.md](./backend/API_IMPLEMENTATION_PLAN.md) - Detailed backend roadmap

- **Technical References:**
  - [backend/API_README.md](./backend/API_README.md) - Complete API documentation
  - [backend/QUICK_REFERENCE.md](./backend/QUICK_REFERENCE.md) - Quick command reference
  - [REFERENCE.md](./REFERENCE.md) - Comprehensive API and service reference

**Rule:** Consult relevant specification documents before making any code changes.

---

## Workflow

**MANDATORY:** Load [WORKFLOW.md](./WORKFLOW.md) before performing any code changes.

The workflow document contains:
- Planning and verification steps
- Code change procedures
- Testing requirements
- Documentation requirements
- Pull request guidelines
- Release note updates

**Key Workflow Rules:**
1. Always generate and review a plan before implementing changes
2. Update documentation when code changes affect APIs or configurations
3. Test locally before committing
4. Update [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md) for completed features
5. Document breaking changes in release notes

---

## Project Structure

Load [INDEX.md](./INDEX.md) for detailed folder structure and service descriptions.

### Top-Level Organization

```
society_management_app/
├── backend/           # FastAPI REST API
├── frontend/          # React + Vite web app
├── docs/              # Additional documentation
└── .plans/            # Implementation plans and notes
```

**Backend Services (all live ✅ — do not break):**
- Authentication & JWT (login, register, password reset, admin approval)
- User management & roles
- Issue tracking with photos, comments, activity logs
- Announcements
- Events
- Polls & voting
- Committee member management
- Asset & facility management + bookings
- Contractor management & work completions
- Visitor logs
- Water tanker orders
- Security guidelines
- Feedback
- Reports & analytics
- File uploads (S3/Supabase)
- Email notifications
- Audit logs

**Frontend Features (all live ✅ — do not break):**
- Authentication (login, register, forgot/reset password)
- Dashboard with stats, announcements, events, polls, committee widgets
- Issue management (list, detail, create, edit)
- Announcements management
- Events (list, create, edit)
- Polls (list, vote, create, edit)
- Asset management + QR scanner
- Facility bookings
- Reports & analytics dashboard
- Admin panel (users, pending approvals, committee, assets)
- Resident directory
- Security page & visitor approvals
- Water tanker orders
- Feedback
- Profile management

---

## API & Functional Reference

Load [REFERENCE.md](./REFERENCE.md) for:
- All API endpoints with methods and descriptions
- Request/response schemas
- Database models and relationships
- Environment variables
- Service configurations

**When to Update REFERENCE.md:**
- Adding new API endpoints
- Modifying endpoint signatures
- Changing database schema
- Adding/removing environment variables
- Updating service configurations

---

## Environment Management

### Virtual Environment

**Python Backend:**
```bash
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

**Important:** Always use the project's `.venv` directory. Never create new virtual environments.

### Environment Variables

All environment variables are documented in [backend/.env.template](./backend/.env.template)

**Required for Backend:**
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key
- `CORS_ORIGINS` - Allowed frontend origins

**Optional Services:**
- AWS S3 credentials (for file uploads)
- Resend API key (for email notifications)
- Supabase credentials (if using Supabase)

---

## Development Rules

### Code Changes

1. **Always Plan First**
   - Read relevant specifications
   - Review existing code
   - Create implementation plan
   - Get user approval for significant changes

2. **Test Locally**
   - Backend: Run `uvicorn app.main:app --reload`
   - Frontend: Run `npm run dev`
   - Test endpoints in Swagger UI (http://127.0.0.1:8000/api/docs)
   - Verify database migrations work

3. **Update Documentation**
   - Update API docs if endpoints change
   - Update README if setup changes
   - Update REFERENCE.md if schemas change
   - Update implementation checklist

4. **Database Migrations**
   - Always use Alembic for schema changes
   - Test migrations: `alembic upgrade head`
   - Never modify database directly in production

### Testing Strategy

**Backend Testing:**
- Manual testing via Swagger UI for new features
- Unit tests for services (when implemented)
- Integration tests for API endpoints (when implemented)
- Database connection tests: `python test_local_db.py`

**Frontend Testing:**
- Manual browser testing
- Component testing (to be implemented)
- E2E tests (to be implemented)

**Rule:** Testing is primarily user-driven unless explicitly requested by the user.

---

## Database Operations

### Local Development (SQLite)

```bash
# Test connection
python test_local_db.py

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Production (PostgreSQL/Supabase)

- Never modify production database directly
- Always test migrations locally first
- Use connection pooling
- Enable SSL connections

---

## Deployment & Environments

### Local Development
- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:5173
- Database: SQLite file (`backend/society_app.db`)

### Production (Future)
- Cloud deployment (Railway/AWS/GCP)
- PostgreSQL database
- Environment-specific configs
- CI/CD pipeline

**Rule:** Never test new features on production. Always test locally first.

---

## Git & Version Control

### Commit Guidelines

**Good Commits:**
- Clear, descriptive messages
- Single feature/fix per commit
- Reference issue numbers if applicable

**Examples:**
```
✅ feat: Add file upload endpoint for issue photos
✅ fix: Resolve JWT token validation error
✅ docs: Update API reference with new endpoints
✅ refactor: Extract auth logic into service layer
```

### Git Operations

**Important:** Agents should **NEVER** perform git operations unless explicitly asked by the user.

This includes:
- ❌ `git add`
- ❌ `git commit`
- ❌ `git push`
- ❌ `git pull`
- ❌ `git merge`
- ❌ `git checkout`

**Why:** User maintains control over version control decisions.

---

## Never Do This

### Absolutely Forbidden

1. **Never delete database files** (`society_app.db`)
2. **Never delete `.venv` folder** (virtual environment)
3. **Never modify `.env` file** (contains secrets)
4. **Never commit sensitive data** (API keys, passwords)
5. **Never delete migration files** (in `alembic/versions/`)
6. **Never bypass authentication** in production code
7. **Never hard-code credentials** in source files
8. **Never modify production databases** directly
9. **Never rename or remove existing API endpoint paths** — the frontend depends on them
10. **Never remove or rename model fields/columns** without a new Alembic migration
11. **Never change an existing migration file** — create a new one instead
12. **Never remove or rename existing frontend API service functions** — pages depend on them
13. **Never change Redux store slice structure** without updating all consumers

### Handle With Care

1. **Migration files** — test thoroughly before applying; always create new ones, never edit existing
2. **Configuration files** — always create backups
3. **Environment variables** — use `.env.template` as reference
4. **Dependencies** — document all new packages in `requirements.txt` / `package.json`
5. **Breaking changes** — clearly document and communicate
6. **Pydantic schemas** — removing a field is a breaking change for the frontend
7. **React routing** — changing a route path breaks navigation and direct links
8. **Redux authSlice** — any structural change requires updating all components that consume it

---

## Preserving Existing Functionality

**This is a fully implemented production-ready application. Every feature listed below is live. Any change that breaks these must be treated as a critical regression.**

### Backend — Live Endpoints (do not modify paths or signatures)

| Module | Path Prefix | Must Not Break |
|--------|-------------|----------------|
| Auth | `/api/v1/auth/` | login, register, password reset, admin approval |
| Users | `/api/v1/users/` | list, get, update, role management |
| Issues | `/api/v1/issues/` | CRUD, filters, issue numbers |
| Photos | `/api/v1/issues/{id}/photos` | upload, list, delete |
| Comments | `/api/v1/issues/{id}/comments` | CRUD, activity |
| Announcements | `/api/v1/announcements/` | CRUD |
| Events | `/api/v1/events/` | CRUD |
| Polls | `/api/v1/polls/` | CRUD, voting |
| Committee | `/api/v1/committee/` | CRUD |
| Assets | `/api/v1/assets/` | CRUD, QR |
| Bookings | `/api/v1/bookings/` | CRUD |
| Contractors | `/api/v1/contractors/` | CRUD, assignments, ratings |
| Visitors | `/api/v1/visitors/` | CRUD |
| Water Tanker | `/api/v1/water-tanker/` | CRUD |
| Guidelines | `/api/v1/guidelines/` | CRUD |
| Feedback | `/api/v1/feedback/` | CRUD |
| Reports | `/api/v1/reports/` | analytics, export |

### Frontend — Live Pages (do not change routes or remove components)

| Page | Route | API Service |
|------|-------|-------------|
| Login | `/login` | authService |
| Register | `/register` | authService |
| Dashboard | `/dashboard` | multiple |
| Issue List | `/issues` | issueService |
| Issue Detail | `/issues/:id` | issueService, commentService |
| Create Issue | `/issues/create` | issueService |
| Assets | `/assets` | assetService |
| Bookings | `/bookings` | assetService |
| Reports | `/reports` | reportService |
| Admin Users | `/admin/users` | userService |
| Admin Pending | `/admin/pending-users` | userService |
| Committee Mgmt | `/admin/committee` | committeeService |
| Events | `/events` | events.js |
| Polls | `/polls` | polls.js |
| Announcements | `/announcements` | announcementService |
| Water Tanker | `/water-tanker` | waterTankerService |
| Visitor Approval | `/visitor-approval` | visitorService |
| Security | `/security` | guidelineService |
| Feedback | `/feedback` | feedbackService |
| Profile | `/profile` | userService |

### Before Adding Any New Feature

1. **Read existing code first** — grep for related patterns before writing new ones
2. **Check for existing service/endpoint** — it may already exist
3. **Add new routes, never rename old ones** — the frontend calls old paths
4. **Create a new Alembic migration** for any schema change — never alter existing migrations
5. **Add new Pydantic schema fields as Optional** when backward compatibility matters
6. **Add new Redux actions** without removing existing ones
7. **Verify the backend runs** (`uvicorn app.main:app --reload`) after backend changes
8. **Verify the frontend compiles** (`npm run dev`) after frontend changes

---

## Assistance Guidelines

### How to Add a New Feature (Standard Process)

1. Copy `.plans/FEATURE_TEMPLATE.md` → `.plans/[feature-name].md`
2. Fill in every section (objective, models, schemas, services, endpoints, pages, routes, verification)
3. Paste this prompt into Copilot/agent chat:

   > "Read `AGENTS.md` first, then implement everything described in `.plans/[feature-name].md` following the Agent Execution Order in Section 5. After implementation, run all verifications in Section 6 and update all documentation listed in Section 7."

4. The agent will complete all phases in order and update all `.md` files automatically.

**Key rules the agent follows from the plan:**
- Backend first (model → migration → schema → service → endpoint)
- Verify backend starts before moving to frontend
- Frontend second (service → pages → routes → sidebar)
- Verify frontend compiles before updating docs
- Documentation last (REFERENCE.md, AGENTS.md, IMPLEMENTATION_CHECKLIST.md, INDEX.md)

---

### When Asked to Implement Features

1. **Read the specification** - Check implementation plan
2. **Review existing code** - Understand current architecture
3. **Create detailed plan** - List all files to modify
4. **Implement systematically** - Follow established patterns
5. **Test thoroughly** - Verify functionality works
6. **Update documentation** - Keep docs in sync

### When Asked to Debug

1. **Gather context** - Read error messages, check logs
2. **Review related code** - Understand the failing component
3. **Propose solution** - Explain the fix before implementing
4. **Test the fix** - Verify the issue is resolved
5. **Document** - Update troubleshooting guides if needed

### When Asked to Review Code

1. **Check against standards** - Follow Python/JS best practices
2. **Security review** - Look for vulnerabilities
3. **Performance review** - Identify bottlenecks
4. **Documentation review** - Ensure code is well-documented
5. **Testing review** - Verify tests cover main paths

---

## Key Files to Consult

### Before Any Backend Change
- [backend/API_IMPLEMENTATION_PLAN.md](./backend/API_IMPLEMENTATION_PLAN.md)
- [backend/API_README.md](./backend/API_README.md)
- [REFERENCE.md](./REFERENCE.md)

### Before Any Frontend Change
- [frontend/README.md](./frontend/README.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)

### Before Database Changes
- [backend/app/models/](./backend/app/models/) - Review existing models
- [backend/alembic/versions/](./backend/alembic/versions/) - Review migration history

### For Project Overview
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- [QUICKSTART.md](./QUICKSTART.md)
- [INDEX.md](./INDEX.md)

---

## Communication Protocol

### With User

- **Be explicit** about what files will be changed
- **Ask for confirmation** for significant changes
- **Explain trade-offs** when multiple approaches exist
- **Provide examples** for complex implementations
- **Document assumptions** when information is unclear

### Code Comments

- Explain **why**, not just **what**
- Document complex business logic
- Reference specification documents
- Note TODOs for future improvements
- Mark deprecated code clearly

---

## Version Information

- **Project:** CommunityOS.ai (formerly Riverdale Connect)
- **Version:** 2.0.0
- **Backend:** FastAPI 0.109.0 + SQLAlchemy 2.0.25 — **40+ endpoints, 28 migrations live**
- **Frontend:** React 18 + Vite 5 — **20+ pages fully implemented**
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Last Updated:** 2026-08-07

---

## Quick Links

- 📖 [Full Workflow](./WORKFLOW.md)
- 📁 [Project Structure](./INDEX.md)
- 🔗 [API Reference](./REFERENCE.md)
- 🚀 [Quick Start](./QUICKSTART.md)
- 📋 [Implementation Plan](./backend/API_IMPLEMENTATION_PLAN.md)
