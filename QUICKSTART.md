# CommunityOS.ai - Quick Start Guide

## 🚀 Quick Start

**CommunityOS.ai** is an AI-powered platform for managing residential societies — issue tracking, events, polls, assets, visitors, and more.

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
copy .env.template .env         # then edit .env with your values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend:** http://localhost:5173
- **Backend API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/api/docs
- **ReDoc:** http://127.0.0.1:8000/api/redoc

### Create Admin User

```bash
cd backend
.venv\Scripts\activate
python scripts/create_admin.py
```

## 📚 Documentation

- [readme.md](readme.md) - Project overview & full structure
- [REFERENCE.md](REFERENCE.md) - Complete API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [WORKFLOW.md](WORKFLOW.md) - Development workflow

## 🏗️ Tech Stack

**Frontend:** React 18 + Vite 5, Material-UI, Redux Toolkit, Recharts  
**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic  
**Database:** SQLite (dev) / PostgreSQL via Supabase (prod)  
**Storage:** AWS S3 / Supabase Storage  
**Hosting:** Vercel (frontend) + Railway/AWS (backend)

## 📝 License

Proprietary - All rights reserved
