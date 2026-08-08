# 🚀 PostgreSQL Setup Guide - Society Management App

**Date:** 2026-07-25  
**Purpose:** Complete Day 1 by switching to PostgreSQL

---

## 📋 What We're Doing

We're switching from SQLite to PostgreSQL to:
- ✅ Avoid SQLite batch mode limitations
- ✅ Match production environment
- ✅ Complete Day 1 migrations successfully
- ✅ Continue with Day 2+ without blockers

---

## 📦 Step 1: Installation (In Progress)

PostgreSQL 16 is currently installing via winget...

**Status:** Downloading (~348 MB)

Once installation completes, PostgreSQL will be available at:
- **Installation Path:** `C:\Program Files\PostgreSQL\16\`
- **Binary Path:** `C:\Program Files\PostgreSQL\16\bin\`
- **Data Path:** `C:\Program Files\PostgreSQL\16\data\`

---

## 🔧 Step 2: Initial Configuration (After Install)

### Set PostgreSQL Password

The installer will prompt for a password during installation. If not:

```powershell
# Connect as postgres superuser
psql -U postgres

# Set password
\password postgres
# Enter your chosen password (e.g., "postgres123" for development)
```

**Save your password!** You'll need it for the next steps.

---

## 🗄️ Step 3: Create Database and User

We'll create:
- **Database:** `society_management`
- **User:** `society_admin`
- **Password:** Auto-generated secure password

### Option A: Automated Setup (Recommended)

```powershell
# Run the setup script
python setup_postgres.py
```

This will:
1. Generate secure credentials
2. Create `.env` file with PostgreSQL configuration
3. Create `setup_postgres.sql` with database setup commands
4. Display instructions for database creation

### Option B: Manual Setup

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database user
CREATE USER society_admin WITH PASSWORD 'your_secure_password_here';

# Create database
CREATE DATABASE society_management OWNER society_admin;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE society_management TO society_admin;

# Connect to the database
\c society_management

# Grant schema privileges
GRANT ALL ON SCHEMA public TO society_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO society_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO society_admin;

# Exit
\q
```

---

## 📝 Step 4: Update .env Configuration

Your `.env` file should look like this:

```env
# PostgreSQL Database Configuration
DATABASE_URL=postgresql://society_admin:YOUR_PASSWORD@localhost:5432/society_management

# Security
SECRET_KEY=your_secret_key_here

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Important:** Replace `YOUR_PASSWORD` with the actual password.

---

## 🔄 Step 5: Apply Database Migrations

Once the database is created and `.env` is configured:

```powershell
# Activate virtual environment
cd backend
.venv\Scripts\activate

# Apply all migrations
python -m alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 17c93b07c633, Initial migration
INFO  [alembic.runtime.migration] Running upgrade 17c93b07c633 -> 3f2d80960de8, Create users and issues tables
INFO  [alembic.runtime.migration] Running upgrade ... -> 8bd0c75a08a3, add_multi_tenancy_tables_and_organization_id
```

---

## ✅ Step 6: Verify Setup

### Check Database Tables

```powershell
psql -U society_admin -d society_management
```

```sql
-- List all tables
\dt

-- Should see:
-- organizations
-- subscription_plans
-- subscriptions
-- billing_invoices
-- usage_metrics
-- organization_settings
-- audit_logs
-- users
-- issues
-- comments
-- issue_activities
-- issue_photos
-- alembic_version

-- Check organization table structure
\d organizations

-- Exit
\q
```

### Test Database Connection

```powershell
python test_db_connection.py
```

Expected output: `✅ Database connection successful!`

---

## 🚀 Step 7: Start Application

```powershell
# Start the backend
uvicorn app.main:app --reload
```

Visit: http://127.0.0.1:8000/api/docs

You should see all your API endpoints including the new multi-tenancy ones!

---

## 🎯 Day 1 Completion Checklist

Once you complete the above steps:

- [x] PostgreSQL installed
- [x] Database created
- [x] User created with proper permissions
- [x] .env configured with PostgreSQL connection
- [x] All migrations applied successfully
- [x] Database tables verified
- [x] Application starts without errors
- [x] API documentation accessible

**When all checked:** Day 1 is 100% complete! 🎉

---

## 🔍 Troubleshooting

### Issue: "psql: command not found"

**Solution:** Add PostgreSQL to PATH

```powershell
# Add to current session
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"

# Or restart your terminal
```

### Issue: "password authentication failed"

**Solution:** 
1. Check your password in `.env` matches what you set
2. Try resetting the password:
   ```powershell
   psql -U postgres
   \password society_admin
   ```

### Issue: "database does not exist"

**Solution:** Create it manually:
```powershell
psql -U postgres
CREATE DATABASE society_management;
\q
```

### Issue: Migration fails with "permission denied"

**Solution:** Grant proper privileges:
```powershell
psql -U postgres -d society_management
GRANT ALL ON SCHEMA public TO society_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO society_admin;
\q
```

---

## 📊 What This Accomplishes

After completing this setup:

✅ **All 11 new database models** will be created
✅ **All existing tables** updated with `organization_id`
✅ **No SQLite limitations** - all migrations work perfectly
✅ **Production parity** - same database as production
✅ **Day 1 complete** - ready to start Day 2

---

## 🎯 Next Steps (Day 2)

With PostgreSQL set up, tomorrow we'll:

1. Create Pydantic schemas for all new models
2. Create billing & usage tracking tables (already in migration!)
3. Test all database relationships
4. Begin tenant context system

**Estimated Day 2 Duration:** 5-6 hours

---

## 🆘 Need Help?

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify PostgreSQL service is running:
   ```powershell
   Get-Service postgresql*
   ```
3. Check PostgreSQL logs:
   ```
   C:\Program Files\PostgreSQL\16\data\log\
   ```

---

**Ready to continue once PostgreSQL installation completes!** ⏳
