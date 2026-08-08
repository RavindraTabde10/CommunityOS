# Society Management App - Backend API

## 🚀 Overview

FastAPI-based REST API for managing society operations including user management, issue tracking, and facility management. Built with SQLAlchemy ORM, JWT authentication, and SQLite database.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Database](#database)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Development](#development)

---

## ✨ Features

### Implemented ✅

- **User Management**
  - User registration with role-based access
  - JWT authentication (login/logout)
  - Password hashing with bcrypt
  - User profile retrieval
  - Role-based access control (resident, contractor, admin, facility, security)

- **Issue Tracking**
  - Create, read, update, delete issues
  - Issue categorization (electrical, plumbing, painting, carpentry, etc.)
  - Priority levels (low, medium, high, critical)
  - Status tracking (open, in_progress, resolved, closed)
  - Role-based visibility (users see only their issues, admins see all)
  - Issue assignment to contractors
  - Work completion tracking
  - Photo upload support

- **Contractor Management** ✅ *NEW*
  - Contractor profile creation and management
  - Specialization-based filtering
  - Contractor verification by admins
  - Issue assignment workflow
  - Work completion tracking
  - Contractor rating system (1-5 stars)
  - Performance metrics (completion rate, average rating)
  - Work verification by admins
  - Availability status tracking

- **Security**
  - JWT token-based authentication
  - Password encryption with bcrypt
  - Protected endpoints with Bearer token
  - Role-based authorization

- **Database**
  - SQLite database for development
  - SQLAlchemy ORM
  - Alembic migrations
  - Automatic schema management

---

## 🛠 Tech Stack

- **Framework:** FastAPI 0.109.0
- **Database:** SQLite (dev) / PostgreSQL (production ready)
- **ORM:** SQLAlchemy 2.0.25
- **Migrations:** Alembic 1.13.1
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Server:** Uvicorn
- **API Documentation:** Swagger UI / ReDoc

---

## 🚦 Getting Started

### Prerequisites

- Python 3.12+
- pip or poetry

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env with your configuration
   # Minimal required:
   DATABASE_URL=sqlite:///./society_app.db
   SECRET_KEY=your-secret-key-here
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the API**
   - API: http://127.0.0.1:8000
   - Swagger Docs: http://127.0.0.1:8000/api/docs
   - ReDoc: http://127.0.0.1:8000/api/redoc

---

## 📚 API Documentation

### Interactive Documentation

Visit http://127.0.0.1:8000/api/docs for interactive Swagger UI documentation.

### Quick Reference

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login and get JWT token | No |
| GET | `/api/v1/auth/me` | Get current user profile | Yes |

#### Issues Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/issues/` | Create new issue | Yes |
| GET | `/api/v1/issues/` | List issues (filtered) | Yes |
| GET | `/api/v1/issues/{id}` | Get issue details | Yes |
| PUT | `/api/v1/issues/{id}` | Update issue | Yes |
| DELETE | `/api/v1/issues/{id}` | Delete issue | Yes |
| POST | `/api/v1/issues/{id}/assign` | Assign contractor to issue | Yes (Admin/Facility) |
| DELETE | `/api/v1/issues/{id}/assign` | Unassign contractor from issue | Yes (Admin/Facility) |
| POST | `/api/v1/issues/{id}/complete` | Mark work complete | Yes (Contractor) |

#### Contractor Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/contractors/` | Create contractor profile | Yes (Contractor) |
| GET | `/api/v1/contractors/` | List contractors (with filters) | Yes |
| GET | `/api/v1/contractors/{id}` | Get contractor details | Yes |
| PUT | `/api/v1/contractors/{id}` | Update contractor profile | Yes (Owner/Admin) |
| GET | `/api/v1/contractors/{id}/stats` | Get contractor statistics | Yes |
| POST | `/api/v1/contractors/{id}/verify` | Verify contractor | Yes (Admin) |
| POST | `/api/v1/contractors/{id}/rate` | Rate contractor | Yes (Issue Reporter) |
| GET | `/api/v1/contractors/{id}/ratings` | List contractor ratings | Yes |
| POST | `/api/v1/work-completions/{id}/verify` | Verify completed work | Yes (Admin/Facility) |

---

## 🔐 Authentication

### User Registration

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "1234567890",
  "role": "resident",
  "unit_number": "A-101",
  "password": "securepassword123"
}
```

### Login

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🗄️ Database

### Schema

**Users Table:**
- id (String, Primary Key)
- email (String, Unique)
- password_hash (String)
- name (String)
- phone (String, Optional)
- role (Enum: resident, contractor, builder, admin, security, facility)
- unit_number (String, Optional)
- created_at (DateTime)
- updated_at (DateTime)

**Issues Table:**
- id (String, Primary Key)
- title (String)
- description (Text)
- category (Enum: electrical, plumbing, painting, carpentry, flooring, civil, other)
- priority (Enum: low, medium, high, critical)
- status (Enum: open, in_progress, resolved, closed)
- location (String)
- unit_number (String)
- reported_by (Foreign Key -> users.id)
- assigned_to (Foreign Key -> users.id)
- created_at (DateTime)
- updated_at (DateTime)
- resolved_at (DateTime)

**Issue Photos Table:**
- id (String, Primary Key)
- issue_id (Foreign Key -> issues.id)
- photo_url (String)
- uploaded_at (DateTime)

**Contractor Profiles Table:**
- id (String, Primary Key)
- user_id (Foreign Key -> users.id, Unique)
- company_name (String, Optional)
- gst_number (String, Unique, Optional)
- license_number (String, Optional)
- specializations (JSON Array: electrical, plumbing, painting, carpentry, etc.)
- years_of_experience (Integer, Optional)
- is_available (Boolean, Default: True)
- availability_status (Enum: available, busy, on_leave, inactive)
- total_jobs_completed (Integer, Default: 0)
- average_rating (Numeric(3,2), Default: 0.00)
- total_ratings (Integer, Default: 0)
- completion_rate (Numeric(5,2), Default: 0.00)
- is_verified (Boolean, Default: False)
- verified_by (Foreign Key -> users.id, Optional)
- verified_at (DateTime, Optional)
- is_active (Boolean, Default: True)
- created_at (DateTime)
- updated_at (DateTime)

**Contractor Ratings Table:**
- id (String, Primary Key)
- contractor_id (Foreign Key -> contractor_profiles.id)
- issue_id (Foreign Key -> issues.id, Optional)
- rated_by (Foreign Key -> users.id)
- rating (Integer, 1-5)
- quality_rating (Integer, 1-5, Optional)
- punctuality_rating (Integer, 1-5, Optional)
- professionalism_rating (Integer, 1-5, Optional)
- review_text (Text, Optional)
- work_photos (JSON Array, Optional)
- created_at (DateTime)

**Work Completions Table:**
- id (String, Primary Key)
- issue_id (Foreign Key -> issues.id, Unique)
- contractor_id (Foreign Key -> contractor_profiles.id)
- completed_at (DateTime)
- work_description (Text, Optional)
- materials_used (JSON Array, Optional)
- labor_cost (Numeric, Optional)
- total_cost (Numeric, Optional)
- before_photos (JSON Array, Optional)
- after_photos (JSON Array, Optional)
- is_verified (Boolean, Default: False)
- verified_by (Foreign Key -> users.id, Optional)
- verified_at (DateTime, Optional)
- verification_notes (Text, Optional)

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 📁 Project Structure

```
backend/
├── alembic/                # Database migrations
│   ├── versions/           # Migration files
│   └── env.py             # Alembic configuration
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/  # API endpoints
│   │       │   ├── auth.py
│   │       │   └── issues.py
│   │       └── api.py      # Router aggregation
│   ├── core/
│   │   └── config.py       # App configuration
│   ├── db/
│   │   ├── base.py         # SQLAlchemy base
│   │   └── session.py      # Database session
│   ├── models/             # SQLAlchemy models
│   │   ├── user.py
│   │   └── issue.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── user.py
│   │   └── issue.py
│   ├── services/           # Business logic
│   │   ├── auth_service.py
│   │   └── s3_service.py
│   └── main.py             # FastAPI app entry
├── .env                    # Environment variables
├── .env.template           # Environment template
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
├── society_app.db         # SQLite database
└── README.md              # This file
```

---

## 🔧 Environment Variables

### Required

```env
DATABASE_URL=sqlite:///./society_app.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Optional

```env
# AWS S3 (for file uploads)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=society-app-uploads

# Email (Resend)
RESEND_API_KEY=your-api-key
FROM_EMAIL=noreply@yourdomain.com

# Supabase (alternative to local DB)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-key
SUPABASE_SECRET_KEY=your-secret-key
```

---

## 👨‍💻 Development

### Testing Locally

1. **Test database connection**
   ```bash
   python test_local_db.py
   ```

2. **Test Supabase API (if using)**
   ```bash
   python test_supabase_api.py
   ```

3. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Creating New Endpoints

1. Create endpoint in `app/api/v1/endpoints/`
2. Add router to `app/api/v1/api.py`
3. Create Pydantic schemas in `app/schemas/`
4. Create SQLAlchemy model in `app/models/`
5. Generate migration: `alembic revision --autogenerate -m "description"`
6. Apply migration: `alembic upgrade head`

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Circular import errors**
   - Don't import models in `app/db/base.py`
   - Import models only in `alembic/env.py`

2. **Authentication errors**
   - Ensure JWT token is included in Authorization header
   - Token format: `Bearer <token>`

3. **Database locked**
   - SQLite doesn't support high concurrency
   - Consider PostgreSQL for production

4. **Migration errors**
   - Check if models are properly imported in `alembic/env.py`
   - Verify database connection string

---

## 📝 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📧 Contact

For questions or support, please contact the development team.
