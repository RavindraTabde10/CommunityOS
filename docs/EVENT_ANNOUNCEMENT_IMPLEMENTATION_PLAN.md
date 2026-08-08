# Event Announcement Feature - Implementation Plan

**Feature**: Event Announcement with Moving Text Display on Dashboard  
**Created**: 2026-07-29  
**Status**: Planning

---

## 📋 Overview

### Purpose
Add functionality for administrators to create, update, and manage event announcements that will be displayed as scrolling/moving text on the dashboard for all users (residents and admins).

### Key Requirements
1. **Admin-Only Management**: Only administrators can create, update, and delete announcements
2. **Dashboard Display**: Active announcements displayed as moving/scrolling text on both user and admin dashboards
3. **Multi-Tenant Support**: Announcements are organization-scoped (each society manages their own)
4. **Active Status Control**: Admins can activate/deactivate announcements
5. **Priority System**: Support for different priority levels (affects display order)
6. **Date Range**: Optional start and end dates for announcements

---

## 🎯 User Stories

### Admin User Stories
- **As an admin**, I want to create event announcements so that residents are informed about upcoming events
- **As an admin**, I want to update existing announcements so that I can correct or modify information
- **As an admin**, I want to activate/deactivate announcements so that I can control what residents see
- **As an admin**, I want to delete old announcements so that the system stays organized
- **As an admin**, I want to set announcement priority so that important messages appear first
- **As an admin**, I want to set date ranges so that announcements automatically expire

### Resident User Stories
- **As a resident**, I want to see active announcements on my dashboard so that I stay informed about society events
- **As a resident**, I want announcements displayed in an eye-catching way so that I don't miss important information

---

## 🏗️ Architecture

### Backend Components

```
backend/
├── app/
│   ├── models/
│   │   └── announcement.py          [NEW] - Announcement ORM model
│   ├── schemas/
│   │   └── announcement.py          [NEW] - Pydantic schemas
│   ├── services/
│   │   └── announcement_service.py  [NEW] - Business logic
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── announcements.py [NEW] - API endpoints
│   │       └── api.py               [MODIFY] - Register new router
│   └── core/
│       └── permissions.py           [REFERENCE] - Check admin permissions
└── alembic/
    └── versions/
        └── XXXXX_add_announcements_table.py [NEW] - Migration file
```

### Frontend Components

```
frontend/
├── src/
│   ├── api/
│   │   └── announcementService.js       [NEW] - API client
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── AnnouncementMarquee.jsx  [NEW] - Scrolling text component
│   │   │   └── index.js                 [MODIFY] - Export new component
│   │   └── admin/
│   │       ├── AnnouncementList.jsx     [NEW] - List view
│   │       ├── AnnouncementForm.jsx     [NEW] - Create/Edit form
│   │       └── AnnouncementManager.jsx  [NEW] - Main management component
│   ├── pages/
│   │   ├── Dashboard.jsx                [MODIFY] - Add marquee component
│   │   └── AnnouncementManagement.jsx   [NEW] - Admin page
│   └── constants/
│       └── announcements.js             [NEW] - Constants (priority levels, etc.)
```

---

## 📊 Database Schema

### Announcement Table

```sql
CREATE TABLE announcements (
    id VARCHAR PRIMARY KEY,                    -- UUID format
    organization_id VARCHAR NOT NULL,          -- Multi-tenant support
    title VARCHAR(200) NOT NULL,               -- Announcement title
    content TEXT NOT NULL,                     -- Full announcement text
    priority VARCHAR(20) DEFAULT 'normal',     -- 'low', 'normal', 'high', 'critical'
    is_active BOOLEAN DEFAULT TRUE,            -- Active status
    start_date DATETIME,                       -- Optional: when to start showing
    end_date DATETIME,                         -- Optional: when to stop showing
    created_by VARCHAR NOT NULL,               -- User ID of creator
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_announcements_org_active ON announcements(organization_id, is_active);
CREATE INDEX idx_announcements_dates ON announcements(start_date, end_date);
```

### Enumerations

```python
class AnnouncementPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
```

---

## 🔧 Implementation Details

### Phase 1: Backend Implementation

#### Step 1.1: Create Database Model
**File**: `backend/app/models/announcement.py`

```python
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base

class AnnouncementPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Enum(AnnouncementPriority), default=AnnouncementPriority.NORMAL)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", backref="announcements")
    creator = relationship("User", backref="created_announcements")
```

#### Step 1.2: Create Pydantic Schemas
**File**: `backend/app/schemas/announcement.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AnnouncementPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class AnnouncementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    priority: AnnouncementPriority = AnnouncementPriority.NORMAL
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    priority: Optional[AnnouncementPriority] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AnnouncementResponse(AnnouncementBase):
    id: str
    organization_id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True
```

#### Step 1.3: Create Service Layer
**File**: `backend/app/services/announcement_service.py`

```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
import uuid

from app.models.announcement import Announcement, AnnouncementPriority
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate

class AnnouncementService:
    
    @staticmethod
    def create_announcement(
        db: Session,
        announcement_data: AnnouncementCreate,
        organization_id: str,
        created_by: str
    ) -> Announcement:
        """Create new announcement"""
        announcement = Announcement(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            created_by=created_by,
            **announcement_data.model_dump()
        )
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return announcement
    
    @staticmethod
    def get_active_announcements(
        db: Session,
        organization_id: str
    ) -> List[Announcement]:
        """Get all active announcements for an organization"""
        now = datetime.utcnow()
        
        query = db.query(Announcement).filter(
            and_(
                Announcement.organization_id == organization_id,
                Announcement.is_active == True,
                or_(
                    Announcement.start_date.is_(None),
                    Announcement.start_date <= now
                ),
                or_(
                    Announcement.end_date.is_(None),
                    Announcement.end_date >= now
                )
            )
        ).order_by(
            Announcement.priority.desc(),
            Announcement.created_at.desc()
        )
        
        return query.all()
    
    @staticmethod
    def get_all_announcements(
        db: Session,
        organization_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Announcement]:
        """Get all announcements (admin view)"""
        return db.query(Announcement).filter(
            Announcement.organization_id == organization_id
        ).order_by(
            Announcement.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_announcement_by_id(
        db: Session,
        announcement_id: str,
        organization_id: str
    ) -> Optional[Announcement]:
        """Get announcement by ID"""
        return db.query(Announcement).filter(
            and_(
                Announcement.id == announcement_id,
                Announcement.organization_id == organization_id
            )
        ).first()
    
    @staticmethod
    def update_announcement(
        db: Session,
        announcement: Announcement,
        update_data: AnnouncementUpdate
    ) -> Announcement:
        """Update announcement"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(announcement, field, value)
        
        db.commit()
        db.refresh(announcement)
        return announcement
    
    @staticmethod
    def delete_announcement(
        db: Session,
        announcement: Announcement
    ) -> None:
        """Delete announcement"""
        db.delete(announcement)
        db.commit()
```

#### Step 1.4: Create API Endpoints
**File**: `backend/app/api/v1/endpoints/announcements.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user, require_admin
from app.models.user import User
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse
)
from app.services.announcement_service import AnnouncementService

router = APIRouter()

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new announcement (Admin only)"""
    announcement = AnnouncementService.create_announcement(
        db=db,
        announcement_data=announcement_data,
        organization_id=current_user.organization_id,
        created_by=current_user.id
    )
    return announcement

@router.get("/active", response_model=List[AnnouncementResponse])
async def get_active_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active announcements (All users)"""
    announcements = AnnouncementService.get_active_announcements(
        db=db,
        organization_id=current_user.organization_id
    )
    return announcements

@router.get("/", response_model=List[AnnouncementResponse])
async def get_all_announcements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all announcements (Admin only)"""
    announcements = AnnouncementService.get_all_announcements(
        db=db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    return announcements

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get announcement by ID"""
    announcement = AnnouncementService.get_announcement_by_id(
        db=db,
        announcement_id=announcement_id,
        organization_id=current_user.organization_id
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    return announcement

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: str,
    update_data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update announcement (Admin only)"""
    announcement = AnnouncementService.get_announcement_by_id(
        db=db,
        announcement_id=announcement_id,
        organization_id=current_user.organization_id
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    updated_announcement = AnnouncementService.update_announcement(
        db=db,
        announcement=announcement,
        update_data=update_data
    )
    return updated_announcement

@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete announcement (Admin only)"""
    announcement = AnnouncementService.get_announcement_by_id(
        db=db,
        announcement_id=announcement_id,
        organization_id=current_user.organization_id
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    AnnouncementService.delete_announcement(db=db, announcement=announcement)
    return None
```

#### Step 1.5: Register Router
**File**: `backend/app/api/v1/api.py` (Modify)

Add this line:
```python
from app.api.v1.endpoints import announcements
api_router.include_router(announcements.router, prefix="/announcements", tags=["Announcements"])
```

#### Step 1.6: Update Models __init__.py
**File**: `backend/app/models/__init__.py` (Modify)

Add import:
```python
from app.models.announcement import Announcement, AnnouncementPriority
```

#### Step 1.7: Create Database Migration
```bash
cd backend
alembic revision --autogenerate -m "add_announcements_table"
alembic upgrade head
```

---

### Phase 2: Frontend Implementation

#### Step 2.1: Create API Service
**File**: `frontend/src/api/announcementService.js`

```javascript
import apiClient from './apiClient'

const announcementService = {
  // Get active announcements (all users)
  getActiveAnnouncements: async () => {
    const response = await apiClient.get('/announcements/active')
    return response.data
  },

  // Get all announcements (admin only)
  getAllAnnouncements: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/announcements/', {
      params: { skip, limit }
    })
    return response.data
  },

  // Get single announcement
  getAnnouncement: async (announcementId) => {
    const response = await apiClient.get(`/announcements/${announcementId}`)
    return response.data
  },

  // Create announcement (admin only)
  createAnnouncement: async (announcementData) => {
    const response = await apiClient.post('/announcements/', announcementData)
    return response.data
  },

  // Update announcement (admin only)
  updateAnnouncement: async (announcementId, updateData) => {
    const response = await apiClient.put(`/announcements/${announcementId}`, updateData)
    return response.data
  },

  // Delete announcement (admin only)
  deleteAnnouncement: async (announcementId) => {
    await apiClient.delete(`/announcements/${announcementId}`)
  }
}

export default announcementService
```

#### Step 2.2: Create Marquee Component
**File**: `frontend/src/components/dashboard/AnnouncementMarquee.jsx`

```jsx
import { useState, useEffect } from 'react'
import { Box, Typography, Paper, Chip } from '@mui/material'
import { keyframes } from '@mui/system'
import CampaignIcon from '@mui/icons-material/Campaign'
import announcementService from '../../api/announcementService'

const scrollText = keyframes`
  0% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(-100%);
  }
`

const AnnouncementMarquee = () => {
  const [announcements, setAnnouncements] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadActiveAnnouncements()
    // Refresh every 5 minutes
    const interval = setInterval(loadActiveAnnouncements, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const loadActiveAnnouncements = async () => {
    try {
      const data = await announcementService.getActiveAnnouncements()
      setAnnouncements(data)
    } catch (error) {
      console.error('Error loading announcements:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || announcements.length === 0) {
    return null
  }

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'error',
      high: 'warning',
      normal: 'info',
      low: 'default'
    }
    return colors[priority] || 'info'
  }

  return (
    <Paper
      elevation={0}
      sx={{
        mb: 3,
        overflow: 'hidden',
        background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: 2,
        position: 'relative'
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 2,
          py: 1.5,
          gap: 2
        }}
      >
        <CampaignIcon sx={{ color: 'primary.main', fontSize: 28 }} />
        
        <Box
          sx={{
            flex: 1,
            overflow: 'hidden',
            position: 'relative',
            minHeight: '32px'
          }}
        >
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 3,
              animation: `${scrollText} ${announcements.length * 15}s linear infinite`,
              whiteSpace: 'nowrap'
            }}
          >
            {announcements.map((announcement, index) => (
              <Box key={announcement.id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={announcement.priority}
                  size="small"
                  color={getPriorityColor(announcement.priority)}
                  sx={{ fontWeight: 600, textTransform: 'uppercase' }}
                />
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 500,
                    color: 'text.primary'
                  }}
                >
                  {announcement.title}: {announcement.content}
                </Typography>
                {index < announcements.length - 1 && (
                  <Typography sx={{ mx: 2, color: 'text.secondary' }}>•</Typography>
                )}
              </Box>
            ))}
          </Box>
        </Box>
      </Box>
    </Paper>
  )
}

export default AnnouncementMarquee
```

#### Step 2.3: Create Admin Management Components

**File**: `frontend/src/components/admin/AnnouncementForm.jsx`

```jsx
import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Grid,
  Box
} from '@mui/material'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import dayjs from 'dayjs'

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low' },
  { value: 'normal', label: 'Normal' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' }
]

const AnnouncementForm = ({ open, onClose, onSubmit, announcement = null, loading = false }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    priority: 'normal',
    is_active: true,
    start_date: null,
    end_date: null
  })

  useEffect(() => {
    if (announcement) {
      setFormData({
        title: announcement.title || '',
        content: announcement.content || '',
        priority: announcement.priority || 'normal',
        is_active: announcement.is_active ?? true,
        start_date: announcement.start_date ? dayjs(announcement.start_date) : null,
        end_date: announcement.end_date ? dayjs(announcement.end_date) : null
      })
    } else {
      // Reset form for new announcement
      setFormData({
        title: '',
        content: '',
        priority: 'normal',
        is_active: true,
        start_date: null,
        end_date: null
      })
    }
  }, [announcement, open])

  const handleChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }))
  }

  const handleSwitchChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.checked
    }))
  }

  const handleDateChange = (field) => (newValue) => {
    setFormData(prev => ({
      ...prev,
      [field]: newValue
    }))
  }

  const handleSubmit = () => {
    const submitData = {
      ...formData,
      start_date: formData.start_date ? formData.start_date.toISOString() : null,
      end_date: formData.end_date ? formData.end_date.toISOString() : null
    }
    onSubmit(submitData)
  }

  const isFormValid = formData.title.trim() && formData.content.trim()

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {announcement ? 'Edit Announcement' : 'Create New Announcement'}
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={handleChange('title')}
                required
                inputProps={{ maxLength: 200 }}
                helperText={`${formData.title.length}/200 characters`}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Content"
                value={formData.content}
                onChange={handleChange('content')}
                required
                multiline
                rows={4}
                helperText="Announcement message to display"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={handleChange('priority')}
                  label="Priority"
                >
                  {PRIORITY_OPTIONS.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleSwitchChange('is_active')}
                    color="primary"
                  />
                }
                label="Active"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DateTimePicker
                  label="Start Date (Optional)"
                  value={formData.start_date}
                  onChange={handleDateChange('start_date')}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DateTimePicker
                  label="End Date (Optional)"
                  value={formData.end_date}
                  onChange={handleDateChange('end_date')}
                  slotProps={{ textField: { fullWidth: true } }}
                  minDateTime={formData.start_date || undefined}
                />
              </LocalizationProvider>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!isFormValid || loading}
        >
          {announcement ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default AnnouncementForm
```

**File**: `frontend/src/pages/AnnouncementManagement.jsx`

```jsx
import { useState, useEffect } from 'react'
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import { toast } from 'react-toastify'
import announcementService from '../api/announcementService'
import AnnouncementForm from '../components/admin/AnnouncementForm'
import { format } from 'date-fns'

const AnnouncementManagement = () => {
  const [announcements, setAnnouncements] = useState([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [selectedAnnouncement, setSelectedAnnouncement] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadAnnouncements()
  }, [])

  const loadAnnouncements = async () => {
    try {
      setLoading(true)
      const data = await announcementService.getAllAnnouncements()
      setAnnouncements(data)
    } catch (error) {
      console.error('Error loading announcements:', error)
      toast.error('Failed to load announcements')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedAnnouncement(null)
    setFormOpen(true)
  }

  const handleEdit = (announcement) => {
    setSelectedAnnouncement(announcement)
    setFormOpen(true)
  }

  const handleDelete = async (announcementId) => {
    if (!window.confirm('Are you sure you want to delete this announcement?')) {
      return
    }

    try {
      await announcementService.deleteAnnouncement(announcementId)
      toast.success('Announcement deleted successfully')
      loadAnnouncements()
    } catch (error) {
      console.error('Error deleting announcement:', error)
      toast.error('Failed to delete announcement')
    }
  }

  const handleFormSubmit = async (formData) => {
    try {
      setSubmitting(true)
      if (selectedAnnouncement) {
        await announcementService.updateAnnouncement(selectedAnnouncement.id, formData)
        toast.success('Announcement updated successfully')
      } else {
        await announcementService.createAnnouncement(formData)
        toast.success('Announcement created successfully')
      }
      setFormOpen(false)
      loadAnnouncements()
    } catch (error) {
      console.error('Error saving announcement:', error)
      toast.error('Failed to save announcement')
    } finally {
      setSubmitting(false)
    }
  }

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'error',
      high: 'warning',
      normal: 'info',
      low: 'default'
    }
    return colors[priority] || 'info'
  }

  const formatDate = (dateString) => {
    return dateString ? format(new Date(dateString), 'MMM dd, yyyy HH:mm') : '-'
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" fontWeight="bold">
          Announcement Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          Create Announcement
        </Button>
      </Box>

      {announcements.length === 0 && !loading && (
        <Alert severity="info">
          No announcements yet. Create your first announcement to get started!
        </Alert>
      )}

      {announcements.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Title</strong></TableCell>
                <TableCell><strong>Priority</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Start Date</strong></TableCell>
                <TableCell><strong>End Date</strong></TableCell>
                <TableCell><strong>Created</strong></TableCell>
                <TableCell align="right"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {announcements.map((announcement) => (
                <TableRow key={announcement.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="500">
                      {announcement.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {announcement.content.substring(0, 60)}
                      {announcement.content.length > 60 && '...'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={announcement.priority}
                      size="small"
                      color={getPriorityColor(announcement.priority)}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={announcement.is_active ? 'Active' : 'Inactive'}
                      size="small"
                      color={announcement.is_active ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{formatDate(announcement.start_date)}</TableCell>
                  <TableCell>{formatDate(announcement.end_date)}</TableCell>
                  <TableCell>{formatDate(announcement.created_at)}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleEdit(announcement)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(announcement.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <AnnouncementForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        announcement={selectedAnnouncement}
        loading={submitting}
      />
    </Container>
  )
}

export default AnnouncementManagement
```

#### Step 2.4: Update Dashboard Component
**File**: `frontend/src/pages/Dashboard.jsx` (Modify)

Add import and component at the top of the dashboard:
```jsx
import AnnouncementMarquee from '../components/dashboard/AnnouncementMarquee'

// Inside the Dashboard component, add this after the header:
<AnnouncementMarquee />
```

#### Step 2.5: Add Route for Admin Management
**File**: `frontend/src/App.jsx` (Modify)

Add route for announcement management (admin only):
```jsx
import AnnouncementManagement from './pages/AnnouncementManagement'

// In the routes section:
<Route path="/announcements" element={<AnnouncementManagement />} />
```

---

## 🧪 Testing Checklist

### Backend Testing

- [ ] **Model Creation**
  - [ ] Test database migration runs successfully
  - [ ] Verify table created with correct schema
  - [ ] Test foreign key relationships

- [ ] **API Endpoints** (Test via Swagger UI: http://127.0.0.1:8000/api/docs)
  - [ ] POST `/api/v1/announcements/` - Create announcement (admin only)
  - [ ] GET `/api/v1/announcements/active` - Get active announcements (all users)
  - [ ] GET `/api/v1/announcements/` - Get all announcements (admin only)
  - [ ] GET `/api/v1/announcements/{id}` - Get single announcement
  - [ ] PUT `/api/v1/announcements/{id}` - Update announcement (admin only)
  - [ ] DELETE `/api/v1/announcements/{id}` - Delete announcement (admin only)

- [ ] **Authorization**
  - [ ] Verify non-admin users cannot create announcements
  - [ ] Verify non-admin users cannot update announcements
  - [ ] Verify non-admin users cannot delete announcements
  - [ ] Verify all users can view active announcements

- [ ] **Business Logic**
  - [ ] Test date range filtering (start_date, end_date)
  - [ ] Test is_active filtering
  - [ ] Test priority ordering
  - [ ] Test multi-tenant isolation (organization_id)

### Frontend Testing

- [ ] **Dashboard Display**
  - [ ] Verify marquee appears on dashboard when announcements exist
  - [ ] Verify marquee doesn't appear when no active announcements
  - [ ] Test scrolling animation works smoothly
  - [ ] Verify priority colors display correctly
  - [ ] Test auto-refresh (5-minute interval)

- [ ] **Admin Management**
  - [ ] Test create announcement form
  - [ ] Test edit announcement form
  - [ ] Test delete announcement
  - [ ] Test form validation (required fields)
  - [ ] Test date picker functionality
  - [ ] Test priority selection
  - [ ] Test active/inactive toggle

- [ ] **Responsive Design**
  - [ ] Test on desktop
  - [ ] Test on tablet
  - [ ] Test on mobile

---

## 📝 Documentation Updates

After implementation, update the following files:

1. **REFERENCE.md** - Add announcement API endpoints
2. **API_IMPLEMENTATION_PLAN.md** - Mark announcements as implemented
3. **IMPLEMENTATION_CHECKLIST.md** - Add announcement feature completion
4. **README.md** - Mention announcement feature in features list

---

## 🚀 Deployment Notes

### Environment Variables
No new environment variables required.

### Database Migration
Run before deployment:
```bash
cd backend
alembic upgrade head
```

### Dependencies
Frontend may need additional packages:
```bash
cd frontend
npm install @mui/x-date-pickers dayjs
```

---

## 🔄 Future Enhancements

- [ ] Rich text editor for announcement content
- [ ] Image/media attachments
- [ ] Notification system integration
- [ ] Announcement categories
- [ ] Scheduled publishing
- [ ] View analytics (how many users saw the announcement)
- [ ] Multiple announcement display styles (banner, toast, modal)
- [ ] User acknowledgment tracking

---

## 📊 Success Criteria

✅ **Backend Complete**
- Announcement model created with all required fields
- Database migration runs successfully
- All API endpoints functional
- Admin-only operations properly secured
- Date range filtering works correctly

✅ **Frontend Complete**
- Marquee component displays active announcements
- Scrolling animation smooth and attractive
- Admin can create/edit/delete announcements
- Form validation prevents invalid data
- Responsive design works on all screen sizes

✅ **Documentation Complete**
- Implementation plan documented
- API reference updated
- Testing checklist completed

---

## 🎯 Timeline Estimate

- **Backend Implementation**: 2-3 hours
- **Frontend Implementation**: 3-4 hours
- **Testing**: 1-2 hours
- **Documentation**: 30 minutes

**Total**: 7-10 hours

---

## 👥 Stakeholders

- **Admin Users**: Can manage announcements
- **Resident Users**: Can view active announcements
- **System Admin**: Maintains the feature

---

## ✅ Sign-off

- [ ] Plan reviewed and approved
- [ ] Backend implementation complete
- [ ] Frontend implementation complete
- [ ] Testing complete
- [ ] Documentation updated
- [ ] Feature deployed

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-29  
**Status**: Ready for Implementation
