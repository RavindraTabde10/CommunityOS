# 🚀 CommunityOS.ai - Quick Start Guide for SaaS Development

**Version:** 2.0.0  
**Last Updated:** 2026-07-24  

---

## 📋 Overview

This guide helps you quickly set up and start developing CommunityOS.ai's SaaS multi-tenancy features.

---

## 🎯 What's Changing?

### Before (Single Society)
- Single database for one society
- All users belong to one organization
- Simple authentication

### After (Multi-Tenant SaaS)
- Multiple societies (organizations) in one database
- Each organization is isolated
- Subscription-based access
- AI-powered features

---

## 🛠️ Setup Instructions

### 1. Update Backend Dependencies

```bash
cd backend

# Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install new dependencies (if any added)
pip install -r requirements.txt
```

### 2. Create Database Migrations

**Step 1: Create Organizations Table**

```bash
# Create migration
alembic revision --autogenerate -m "add organizations and subscription tables"

# Review the generated migration file in backend/alembic/versions/
# Edit if needed

# Apply migration
alembic upgrade head
```

**Step 2: Add organization_id to Existing Tables**

```bash
# Create another migration
alembic revision -m "add organization_id to existing tables"
```

Edit the migration file to add:

```python
def upgrade():
    # Add organization_id to users
    op.add_column('users', sa.Column('organization_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'users', 'organizations', ['organization_id'], ['id'])
    op.create_index('idx_users_organization', 'users', ['organization_id'])
    
    # Add organization_id to issues
    op.add_column('issues', sa.Column('organization_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'issues', 'organizations', ['organization_id'], ['id'])
    op.create_index('idx_issues_organization', 'issues', ['organization_id'])
    
    # Add organization_id to comments
    op.add_column('comments', sa.Column('organization_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'comments', 'organizations', ['organization_id'], ['id'])
    
    # Add organization_id to issue_activities
    op.add_column('issue_activities', sa.Column('organization_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'issue_activities', 'organizations', ['organization_id'], ['id'])

def downgrade():
    # Remove columns in reverse order
    op.drop_column('issue_activities', 'organization_id')
    op.drop_column('comments', 'organization_id')
    op.drop_column('issues', 'organization_id')
    op.drop_column('users', 'organization_id')
```

Apply the migration:

```bash
alembic upgrade head
```

### 3. Create New Models

**Create: `backend/app/models/organization.py`**

```python
"""
Organization Database Model
Multi-tenancy support
"""

from sqlalchemy import Column, String, Integer, Date, Enum, Boolean, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class OrganizationType(str, enum.Enum):
    """Organization type enumeration"""
    APARTMENT_COMPLEX = "apartment_complex"
    HOUSING_SOCIETY = "housing_society"
    GATED_COMMUNITY = "gated_community"
    VILLA_COMMUNITY = "villa_community"


class OrganizationStatus(str, enum.Enum):
    """Organization status enumeration"""
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """Organization model for multi-tenancy"""
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contact Information
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(String)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default='India')
    pincode = Column(String(10))
    
    # Organization Details
    organization_type = Column(Enum(OrganizationType), default=OrganizationType.APARTMENT_COMPLEX)
    total_units = Column(Integer)
    total_towers = Column(Integer)
    possession_date = Column(Date)
    formation_date = Column(Date)
    
    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color
    
    # Status
    status = Column(Enum(OrganizationStatus), default=OrganizationStatus.TRIAL)
    is_active = Column(Boolean, default=True)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.BASIC)
    subscription_start_date = Column(Date)
    subscription_end_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime)  # Soft delete
    
    # Relationships
    users = relationship("User", back_populates="organization")
    issues = relationship("Issue", back_populates="organization")
```

**Create: `backend/app/core/tenant.py`**

```python
"""
Tenant Context Management
Handles organization context for multi-tenancy
"""

from contextvars import ContextVar
from typing import Optional
from fastapi import HTTPException

# Context variable for current tenant
_current_tenant: ContextVar[Optional[str]] = ContextVar("current_tenant", default=None)


def set_current_tenant(organization_id: str):
    """Set current tenant context"""
    if not organization_id:
        raise ValueError("organization_id cannot be None")
    _current_tenant.set(organization_id)


def get_current_tenant() -> Optional[str]:
    """Get current tenant context"""
    return _current_tenant.get()


def clear_current_tenant():
    """Clear current tenant context"""
    _current_tenant.set(None)


def require_tenant() -> str:
    """Get current tenant or raise exception"""
    org_id = get_current_tenant()
    if not org_id:
        raise HTTPException(
            status_code=403, 
            detail="No organization context. User must belong to an organization."
        )
    return org_id


def tenant_filter(query, model):
    """
    Apply tenant filter to SQLAlchemy query
    
    Usage:
        query = db.query(Issue)
        query = tenant_filter(query, Issue)
    """
    org_id = require_tenant()
    return query.filter(model.organization_id == org_id)
```

**Create: `backend/app/middleware/tenant_context.py`**

```python
"""
Tenant Context Middleware
Extracts organization_id from JWT and sets tenant context
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.tenant import set_current_tenant, clear_current_tenant
from app.services.auth_service import AuthService


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set tenant context from JWT token"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and set tenant context"""
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get("authorization")
            
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = AuthService.decode_token(token)
                
                if payload and "organization_id" in payload:
                    set_current_tenant(payload["organization_id"])
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log error but don't block request
            print(f"Tenant context error: {e}")
            response = await call_next(request)
            return response
            
        finally:
            clear_current_tenant()
```

### 4. Update Existing Models

**Update: `backend/app/models/user.py`**

Add to User model:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    # ... existing fields ...
    
    # Multi-tenancy
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    is_organization_admin = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    
    # ... rest of the model ...
```

**Update: `backend/app/models/issue.py`**

Add to Issue model:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Issue(Base):
    __tablename__ = "issues"
    
    # ... existing fields ...
    
    # Multi-tenancy
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="issues")
    
    # ... rest of the model ...
```

### 5. Update Main App Configuration

**Update: `backend/app/main.py`**

```python
from app.middleware.tenant_context import TenantContextMiddleware

# Add middleware
app.add_middleware(TenantContextMiddleware)
```

### 6. Update Services to Use Tenant Context

**Example: Update `backend/app/services/issue_service.py`**

```python
from app.core.tenant import tenant_filter, get_current_tenant

class IssueService:
    
    @staticmethod
    def get_all_issues(db: Session, filters: dict = None):
        """Get all issues for current organization"""
        query = db.query(Issue)
        
        # Apply tenant filter
        query = tenant_filter(query, Issue)
        
        # Apply other filters
        if filters:
            if filters.get("status"):
                query = query.filter(Issue.status == filters["status"])
        
        return query.all()
    
    @staticmethod
    def create_issue(db: Session, issue_data: dict):
        """Create issue with automatic organization_id"""
        org_id = get_current_tenant()
        issue_data["organization_id"] = org_id
        
        issue = Issue(**issue_data)
        db.add(issue)
        db.commit()
        db.refresh(issue)
        return issue
```

### 7. Update JWT Token Generation

**Update: `backend/app/services/auth_service.py`**

```python
@staticmethod
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with organization_id"""
    to_encode = data.copy()
    
    # Ensure organization_id is included
    if "organization_id" not in to_encode:
        raise ValueError("organization_id is required in token data")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

---

## 🧪 Testing Multi-Tenancy

### Create Test Organizations

```python
# backend/test_setup.py

from app.db.session import SessionLocal
from app.models.organization import Organization

def create_test_organizations():
    db = SessionLocal()
    
    # Organization 1
    org1 = Organization(
        name="Riverdale Heights",
        display_name="Riverdale Heights Society",
        slug="riverdale-heights",
        email="admin@riverdaleheights.com",
        total_units=120,
        organization_type="apartment_complex",
        status="active",
        subscription_tier="professional"
    )
    db.add(org1)
    
    # Organization 2
    org2 = Organization(
        name="Green Valley",
        display_name="Green Valley Community",
        slug="green-valley",
        email="admin@greenvalley.com",
        total_units=200,
        organization_type="gated_community",
        status="active",
        subscription_tier="enterprise"
    )
    db.add(org2)
    
    db.commit()
    print("Test organizations created!")

if __name__ == "__main__":
    create_test_organizations()
```

Run it:

```bash
python backend/test_setup.py
```

### Test Tenant Isolation

```python
# backend/tests/test_tenant_isolation.py

import pytest
from app.models.user import User
from app.models.issue import Issue
from app.core.tenant import set_current_tenant, clear_current_tenant

def test_users_isolated_by_organization(db_session):
    """Test that users from different organizations don't see each other"""
    
    # Create users in org1
    set_current_tenant("org1-id")
    user1_org1 = create_user(db_session, email="user1@org1.com")
    
    # Create users in org2
    set_current_tenant("org2-id")
    user1_org2 = create_user(db_session, email="user1@org2.com")
    
    # Query users in org1 context
    set_current_tenant("org1-id")
    org1_users = db_session.query(User).filter(
        User.organization_id == "org1-id"
    ).all()
    
    assert len(org1_users) == 1
    assert org1_users[0].email == "user1@org1.com"
    
    # Query users in org2 context
    set_current_tenant("org2-id")
    org2_users = db_session.query(User).filter(
        User.organization_id == "org2-id"
    ).all()
    
    assert len(org2_users) == 1
    assert org2_users[0].email == "user1@org2.com"
    
    clear_current_tenant()
```

---

## 📊 Migration Strategy for Existing Data

If you have existing data, you need to migrate it:

```python
# backend/migrate_existing_data.py

from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.user import User
from app.models.issue import Issue

def migrate_existing_data():
    db = SessionLocal()
    
    # Create default organization for existing data
    default_org = Organization(
        name="Default Organization",
        display_name="Default Organization",
        slug="default-org",
        status="active",
        subscription_tier="professional"
    )
    db.add(default_org)
    db.commit()
    db.refresh(default_org)
    
    # Update all existing users
    db.query(User).update({"organization_id": default_org.id})
    
    # Update all existing issues
    db.query(Issue).update({"organization_id": default_org.id})
    
    # Update comments
    db.query(Comment).update({"organization_id": default_org.id})
    
    # Update activities
    db.query(IssueActivity).update({"organization_id": default_org.id})
    
    db.commit()
    print(f"Migrated existing data to organization: {default_org.name}")

if __name__ == "__main__":
    migrate_existing_data()
```

---

## 🎯 Development Checklist

### Phase 1: Core Multi-Tenancy
- [ ] Create database migrations
- [ ] Create Organization model
- [ ] Create Subscription models
- [ ] Implement tenant context system
- [ ] Update existing models
- [ ] Add middleware for tenant context
- [ ] Update all services with tenant filtering
- [ ] Write unit tests for tenant isolation
- [ ] Write integration tests
- [ ] Security audit

### Phase 2: API Endpoints
- [ ] Organization CRUD endpoints
- [ ] User invitation system
- [ ] Subscription management endpoints
- [ ] Organization onboarding flow
- [ ] Admin dashboard APIs

### Phase 3: Frontend
- [ ] Update frontend with organization context
- [ ] Organization switcher component
- [ ] Subscription management UI
- [ ] Organization settings page
- [ ] Admin dashboard

---

## 🚨 Important Notes

### Security
1. **Always validate tenant context** - Never trust client-sent organization_id
2. **Test cross-tenant access** - Ensure no data leaks between organizations
3. **Audit logging** - Log all organization-level operations

### Performance
1. **Index organization_id** on all tables
2. **Use connection pooling**
3. **Cache organization data**

### Data Integrity
1. **Foreign key constraints** for organization_id
2. **Cascade deletes** properly configured
3. **Backup before migrations**

---

## 📚 Additional Resources

- [SAAS_MULTI_TENANCY_PLAN.md](./SAAS_MULTI_TENANCY_PLAN.md) - Complete database schema
- [SAAS_IMPLEMENTATION_ROADMAP.md](./SAAS_IMPLEMENTATION_ROADMAP.md) - 12-week timeline
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture

---

## 🆘 Troubleshooting

### Issue: "No organization context" error
**Solution:** Ensure JWT token includes organization_id and middleware is configured

### Issue: Users see data from other organizations
**Solution:** Check tenant_filter is applied to all queries

### Issue: Migration fails
**Solution:** Backup database, check existing data, rollback if needed

---

**Ready to build? Let's create the future of community management! 🚀**
