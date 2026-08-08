# Dashboard Redesign Plan - Society Management Focus

## Overview
Transform the current issue-tracker-focused dashboard into a comprehensive **Society Management Dashboard** that emphasizes community information, committee members, announcements, and resident services.

---

## Current State Analysis

### Existing Dashboard Components
1. ✅ User welcome header with role badge
2. ✅ Announcement marquee (recently implemented - looks great!)
3. ❌ **Issue-focused statistics** (Total, Open, In Progress, Resolved)
4. ❌ **Issue-only Quick Actions** (Create Issue, View All Issues)
5. ❌ **Recent Issues section** (dominates the page)
6. 🚧 Under construction notice

### Problems with Current Design
- **Too issue-centric**: Feels like a bug tracker, not a society platform
- **Missing community context**: No committee info, society details, or member information
- **No community engagement**: No upcoming events, meetings, or community activities
- **Limited resident value**: Dashboard doesn't help residents connect with their community

---

## Proposed New Dashboard Layout

### 1. **Hero Section** (Top)
```
┌─────────────────────────────────────────────────────────┐
│  Welcome to [Society Name]!                             │
│  Hello, [User Name] ([Role])                            │
│  [Unit Number] • [Building/Wing]                        │
└─────────────────────────────────────────────────────────┘
```

### 2. **Announcement Marquee** (Already Implemented ✅)
```
┌─────────────────────────────────────────────────────────┐
│  🔊 [Scrolling Announcements]                           │
└─────────────────────────────────────────────────────────┘
```

### 3. **Committee Members Section** (NEW 🆕)
```
┌─────────────────────────────────────────────────────────┐
│  🏛️ Committee Members                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Avatar  │  │ Avatar  │  │ Avatar  │  │ Avatar  │   │
│  │ Name    │  │ Name    │  │ Name    │  │ Name    │   │
│  │ Role    │  │ Role    │  │ Role    │  │ Role    │   │
│  │ Contact │  │ Contact │  │ Contact │  │ Contact │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 4. **Community Quick Stats** (REDESIGNED 📊)
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 👥 Total     │ 🏠 Total     │ 📝 Active    │ ✅ Resolved  │
│ Residents    │ Units        │ Issues       │ This Month   │
│    125       │     100      │      3       │      8       │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### 5. **Quick Actions** (ENHANCED 🔗)
```
┌─────────────────────────────────────────────────────────┐
│  🐛 Report Issue    📅 View Events    📋 Notice Board   │
│  💰 Pay Bills       📞 Contact Committee  🏊 Book Facility│
└─────────────────────────────────────────────────────────┘
```

### 6. **Upcoming Events & Meetings** (NEW 📅)
```
┌─────────────────────────────────────────────────────────┐
│  📅 Upcoming Events                                     │
│  • Committee Meeting - Aug 5, 2026 at 6:00 PM          │
│  • Festival Celebration - Aug 15, 2026                  │
│  • Maintenance Work - Aug 20-22, 2026                   │
└─────────────────────────────────────────────────────────┘
```

### 7. **Recent Activity** (REDESIGNED 🔄)
```
┌─────────────────────────────────────────────────────────┐
│  🔔 Recent Community Activity                           │
│  • New announcement posted                              │
│  • Issue RGTS-00001 resolved                            │
│  • Facility booking confirmed                           │
│  • New resident joined                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Phase 1: Backend - Committee Members Feature

#### Step 1.1: Create Committee Member Model
**File**: `backend/app/models/committee_member.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base_class import Base

class CommitteeRole(str, enum.Enum):
    """Committee member roles"""
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    MEMBER = "member"

class CommitteeMember(Base):
    """Committee member model"""
    __tablename__ = "committee_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(CommitteeRole), nullable=False)
    position_name = Column(String(100))  # Custom position title
    responsibilities = Column(String(500))  # Brief description
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    term_start_date = Column(DateTime, nullable=True)
    term_end_date = Column(DateTime, nullable=True)
    display_order = Column(Integer, default=0)  # For ordering on dashboard
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="committee_membership")
```

#### Step 1.2: Create Schemas
**File**: `backend/app/schemas/committee_member.py`

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from app.models.committee_member import CommitteeRole

class CommitteeMemberBase(BaseModel):
    role: CommitteeRole
    position_name: Optional[str] = None
    responsibilities: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    display_order: int = 0

class CommitteeMemberCreate(CommitteeMemberBase):
    user_id: int
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None

class CommitteeMemberUpdate(BaseModel):
    role: Optional[CommitteeRole] = None
    position_name: Optional[str] = None
    responsibilities: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None
    display_order: Optional[int] = None

class CommitteeMemberResponse(CommitteeMemberBase):
    id: int
    user_id: int
    user_name: str  # From joined user
    user_email: str  # From joined user
    is_active: bool
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

#### Step 1.3: Create Service Layer
**File**: `backend/app/services/committee_service.py`

```python
from sqlalchemy.orm import Session, joinedload
from app.models.committee_member import CommitteeMember
from app.models.user import User
from app.schemas.committee_member import CommitteeMemberCreate, CommitteeMemberUpdate
from typing import List, Optional

def create_committee_member(db: Session, data: CommitteeMemberCreate) -> CommitteeMember:
    """Create a new committee member"""
    member = CommitteeMember(**data.dict())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def get_active_committee_members(db: Session) -> List[dict]:
    """Get all active committee members ordered by display_order"""
    members = db.query(CommitteeMember).filter(
        CommitteeMember.is_active == True
    ).options(
        joinedload(CommitteeMember.user)
    ).order_by(
        CommitteeMember.display_order
    ).all()
    
    # Format response with user data
    result = []
    for member in members:
        result.append({
            "id": member.id,
            "role": member.role,
            "position_name": member.position_name,
            "responsibilities": member.responsibilities,
            "contact_email": member.contact_email or member.user.email,
            "contact_phone": member.contact_phone,
            "user_name": member.user.name,
            "user_email": member.user.email,
            "display_order": member.display_order,
            "term_start_date": member.term_start_date,
            "term_end_date": member.term_end_date,
        })
    return result

def get_all_committee_members(db: Session) -> List[CommitteeMember]:
    """Get all committee members (for admin)"""
    return db.query(CommitteeMember).options(
        joinedload(CommitteeMember.user)
    ).order_by(CommitteeMember.display_order).all()

def get_committee_member_by_id(db: Session, member_id: int) -> Optional[CommitteeMember]:
    """Get committee member by ID"""
    return db.query(CommitteeMember).options(
        joinedload(CommitteeMember.user)
    ).filter(CommitteeMember.id == member_id).first()

def update_committee_member(
    db: Session, 
    member_id: int, 
    data: CommitteeMemberUpdate
) -> Optional[CommitteeMember]:
    """Update committee member"""
    member = get_committee_member_by_id(db, member_id)
    if not member:
        return None
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(member, key, value)
    
    db.commit()
    db.refresh(member)
    return member

def delete_committee_member(db: Session, member_id: int) -> bool:
    """Delete committee member"""
    member = get_committee_member_by_id(db, member_id)
    if not member:
        return False
    
    db.delete(member)
    db.commit()
    return True
```

#### Step 1.4: Create API Endpoints
**File**: `backend/app/api/v1/endpoints/committee.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.committee_member import (
    CommitteeMemberCreate,
    CommitteeMemberUpdate,
    CommitteeMemberResponse
)
from app.services import committee_service

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.post("/", response_model=CommitteeMemberResponse, status_code=status.HTTP_201_CREATED)
def create_committee_member(
    data: CommitteeMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new committee member (Admin only)"""
    return committee_service.create_committee_member(db, data)

@router.get("/active", response_model=List[dict])
def get_active_committee_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active committee members (Public - all authenticated users)"""
    return committee_service.get_active_committee_members(db)

@router.get("/", response_model=List[CommitteeMemberResponse])
def get_all_committee_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all committee members including inactive (Admin only)"""
    members = committee_service.get_all_committee_members(db)
    # Format with user data
    result = []
    for member in members:
        result.append({
            **CommitteeMemberResponse.from_orm(member).dict(),
            "user_name": member.user.name,
            "user_email": member.user.email
        })
    return result

@router.get("/{member_id}", response_model=CommitteeMemberResponse)
def get_committee_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get committee member by ID"""
    member = committee_service.get_committee_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Committee member not found"
        )
    return {
        **CommitteeMemberResponse.from_orm(member).dict(),
        "user_name": member.user.name,
        "user_email": member.user.email
    }

@router.put("/{member_id}", response_model=CommitteeMemberResponse)
def update_committee_member(
    member_id: int,
    data: CommitteeMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update committee member (Admin only)"""
    member = committee_service.update_committee_member(db, member_id, data)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Committee member not found"
        )
    return {
        **CommitteeMemberResponse.from_orm(member).dict(),
        "user_name": member.user.name,
        "user_email": member.user.email
    }

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_committee_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete committee member (Admin only)"""
    success = committee_service.delete_committee_member(db, member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Committee member not found"
        )
```

#### Step 1.5: Register Router
**File**: `backend/app/api/v1/api.py`

Add to imports and router includes:
```python
from app.api.v1.endpoints import committee

api_router.include_router(
    committee.router,
    prefix="/committee",
    tags=["committee"]
)
```

#### Step 1.6: Create Migration
```bash
cd backend
alembic revision --autogenerate -m "add_committee_members_table"
alembic upgrade head
```

#### Step 1.7: Export Models
**File**: `backend/app/models/__init__.py`

Add:
```python
from app.models.committee_member import CommitteeMember, CommitteeRole
```

---

### Phase 2: Frontend - Dashboard Redesign

#### Step 2.1: Create Committee Service
**File**: `frontend/src/api/committeeService.js`

```javascript
import apiClient from './client'

const committeeService = {
  // Get active committee members (public)
  getActiveMembers: async () => {
    const response = await apiClient.get('/committee/active')
    return response.data
  },

  // Get all committee members (admin only)
  getAllMembers: async () => {
    const response = await apiClient.get('/committee')
    return response.data
  },

  // Get committee member by ID
  getMember: async (id) => {
    const response = await apiClient.get(`/committee/${id}`)
    return response.data
  },

  // Create committee member (admin only)
  createMember: async (data) => {
    const response = await apiClient.post('/committee', data)
    return response.data
  },

  // Update committee member (admin only)
  updateMember: async (id, data) => {
    const response = await apiClient.put(`/committee/${id}`, data)
    return response.data
  },

  // Delete committee member (admin only)
  deleteMember: async (id) => {
    await apiClient.delete(`/committee/${id}`)
  }
}

export default committeeService
```

#### Step 2.2: Create Committee Constants
**File**: `frontend/src/constants/committee.js`

```javascript
export const COMMITTEE_ROLES = {
  PRESIDENT: 'president',
  VICE_PRESIDENT: 'vice_president',
  SECRETARY: 'secretary',
  TREASURER: 'treasurer',
  MEMBER: 'member'
}

export const ROLE_LABELS = {
  president: 'President',
  vice_president: 'Vice President',
  secretary: 'Secretary',
  treasurer: 'Treasurer',
  member: 'Committee Member'
}

export const ROLE_ICONS = {
  president: '👑',
  vice_president: '🥈',
  secretary: '📝',
  treasurer: '💰',
  member: '👤'
}

export const getRoleLabel = (role) => ROLE_LABELS[role] || role
export const getRoleIcon = (role) => ROLE_ICONS[role] || '👤'
```

#### Step 2.3: Create Committee Member Card Component
**File**: `frontend/src/components/dashboard/CommitteeMemberCard.jsx`

```jsx
import { Card, CardContent, Typography, Box, Avatar, Chip, IconButton, Tooltip } from '@mui/material'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'
import { getRoleLabel, getRoleIcon } from '../../constants/committee'

const CommitteeMemberCard = ({ member }) => {
  const roleIcon = getRoleIcon(member.role)
  const roleLabel = getRoleLabel(member.role)

  return (
    <Card 
      elevation={2}
      sx={{ 
        height: '100%',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6
        }
      }}
    >
      <CardContent sx={{ textAlign: 'center', p: 3 }}>
        {/* Avatar */}
        <Box sx={{ mb: 2 }}>
          <Avatar 
            sx={{ 
              width: 80, 
              height: 80, 
              margin: '0 auto',
              bgcolor: 'primary.main',
              fontSize: '2rem',
              fontWeight: 'bold'
            }}
          >
            {member.user_name?.charAt(0).toUpperCase() || '?'}
          </Avatar>
        </Box>

        {/* Name */}
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          {member.user_name}
        </Typography>

        {/* Role with Icon */}
        <Chip 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span>{roleIcon}</span>
              <span>{roleLabel}</span>
            </Box>
          }
          color="primary"
          variant="outlined"
          sx={{ mb: 2, fontWeight: 600 }}
        />

        {/* Position Name (if different from role) */}
        {member.position_name && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontStyle: 'italic' }}>
            {member.position_name}
          </Typography>
        )}

        {/* Responsibilities */}
        {member.responsibilities && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontSize: '0.85rem' }}>
            {member.responsibilities}
          </Typography>
        )}

        {/* Contact Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
          {member.contact_email && (
            <Tooltip title={member.contact_email}>
              <IconButton 
                size="small" 
                color="primary"
                onClick={() => window.location.href = `mailto:${member.contact_email}`}
              >
                <EmailIcon />
              </IconButton>
            </Tooltip>
          )}
          {member.contact_phone && (
            <Tooltip title={member.contact_phone}>
              <IconButton 
                size="small" 
                color="primary"
                onClick={() => window.location.href = `tel:${member.contact_phone}`}
              >
                <PhoneIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </CardContent>
    </Card>
  )
}

export default CommitteeMemberCard
```

#### Step 2.4: Create Community Stats Component
**File**: `frontend/src/components/dashboard/CommunityStats.jsx`

```jsx
import { Grid } from '@mui/material'
import { StatCard } from '.'
import PeopleIcon from '@mui/icons-material/People'
import HomeIcon from '@mui/icons-material/Home'
import BugReportIcon from '@mui/icons-material/BugReport'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

const CommunityStats = ({ stats, loading }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={PeopleIcon}
          label="Total Residents"
          value={stats?.total_residents || 0}
          color="info"
          isLoading={loading}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={HomeIcon}
          label="Total Units"
          value={stats?.total_units || 0}
          color="success"
          isLoading={loading}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={BugReportIcon}
          label="Active Issues"
          value={stats?.open_issues || 0}
          color="warning"
          isLoading={loading}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={CheckCircleIcon}
          label="Resolved This Month"
          value={stats?.resolved_this_month || 0}
          color="success"
          isLoading={loading}
        />
      </Grid>
    </Grid>
  )
}

export default CommunityStats
```

#### Step 2.5: Update Dashboard Index Exports
**File**: `frontend/src/components/dashboard/index.js`

```javascript
export { default as StatCard } from './StatCard'
export { default as IssuePreviewCard } from './IssuePreviewCard'
export { default as QuickActions } from './QuickActions'
export { default as AnnouncementMarquee } from './AnnouncementMarquee'
export { default as CommitteeMemberCard } from './CommitteeMemberCard'
export { default as CommunityStats } from './CommunityStats'
```

#### Step 2.6: Redesign Dashboard.jsx
**File**: `frontend/src/pages/Dashboard.jsx`

Major changes:
1. Remove issue-only statistics
2. Add committee members section
3. Add community stats
4. Enhance quick actions
5. Make recent issues less prominent
6. Add society name/info

(Implementation provided in next section)

---

### Phase 3: Dashboard Backend Enhancements

#### Step 3.1: Enhance Statistics Endpoint
**File**: `backend/app/api/v1/endpoints/issues.py`

Add new endpoint for community stats:
```python
@router.get("/community-stats")
def get_community_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get community-wide statistics"""
    from datetime import datetime, timedelta
    
    # Total users (residents)
    total_residents = db.query(User).filter(User.role == UserRole.RESIDENT).count()
    
    # Total issues by status
    open_issues = db.query(Issue).filter(Issue.status.in_(['open', 'in_progress'])).count()
    
    # Resolved this month
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    resolved_this_month = db.query(Issue).filter(
        Issue.status == IssueStatus.RESOLVED,
        Issue.updated_at >= start_of_month
    ).count()
    
    return {
        "total_residents": total_residents,
        "total_units": 100,  # Hard-coded for now, can be from settings
        "open_issues": open_issues,
        "resolved_this_month": resolved_this_month
    }
```

---

## Implementation Timeline

### Priority 1: Backend Foundation (Est. 1-2 hours)
- ✅ Create Committee Member model
- ✅ Create schemas
- ✅ Create service layer
- ✅ Create API endpoints
- ✅ Run migration
- ✅ Test endpoints in Swagger

### Priority 2: Frontend Components (Est. 1-2 hours)
- ✅ Create committee service
- ✅ Create constants
- ✅ Create CommitteeMemberCard component
- ✅ Create CommunityStats component
- ✅ Export components

### Priority 3: Dashboard Redesign (Est. 1 hour)
- ✅ Update Dashboard.jsx with new layout
- ✅ Add committee members section
- ✅ Add community stats
- ✅ Reduce issue prominence
- ✅ Test and refine UI

### Priority 4: Admin Management Page (Est. 1 hour - Optional)
- Create CommitteeManagement.jsx page
- Add route and navigation
- CRUD operations for committee members

---

## Testing Checklist

### Backend Testing
- [ ] Create committee member via API
- [ ] Get active committee members
- [ ] Get all committee members (admin)
- [ ] Update committee member
- [ ] Delete committee member
- [ ] Verify role-based access (admin only for modifications)

### Frontend Testing
- [ ] Committee members display on dashboard
- [ ] Contact buttons work (email/phone)
- [ ] Community stats display correctly
- [ ] Announcements still working
- [ ] Quick actions functional
- [ ] Responsive design on mobile

---

## Success Criteria

### Dashboard should:
✅ **Feel like a community hub**, not just an issue tracker
✅ **Prominently display committee members** with contact info
✅ **Show community statistics** that matter to residents
✅ **Keep announcements visible** (already done!)
✅ **Provide quick access** to common actions
✅ **Be visually balanced** between information and actions
✅ **Work on all screen sizes** (mobile, tablet, desktop)

---

## Future Enhancements (Post-Implementation)

1. **Upcoming Events Calendar** - Show community events/meetings
2. **Society Information Card** - Name, address, established date
3. **Recent Activity Feed** - Mix of issues, announcements, events
4. **Notice Board** - Important documents and notices
5. **Quick Polls/Surveys** - Community engagement
6. **Weather Widget** - Local weather for the society
7. **Facility Booking Status** - Available/booked facilities

---

## Notes

- **Single-tenant architecture**: No organization_id filtering needed
- **Role-based access**: Committee management is admin-only, viewing is public
- **User integration**: Committee members are linked to User records
- **Flexible positions**: Support custom position names beyond standard roles
- **Display ordering**: Configurable order for dashboard display

---

## Files to Create/Modify

### Backend Files
- 🆕 `backend/app/models/committee_member.py`
- 🆕 `backend/app/schemas/committee_member.py`
- 🆕 `backend/app/services/committee_service.py`
- 🆕 `backend/app/api/v1/endpoints/committee.py`
- 📝 `backend/app/api/v1/api.py` (register router)
- 📝 `backend/app/models/__init__.py` (export model)
- 🆕 `backend/alembic/versions/[hash]_add_committee_members_table.py`
- 📝 `backend/app/api/v1/endpoints/issues.py` (add community stats)

### Frontend Files
- 🆕 `frontend/src/api/committeeService.js`
- 🆕 `frontend/src/constants/committee.js`
- 🆕 `frontend/src/components/dashboard/CommitteeMemberCard.jsx`
- 🆕 `frontend/src/components/dashboard/CommunityStats.jsx`
- 📝 `frontend/src/components/dashboard/index.js` (add exports)
- 📝 `frontend/src/pages/Dashboard.jsx` (major redesign)

---

## Ready to Implement?

The plan is complete and ready for implementation. Would you like me to:
1. **Start with backend** (committee members feature)?
2. **Start with frontend** (dashboard redesign using mock data)?
3. **Implement everything** in sequence?

Let me know, and I'll begin the implementation! 🚀
