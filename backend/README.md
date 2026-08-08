# Riverdale Connect - Backend

FastAPI backend for Riverdale Connect pre-handover project governance application.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Storage**: AWS S3
- **Email**: Resend

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       └── api.py          # API router aggregation
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── security.py        # Security utilities
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── db/                    # Database configuration
│   └── main.py                # Application entry point
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
└── .env.example              # Environment variables template
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (or Supabase account)
- AWS S3 bucket
- Resend account

### Installation

1. Clone the repository:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

5. Initialize database:
```bash
alembic upgrade head
```

### Running the Application

**Development mode:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Database Migrations

**Create new migration:**
```bash
alembic revision --autogenerate -m "description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

## Testing

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=app tests/
```

## API Endpoints

### Version 1 Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

#### Issues
- `POST /api/v1/issues` - Create issue
- `GET /api/v1/issues` - List issues
- `GET /api/v1/issues/{id}` - Get issue
- `PUT /api/v1/issues/{id}` - Update issue
- `DELETE /api/v1/issues/{id}` - Delete issue
- `POST /api/v1/issues/{id}/photos` - Upload photos

#### Reports
- `GET /api/v1/reports/weekly` - Generate weekly report
- `GET /api/v1/reports/download/{id}` - Download report

#### QR Codes
- `POST /api/v1/qrcodes` - Generate QR code
- `GET /api/v1/qrcodes/{code}` - Get QR details

## Environment Variables

See `.env.example` for all required environment variables.

## Development Guidelines

1. **Code Style**: Follow PEP 8, use Black for formatting
2. **Type Hints**: Use type hints for all functions
3. **Docstrings**: Document all classes and functions
4. **Testing**: Write tests for all new features
5. **Commits**: Use conventional commit messages

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel --prod
```

### Docker Deployment

```bash
docker build -t riverdale-connect-backend .
docker run -p 8000:8000 riverdale-connect-backend
```

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact the development team.
