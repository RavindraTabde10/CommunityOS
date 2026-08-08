# Backend API - Quick Reference Guide

## 🚀 Quick Start

```bash
# Navigate to backend
cd backend

# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Start server
uvicorn app.main:app --reload

# Access API
# - API: http://127.0.0.1:8000
# - Docs: http://127.0.0.1:8000/api/docs
```

---

## 📚 API Endpoints

### Base URL: `http://127.0.0.1:8000/api/v1`

### Authentication

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/auth/register` | POST | Register new user | No |
| `/auth/login` | POST | Login and get token | No |
| `/auth/me` | GET | Get current user | Yes |

### Issues

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/issues/` | POST | Create issue | Yes |
| `/issues/` | GET | List issues | Yes |
| `/issues/{id}` | GET | Get issue | Yes |
| `/issues/{id}` | PUT | Update issue | Yes |
| `/issues/{id}` | DELETE | Delete issue | Yes |

---

## 🔐 Authentication Flow

### 1. Register
```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "resident",
  "password": "password123"
}
```

### 2. Login
```json
POST /api/v1/auth/login
Form Data:
- username: user@example.com
- password: password123

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Use Token
```
Authorization: Bearer eyJ...
```

---

## 📊 Database Commands

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Test connection
python test_local_db.py
```

---

## 🗂️ Database Schema

### Users
- id (String)
- email (String, unique)
- name (String)
- role (resident/contractor/admin/security/facility)
- password_hash (String)
- phone (String, optional)
- unit_number (String, optional)

### Issues
- id (String)
- title (String)
- description (Text)
- category (electrical/plumbing/painting/carpentry/flooring/civil/other)
- priority (low/medium/high/critical)
- status (open/in_progress/resolved/closed)
- reported_by (FK → users.id)
- assigned_to (FK → users.id, optional)

### Issue Photos
- id (String)
- issue_id (FK → issues.id)
- photo_url (String)
- uploaded_at (DateTime)

---

## 🎨 Example Requests

### Create Issue
```json
POST /api/v1/issues/
Authorization: Bearer {token}

{
  "title": "Broken door lock",
  "description": "Main door lock not working",
  "category": "civil",
  "priority": "high",
  "location": "Building A",
  "unit_number": "A-101"
}
```

### List Issues
```
GET /api/v1/issues/?status=open&category=electrical
Authorization: Bearer {token}
```

---

## 🔧 Environment Variables

```env
# Required
DATABASE_URL=sqlite:///./society_app.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173

# Optional
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=your-bucket
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/   # API routes
│   ├── core/               # Config
│   ├── db/                 # Database
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── main.py            # FastAPI app
├── alembic/               # Migrations
├── .env                   # Environment vars
├── requirements.txt       # Dependencies
└── society_app.db        # SQLite DB
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
taskkill /F /IM python.exe  # Windows
# kill -9 $(lsof -t -i:8000)  # Linux/Mac
```

### Migration errors
```bash
# Reset database
rm society_app.db
alembic upgrade head
```

### Import errors
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📞 Quick Commands

```bash
# Start server
uvicorn app.main:app --reload

# Create migration
alembic revision --autogenerate -m "message"

# Apply migrations
alembic upgrade head

# Test DB connection
python test_local_db.py

# Format code
black .

# Run tests
pytest

# Install dependencies
pip install -r requirements.txt
```

---

## 📖 Documentation Links

- **Swagger UI:** http://127.0.0.1:8000/api/docs
- **ReDoc:** http://127.0.0.1:8000/api/redoc
- **Full README:** [API_README.md](API_README.md)
- **Implementation Plan:** [API_IMPLEMENTATION_PLAN.md](API_IMPLEMENTATION_PLAN.md)

---

**Last Updated:** 2026-07-23
