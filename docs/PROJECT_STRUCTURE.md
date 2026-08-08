# Riverdale Connect - Project Structure

Complete repository structure and organization for the Riverdale Connect application.

## Root Directory Structure

```
society_management_app/
├── backend/                    # FastAPI backend application
├── frontend/                   # React frontend application
├── docs/                       # Documentation files
│   ├── api/                   # API documentation
│   ├── user-guides/           # User manuals
│   └── developer-guides/      # Developer documentation
├── scripts/                    # Utility scripts
│   ├── deployment/            # Deployment scripts
│   ├── database/              # Database scripts
│   └── testing/               # Test scripts
├── .github/                    # GitHub workflows and configurations
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       └── deploy-prod.yml
├── .gitignore                 # Git ignore rules
├── readme.md                  # Project overview
├── DEVELOPMENT_PLAN.md        # Comprehensive development plan
├── ARCHITECTURE.md            # System architecture documentation
├── PROJECT_STRUCTURE.md       # This file
├── CONTRIBUTING.md            # Contribution guidelines
└── LICENSE                    # License information
```

---

## Backend Structure (Detailed)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI application entry
│   │
│   ├── api/                              # API layer
│   │   ├── __init__.py
│   │   ├── deps.py                       # Dependencies (auth, db session)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py                    # API router aggregation
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py               # /auth/* endpoints
│   │           ├── issues.py             # /issues/* endpoints
│   │           ├── contractors.py        # /contractors/* endpoints
│   │           ├── assets.py             # /assets/* endpoints
│   │           ├── reports.py            # /reports/* endpoints
│   │           ├── qrcodes.py            # /qrcodes/* endpoints
│   │           └── users.py              # /users/* endpoints
│   │
│   ├── core/                             # Core configurations
│   │   ├── __init__.py
│   │   ├── config.py                     # Settings & environment
│   │   ├── security.py                   # Security utilities
│   │   └── logging.py                    # Logging configuration
│   │
│   ├── models/                           # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py                       # User model
│   │   ├── issue.py                      # Issue & IssuePhoto models
│   │   ├── contractor.py                 # Contractor model
│   │   ├── asset.py                      # Asset model
│   │   ├── qrcode.py                     # QRCode model
│   │   ├── material_movement.py          # MaterialMovement model
│   │   └── report.py                     # Report model
│   │
│   ├── schemas/                          # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py                       # User request/response schemas
│   │   ├── issue.py                      # Issue request/response schemas
│   │   ├── contractor.py                 # Contractor schemas
│   │   ├── asset.py                      # Asset schemas
│   │   ├── report.py                     # Report schemas
│   │   └── response.py                   # Standard response models
│   │
│   ├── services/                         # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py               # Authentication logic
│   │   ├── issue_service.py              # Issue management logic
│   │   ├── contractor_service.py         # Contractor management
│   │   ├── asset_service.py              # Asset management
│   │   ├── s3_service.py                 # AWS S3 file operations
│   │   ├── email_service.py              # Email sending
│   │   ├── pdf_service.py                # PDF generation
│   │   └── qrcode_service.py             # QR code generation
│   │
│   ├── db/                               # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py                       # Base model & imports
│   │   ├── session.py                    # Database session
│   │   └── init_db.py                    # Database initialization
│   │
│   └── utils/                            # Utility functions
│       ├── __init__.py
│       ├── validators.py                 # Validation utilities
│       ├── formatters.py                 # Data formatters
│       └── constants.py                  # Application constants
│
├── alembic/                              # Database migrations
│   ├── versions/                         # Migration files
│   ├── env.py                            # Alembic environment
│   └── script.py.mako                    # Migration template
│
├── tests/                                # Test suite
│   ├── __init__.py
│   ├── conftest.py                       # Pytest fixtures
│   ├── api/                              # API endpoint tests
│   │   ├── test_auth.py
│   │   ├── test_issues.py
│   │   └── test_contractors.py
│   ├── services/                         # Service layer tests
│   │   ├── test_auth_service.py
│   │   └── test_issue_service.py
│   └── utils/                            # Utility tests
│
├── .env.example                          # Environment template
├── .env                                  # Environment variables (gitignored)
├── requirements.txt                      # Python dependencies
├── requirements-dev.txt                  # Development dependencies
├── alembic.ini                           # Alembic configuration
├── pytest.ini                            # Pytest configuration
├── pyproject.toml                        # Python project metadata
├── Dockerfile                            # Docker configuration
└── README.md                             # Backend documentation
```

---

## Frontend Structure (Detailed)

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── robots.txt
│   ├── manifest.json                     # PWA manifest
│   ├── apple-touch-icon.png
│   ├── pwa-192x192.png
│   └── pwa-512x512.png
│
├── src/
│   ├── main.jsx                          # Application entry point
│   ├── App.jsx                           # Main app component
│   ├── index.css                         # Global styles
│   ├── theme.js                          # MUI theme configuration
│   │
│   ├── api/                              # API layer
│   │   ├── client.js                     # Axios configuration
│   │   ├── auth.js                       # Auth API calls
│   │   ├── issues.js                     # Issues API calls
│   │   ├── contractors.js                # Contractors API calls
│   │   ├── assets.js                     # Assets API calls
│   │   ├── reports.js                    # Reports API calls
│   │   └── qrcodes.js                    # QR codes API calls
│   │
│   ├── components/                       # React components
│   │   ├── common/                       # Shared components
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── Layout.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Loader.jsx
│   │   │   ├── ErrorBoundary.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   │
│   │   ├── issues/                       # Issue components
│   │   │   ├── IssueForm.jsx
│   │   │   ├── IssueCard.jsx
│   │   │   ├── IssueList.jsx
│   │   │   ├── IssueDetails.jsx
│   │   │   ├── IssueFilter.jsx
│   │   │   └── IssueStatusBadge.jsx
│   │   │
│   │   ├── contractors/                  # Contractor components
│   │   │   ├── ContractorCard.jsx
│   │   │   ├── ContractorList.jsx
│   │   │   ├── ContractorForm.jsx
│   │   │   └── ContractorRating.jsx
│   │   │
│   │   ├── assets/                       # Asset components
│   │   │   ├── AssetCard.jsx
│   │   │   ├── AssetList.jsx
│   │   │   └── AssetForm.jsx
│   │   │
│   │   ├── qrcode/                       # QR code components
│   │   │   ├── QRScanner.jsx
│   │   │   ├── QRGenerator.jsx
│   │   │   └── QRDisplay.jsx
│   │   │
│   │   ├── upload/                       # Upload components
│   │   │   ├── PhotoUpload.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   └── ImagePreview.jsx
│   │   │
│   │   ├── charts/                       # Chart components
│   │   │   ├── IssueChart.jsx
│   │   │   ├── StatusChart.jsx
│   │   │   └── TrendChart.jsx
│   │   │
│   │   └── reports/                      # Report components
│   │       ├── WeeklyReport.jsx
│   │       └── ReportViewer.jsx
│   │
│   ├── pages/                            # Page components
│   │   ├── Login.jsx                     # Login page
│   │   ├── Register.jsx                  # Registration page
│   │   ├── Dashboard.jsx                 # Main dashboard
│   │   ├── Issues.jsx                    # Issues page
│   │   ├── IssueDetails.jsx              # Issue details page
│   │   ├── CreateIssue.jsx               # Create issue page
│   │   ├── Contractors.jsx               # Contractors page
│   │   ├── Assets.jsx                    # Assets page
│   │   ├── Reports.jsx                   # Reports page
│   │   ├── Profile.jsx                   # User profile page
│   │   ├── Settings.jsx                  # Settings page
│   │   └── NotFound.jsx                  # 404 page
│   │
│   ├── store/                            # Redux store
│   │   ├── index.js                      # Store configuration
│   │   ├── authSlice.js                  # Auth state management
│   │   ├── issuesSlice.js                # Issues state management
│   │   ├── contractorsSlice.js           # Contractors state
│   │   ├── assetsSlice.js                # Assets state
│   │   └── uiSlice.js                    # UI state (loading, errors)
│   │
│   ├── hooks/                            # Custom React hooks
│   │   ├── useAuth.js                    # Authentication hook
│   │   ├── useIssues.js                  # Issues data hook
│   │   ├── useDebounce.js                # Debounce hook
│   │   └── useLocalStorage.js            # LocalStorage hook
│   │
│   ├── utils/                            # Utility functions
│   │   ├── constants.js                  # App constants
│   │   ├── validators.js                 # Form validators
│   │   ├── formatters.js                 # Data formatters
│   │   ├── helpers.js                    # Helper functions
│   │   └── storage.js                    # LocalStorage wrapper
│   │
│   └── styles/                           # Additional styles
│       ├── variables.css                 # CSS variables
│       └── animations.css                # CSS animations
│
├── .env.example                          # Environment template
├── .env                                  # Environment variables (gitignored)
├── .env.development                      # Development environment
├── .env.production                       # Production environment
├── package.json                          # NPM dependencies
├── package-lock.json                     # NPM lock file
├── vite.config.js                        # Vite configuration
├── .eslintrc.json                        # ESLint configuration
├── .prettierrc                           # Prettier configuration
├── index.html                            # HTML template
├── Dockerfile                            # Docker configuration
└── README.md                             # Frontend documentation
```

---

## Documentation Structure

```
docs/
├── api/
│   ├── authentication.md                 # Auth API docs
│   ├── issues.md                         # Issues API docs
│   ├── contractors.md                    # Contractors API docs
│   └── postman-collection.json           # Postman collection
│
├── user-guides/
│   ├── resident-guide.md                 # Guide for residents
│   ├── contractor-guide.md               # Guide for contractors
│   ├── builder-guide.md                  # Guide for builders
│   └── admin-guide.md                    # Guide for admins
│
├── developer-guides/
│   ├── setup-guide.md                    # Development setup
│   ├── coding-standards.md               # Coding conventions
│   ├── deployment-guide.md               # Deployment instructions
│   └── troubleshooting.md                # Common issues
│
└── diagrams/
    ├── architecture-diagram.png
    ├── database-schema.png
    └── workflow-diagrams/
```

---

## Scripts Structure

```
scripts/
├── deployment/
│   ├── deploy-backend.sh                 # Deploy backend script
│   ├── deploy-frontend.sh                # Deploy frontend script
│   └── rollback.sh                       # Rollback script
│
├── database/
│   ├── seed-data.sql                     # Seed database
│   ├── backup.sh                         # Backup script
│   └── restore.sh                        # Restore script
│
└── testing/
    ├── run-tests.sh                      # Run all tests
    └── load-test.py                      # Load testing script
```

---

## GitHub Workflows Structure

```
.github/
├── workflows/
│   ├── backend-ci.yml                    # Backend CI pipeline
│   ├── frontend-ci.yml                   # Frontend CI pipeline
│   ├── deploy-staging.yml                # Deploy to staging
│   ├── deploy-prod.yml                   # Deploy to production
│   └── security-scan.yml                 # Security scanning
│
├── ISSUE_TEMPLATE/
│   ├── bug_report.md                     # Bug report template
│   └── feature_request.md                # Feature request template
│
└── PULL_REQUEST_TEMPLATE.md              # PR template
```

---

## File Naming Conventions

### Backend (Python)
- **Files**: `snake_case.py` (e.g., `auth_service.py`)
- **Classes**: `PascalCase` (e.g., `UserService`)
- **Functions**: `snake_case` (e.g., `get_user_by_email`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_UPLOAD_SIZE`)

### Frontend (JavaScript/React)
- **Components**: `PascalCase.jsx` (e.g., `IssueCard.jsx`)
- **Utilities**: `camelCase.js` (e.g., `validators.js`)
- **Hooks**: `useCamelCase.js` (e.g., `useAuth.js`)
- **Constants**: `UPPER_SNAKE_CASE` in `constants.js`

---

## Git Branch Strategy

```
main                    # Production-ready code
├── develop            # Integration branch
    ├── feature/module-name
    ├── bugfix/issue-description
    ├── hotfix/critical-fix
    └── release/v1.0.0
```

---

## Key Files Description

| File | Purpose |
|------|---------|
| `readme.md` | Project overview and quick start |
| `DEVELOPMENT_PLAN.md` | Comprehensive development roadmap |
| `ARCHITECTURE.md` | System architecture and design |
| `PROJECT_STRUCTURE.md` | This file - repository organization |
| `CONTRIBUTING.md` | Contribution guidelines for developers |
| `.gitignore` | Files to exclude from version control |
| `requirements.txt` | Python backend dependencies |
| `package.json` | Node.js frontend dependencies |
| `.env.example` | Template for environment variables |

---

## Notes

1. **All `.env` files are gitignored** - Never commit environment files
2. **TODO comments** - Indicate incomplete implementation
3. **Modular structure** - Easy to navigate and scale
4. **Clear separation** - Frontend, backend, docs, scripts separated
5. **Version control** - Follow branch strategy strictly

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-22  
**Maintained By**: Development Team
