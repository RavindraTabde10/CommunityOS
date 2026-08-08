"""
PostgreSQL Database Setup Script
This script creates a PostgreSQL database for the Society Management App
"""

import os
import sys
from pathlib import Path
from secrets import token_urlsafe

def generate_password():
    """Generate a secure random password"""
    return token_urlsafe(16)

def create_env_config():
    """Create PostgreSQL configuration for .env file"""
    
    # Database configuration
    db_host = "localhost"
    db_port = "5432"
    db_name = "society_management"
    db_user = "society_admin"
    db_password = generate_password()
    
    # Build connection string
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Generate secret key if needed
    secret_key = token_urlsafe(32)
    
    env_content = f"""# PostgreSQL Database Configuration
DATABASE_URL={database_url}

# Security
SECRET_KEY={secret_key}

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: S3/Supabase (configure if needed)
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_S3_BUCKET_NAME=
# SUPABASE_URL=
# SUPABASE_KEY=
"""
    
    return env_content, db_name, db_user, db_password

def create_postgres_setup_sql(db_name, db_user, db_password):
    """Generate SQL commands to set up PostgreSQL database"""
    
    sql_commands = f"""-- PostgreSQL Setup Commands
-- Run these in psql as the postgres superuser

-- Create database user
CREATE USER {db_user} WITH PASSWORD '{db_password}';

-- Create database
CREATE DATABASE {db_name} OWNER {db_user};

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};

-- Connect to the database and grant schema privileges
\\c {db_name}
GRANT ALL ON SCHEMA public TO {db_user};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_user};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {db_user};

-- Verify setup
\\du {db_user}
\\l {db_name}
"""
    
    return sql_commands

def main():
    print("=" * 70)
    print("POSTGRESQL SETUP FOR SOCIETY MANAGEMENT APP")
    print("=" * 70)
    print()
    
    # Generate configuration
    print("📝 Generating PostgreSQL configuration...")
    env_content, db_name, db_user, db_password = create_env_config()
    
    # Save .env file
    env_file = Path(__file__).parent / ".env"
    backup_file = Path(__file__).parent / ".env.backup"
    
    # Backup existing .env if it exists
    if env_file.exists():
        print(f"📦 Backing up existing .env to .env.backup...")
        env_file.rename(backup_file)
    
    # Write new .env
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file with PostgreSQL configuration")
    print()
    
    # Generate SQL setup file
    sql_content = create_postgres_setup_sql(db_name, db_user, db_password)
    sql_file = Path(__file__).parent / "setup_postgres.sql"
    
    with open(sql_file, 'w') as f:
        f.write(sql_content)
    
    print(f"✅ Created setup_postgres.sql file")
    print()
    
    # Display instructions
    print("=" * 70)
    print("📋 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1️⃣  Set PostgreSQL superuser password (if not already set):")
    print("    Run in terminal: psql -U postgres")
    print("    Then: \\password postgres")
    print()
    print("2️⃣  Create the database and user:")
    print("    Option A - From terminal:")
    print(f"      psql -U postgres -f setup_postgres.sql")
    print()
    print("    Option B - Manual commands:")
    print(f"      psql -U postgres")
    print(f"      CREATE USER {db_user} WITH PASSWORD '{db_password}';")
    print(f"      CREATE DATABASE {db_name} OWNER {db_user};")
    print()
    print("3️⃣  Apply database migrations:")
    print("      alembic upgrade head")
    print()
    print("4️⃣  Start your application:")
    print("      uvicorn app.main:app --reload")
    print()
    print("=" * 70)
    print("DATABASE CREDENTIALS (save these securely):")
    print("=" * 70)
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    print(f"Password: {db_password}")
    print(f"Host: localhost")
    print(f"Port: 5432")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT: The password is also in your .env file")
    print("    Keep your .env file secure and never commit it to git!")
    print()
    print("✅ Setup script complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
