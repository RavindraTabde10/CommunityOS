# Contractor Management - Phase 3 Implementation Plan

**Feature:** Contractor Management System  
**Phase:** 3  
**Estimated Time:** 4-5 days  
**Priority:** High (Next after Phase 2)  
**Created:** 2026-07-25  
**Status:** 📋 Planning

---

## 🎯 Objective

Build a comprehensive contractor management system that enables:
- Contractor registration and profile management
- Contractor specialization and skill tracking
- Issue assignment to contractors
- Work completion verification
- Rating and review system
- Performance analytics and metrics

---

## 🏗️ Architecture Overview

### Database Design

#### New Models to Create

**1. ContractorProfile (extends User model)**
```python
class ContractorProfile(Base):
    """Contractor-specific profile information"""
    __tablename__ = "contractor_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Business Information
    company_name = Column(String)
    gst_number = Column(String)
    license_number = Column(String)
    
    # Skills & Specializations (JSON array)
    specializations = Column(JSON)  # ["electrical", "plumbing", etc.]
    years_of_experience = Column(Integer)
    
    # Availability
    is_available = Column(Boolean, default=True)
    availability_status = Column(Enum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    
    # Performance Metrics
    total_jobs_completed = Column(Integer, default=0)
    average_rating = Column(Numeric(3, 2), default=0.0)  # 0.00 to 5.00
    total_ratings = Column(Integer, default=0)
    response_time_avg = Column(Integer)  # Average response time in hours
    completion_rate = Column(Numeric(5, 2), default=0.0)  # Percentage
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(String, ForeignKey("users.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="contractor_profile")
    ratings = relationship("ContractorRating", back_populates="contractor")
    work_completions = relationship("WorkCompletion", back_populates="contractor")
```

**2. ContractorRating**
```python
class ContractorRating(Base):
    """Ratings and reviews for contractors"""
    __tablename__ = "contractor_ratings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contractor_id = Column(String, ForeignKey("contractor_profiles.id", ondelete="CASCADE"), nullable=False)
    issue_id = Column(String, ForeignKey("issues.id", ondelete="SET NULL"))
    rated_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Rating Details
    rating = Column(Integer, nullable=False)  # 1 to 5
    quality_rating = Column(Integer)  # 1 to 5
    punctuality_rating = Column(Integer)  # 1 to 5
    professionalism_rating = Column(Integer)  # 1 to 5
    
    # Review
    review_text = Column(Text)
    
    # Photos (optional)
    work_photos = Column(JSON)  # Array of photo URLs
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    contractor = relationship("ContractorProfile", back_populates="ratings")
    issue = relationship("Issue")
    reviewer = relationship("User")
```

**3. WorkCompletion**
```python
class WorkCompletion(Base):
    """Work completion records and verification"""
    __tablename__ = "work_completions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, unique=True)
    contractor_id = Column(String, ForeignKey("contractor_profiles.id"), nullable=False)
    
    # Completion Details
    completed_at = Column(DateTime, nullable=False)
    work_description = Column(Text)
    materials_used = Column(JSON)  # Array of materials with costs
    labor_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    
    # Verification
    verified_by = Column(String, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Photos
    before_photos = Column(JSON)  # URLs from issue photos
    after_photos = Column(JSON)  # URLs uploaded on completion
    
    # Status
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    issue = relationship("Issue")
    contractor = relationship("ContractorProfile", back_populates="work_completions")
    verifier = relationship("User")
```

**4. Enums**
```python
class AvailabilityStatus(str, enum.Enum):
    """Contractor availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    ON_LEAVE = "on_leave"
    INACTIVE = "inactive"
```

---

## 📁 Affected Components

### Backend Files to Create/Modify

#### New Files (Create)
- [ ] `backend/app/models/contractor.py` - Contractor models
- [ ] `backend/app/schemas/contractor.py` - Contractor schemas
- [ ] `backend/app/services/contractor_service.py` - Contractor business logic
- [ ] `backend/app/api/v1/endpoints/contractors.py` - Contractor endpoints
- [ ] `backend/tests/test_contractors.py` - Contractor tests

#### Files to Modify
- [ ] `backend/app/models/__init__.py` - Add contractor models
- [ ] `backend/app/models/user.py` - Add contractor_profile relationship
- [ ] `backend/app/models/issue.py` - Enhance assigned_to logic
- [ ] `backend/app/api/v1/api.py` - Include contractor router
- [ ] `backend/app/api/v1/endpoints/issues.py` - Add assignment endpoint
- [ ] `backend/alembic/env.py` - Import new models (if needed)

#### Database Migration
- [ ] Create migration: `alembic revision --autogenerate -m "add_contractor_management_tables"`

---

## 🔌 API Endpoints

### Contractor Management

#### 1. Register Contractor Profile
```
POST /api/v1/contractors
Authorization: Bearer <token> (role: contractor, admin)

Request Body:
{
  "company_name": "ABC Electricals",
  "gst_number": "29ABCDE1234F1Z5",
  "license_number": "LIC123456",
  "specializations": ["electrical", "plumbing"],
  "years_of_experience": 5
}

Response: 201 Created
{
  "id": "uuid",
  "user_id": "user_uuid",
  "company_name": "ABC Electricals",
  "specializations": ["electrical", "plumbing"],
  "average_rating": 0.0,
  "is_verified": false,
  "created_at": "2026-07-25T10:00:00Z"
}
```

#### 2. List Contractors
```
GET /api/v1/contractors
Authorization: Bearer <token>

Query Parameters:
  - specialization: string (optional) - Filter by specialization
  - is_available: boolean (optional) - Filter by availability
  - min_rating: float (optional) - Minimum rating filter
  - is_verified: boolean (optional) - Filter verified contractors
  - skip: int (default: 0)
  - limit: int (default: 50)

Response: 200 OK
{
  "total": 45,
  "items": [
    {
      "id": "uuid",
      "user": {
        "id": "user_uuid",
        "name": "John Electrician",
        "email": "john@example.com",
        "phone": "+91-9876543210"
      },
      "company_name": "ABC Electricals",
      "specializations": ["electrical"],
      "average_rating": 4.5,
      "total_ratings": 23,
      "total_jobs_completed": 48,
      "is_available": true,
      "is_verified": true
    }
  ]
}
```

#### 3. Get Contractor Details
```
GET /api/v1/contractors/{contractor_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "uuid",
  "user": { ... },
  "company_name": "ABC Electricals",
  "gst_number": "29ABCDE1234F1Z5",
  "license_number": "LIC123456",
  "specializations": ["electrical", "plumbing"],
  "years_of_experience": 5,
  "average_rating": 4.5,
  "total_ratings": 23,
  "total_jobs_completed": 48,
  "completion_rate": 95.5,
  "response_time_avg": 2,
  "is_available": true,
  "is_verified": true,
  "recent_ratings": [...]
}
```

#### 4. Update Contractor Profile
```
PUT /api/v1/contractors/{contractor_id}
Authorization: Bearer <token> (own profile or admin)

Request Body:
{
  "company_name": "ABC Electricals Pvt Ltd",
  "specializations": ["electrical", "plumbing", "painting"],
  "is_available": false
}

Response: 200 OK
```

#### 5. Get Contractor Performance Stats
```
GET /api/v1/contractors/{contractor_id}/stats
Authorization: Bearer <token>

Response: 200 OK
{
  "contractor_id": "uuid",
  "total_jobs": 48,
  "completed_jobs": 46,
  "cancelled_jobs": 2,
  "completion_rate": 95.83,
  "average_rating": 4.5,
  "rating_breakdown": {
    "5_star": 20,
    "4_star": 15,
    "3_star": 5,
    "2_star": 2,
    "1_star": 1
  },
  "average_response_time_hours": 2,
  "jobs_by_category": {
    "electrical": 28,
    "plumbing": 20
  }
}
```

### Issue Assignment

#### 6. Assign Issue to Contractor
```
POST /api/v1/issues/{issue_id}/assign
Authorization: Bearer <token> (role: admin, facility)

Request Body:
{
  "contractor_id": "user_uuid",
  "notes": "Urgent - needs immediate attention"
}

Response: 200 OK
{
  "issue_id": "RGTS-000001",
  "assigned_to": "user_uuid",
  "assigned_at": "2026-07-25T10:00:00Z",
  "status": "in_progress"
}
```

#### 7. Unassign Contractor
```
DELETE /api/v1/issues/{issue_id}/assign
Authorization: Bearer <token> (role: admin, facility)

Response: 200 OK
```

### Work Completion

#### 8. Mark Work as Complete
```
POST /api/v1/issues/{issue_id}/complete
Authorization: Bearer <token> (role: contractor assigned to issue)

Request Body:
{
  "work_description": "Fixed electrical wiring in bathroom",
  "materials_used": [
    {"name": "Wire 2.5mm", "quantity": 10, "cost": 250},
    {"name": "MCB 32A", "quantity": 1, "cost": 120}
  ],
  "labor_cost": 500,
  "after_photos": ["url1", "url2"]
}

Response: 201 Created
{
  "id": "completion_uuid",
  "issue_id": "RGTS-000001",
  "completed_at": "2026-07-25T10:00:00Z",
  "total_cost": 870,
  "is_verified": false
}
```

#### 9. Verify Work Completion
```
POST /api/v1/work-completions/{completion_id}/verify
Authorization: Bearer <token> (role: admin, facility)

Request Body:
{
  "verification_notes": "Work quality is excellent",
  "is_approved": true
}

Response: 200 OK
```

### Rating System

#### 10. Rate Contractor
```
POST /api/v1/contractors/{contractor_id}/rate
Authorization: Bearer <token> (issue reporter only)

Request Body:
{
  "issue_id": "RGTS-000001",
  "rating": 5,
  "quality_rating": 5,
  "punctuality_rating": 4,
  "professionalism_rating": 5,
  "review_text": "Excellent work! Very professional.",
  "work_photos": ["url1", "url2"]
}

Response: 201 Created
{
  "id": "rating_uuid",
  "contractor_id": "uuid",
  "rating": 5,
  "created_at": "2026-07-25T10:00:00Z"
}
```

---

## 🔄 Implementation Steps

### Day 1: Database Models & Schemas (6-8 hours)

1. **Create contractor models** (2 hours)
   - [ ] Create `backend/app/models/contractor.py`
   - [ ] Define ContractorProfile model
   - [ ] Define ContractorRating model
   - [ ] Define WorkCompletion model
   - [ ] Define AvailabilityStatus enum
   - [ ] Add relationships

2. **Create Pydantic schemas** (2 hours)
   - [ ] Create `backend/app/schemas/contractor.py`
   - [ ] ContractorProfileCreate, ContractorProfileUpdate
   - [ ] ContractorProfileResponse, ContractorListResponse
   - [ ] ContractorRatingCreate, ContractorRatingResponse
   - [ ] WorkCompletionCreate, WorkCompletionResponse
   - [ ] ContractorStatsResponse

3. **Database migration** (1 hour)
   - [ ] Update `backend/app/models/__init__.py`
   - [ ] Update `backend/app/models/user.py` (add relationship)
   - [ ] Generate migration: `python backend/create_migration.py "add_contractor_management_tables"`
   - [ ] Review generated migration
   - [ ] Test migration: `cd backend && alembic upgrade head`
   - [ ] Verify tables created

4. **Update existing models** (1 hour)
   - [ ] Add contractor_profile relationship to User model
   - [ ] Document assignment workflow in Issue model

### Day 2: Contractor Service Layer (6-8 hours)

1. **Create contractor service** (4 hours)
   - [ ] Create `backend/app/services/contractor_service.py`
   - [ ] Implement contractor registration logic
   - [ ] Implement profile update logic
   - [ ] Implement contractor listing with filters
   - [ ] Implement availability management
   - [ ] Implement performance calculation logic
   - [ ] Add proper error handling

2. **Create rating service functions** (2 hours)
   - [ ] Implement rating creation
   - [ ] Implement rating aggregation
   - [ ] Implement automatic average calculation
   - [ ] Add rating validation (one per issue)

3. **Create work completion service** (2 hours)
   - [ ] Implement work completion recording
   - [ ] Implement verification workflow
   - [ ] Update contractor metrics on completion

### Day 3: API Endpoints (6-8 hours)

1. **Create contractor endpoints** (4 hours)
   - [ ] Create `backend/app/api/v1/endpoints/contractors.py`
   - [ ] POST /contractors - Register profile
   - [ ] GET /contractors - List contractors
   - [ ] GET /contractors/{id} - Get details
   - [ ] PUT /contractors/{id} - Update profile
   - [ ] GET /contractors/{id}/stats - Performance stats
   - [ ] Add role-based permissions
   - [ ] Add input validation

2. **Update issue endpoints** (2 hours)
   - [ ] POST /issues/{id}/assign - Assign contractor
   - [ ] DELETE /issues/{id}/assign - Unassign
   - [ ] POST /issues/{id}/complete - Mark complete
   - [ ] Update issue status on assignment

3. **Create rating endpoints** (2 hours)
   - [ ] POST /contractors/{id}/rate - Rate contractor
   - [ ] GET /contractors/{id}/ratings - List ratings
   - [ ] Add authorization checks (only issue reporter can rate)

4. **Include router** (15 minutes)
   - [ ] Update `backend/app/api/v1/api.py`
   - [ ] Include contractors router with prefix `/contractors`

### Day 4: Testing (6-8 hours)

1. **Create test file** (1 hour)
   - [ ] Create `backend/tests/test_contractors.py`
   - [ ] Set up test fixtures
   - [ ] Create test contractor profiles

2. **Unit tests for contractors** (3 hours)
   - [ ] Test contractor registration
   - [ ] Test profile updates
   - [ ] Test contractor listing with filters
   - [ ] Test availability management
   - [ ] Test permission checks

3. **Unit tests for ratings** (2 hours)
   - [ ] Test rating creation
   - [ ] Test rating validation
   - [ ] Test average calculation
   - [ ] Test duplicate rating prevention

4. **Integration tests** (2 hours)
   - [ ] Test full assignment workflow
   - [ ] Test work completion flow
   - [ ] Test rating after completion
   - [ ] Test performance metrics update

5. **Run full test suite** (30 minutes)
   - [ ] `cd backend && python run_tests.py`
   - [ ] Ensure all tests pass
   - [ ] Check test coverage

### Day 5: Documentation & Polish (4-6 hours)

1. **Update documentation** (2 hours)
   - [ ] Update `backend/API_README.md` with new endpoints
   - [ ] Update `REFERENCE.md` with contractor models
   - [ ] Add contractor management section
   - [ ] Document rating workflow
   - [ ] Add usage examples

2. **Update implementation checklist** (30 minutes)
   - [ ] Update `IMPLEMENTATION_CHECKLIST.md`
   - [ ] Mark Phase 3 Contractor Management as complete

3. **Test with Swagger UI** (1 hour)
   - [ ] Start backend: `cd backend && uvicorn app.main:app --reload`
   - [ ] Open http://127.0.0.1:8000/api/docs
   - [ ] Test each endpoint manually
   - [ ] Verify request/response schemas

4. **Create sample data** (1 hour)
   - [ ] Create script to seed contractor data
   - [ ] Add 3-5 sample contractors
   - [ ] Add sample ratings
   - [ ] Add sample work completions

5. **Edge case testing** (1 hour)
   - [ ] Test assignment to unavailable contractor
   - [ ] Test rating without work completion
   - [ ] Test unauthorized access attempts
   - [ ] Test invalid data inputs

---

## ✅ Testing Plan

### Unit Tests (backend/tests/test_contractors.py)

#### Contractor Profile Tests
- [ ] `test_create_contractor_profile_success`
- [ ] `test_create_contractor_profile_without_user`
- [ ] `test_create_contractor_profile_duplicate`
- [ ] `test_update_contractor_profile_success`
- [ ] `test_update_contractor_profile_unauthorized`
- [ ] `test_list_contractors_all`
- [ ] `test_list_contractors_filter_by_specialization`
- [ ] `test_list_contractors_filter_by_rating`
- [ ] `test_list_contractors_available_only`
- [ ] `test_get_contractor_details_success`
- [ ] `test_get_contractor_details_not_found`

#### Assignment Tests
- [ ] `test_assign_issue_to_contractor_success`
- [ ] `test_assign_issue_updates_status`
- [ ] `test_assign_issue_to_unavailable_contractor`
- [ ] `test_assign_issue_unauthorized`
- [ ] `test_unassign_contractor_success`
- [ ] `test_reassign_issue_to_different_contractor`

#### Work Completion Tests
- [ ] `test_mark_work_complete_success`
- [ ] `test_mark_work_complete_unassigned_issue`
- [ ] `test_mark_work_complete_wrong_contractor`
- [ ] `test_verify_work_completion_success`
- [ ] `test_verify_work_completion_unauthorized`
- [ ] `test_work_completion_updates_metrics`

#### Rating Tests
- [ ] `test_rate_contractor_success`
- [ ] `test_rate_contractor_updates_average`
- [ ] `test_rate_contractor_duplicate_prevents`
- [ ] `test_rate_contractor_without_completion`
- [ ] `test_rate_contractor_unauthorized`
- [ ] `test_rating_by_non_reporter_fails`

#### Performance Tests
- [ ] `test_contractor_stats_calculation`
- [ ] `test_completion_rate_calculation`
- [ ] `test_rating_breakdown`

### Integration Tests
- [ ] Full workflow: Register → Assign → Complete → Rate
- [ ] Permission checks across all endpoints
- [ ] Cascade deletes work correctly

### Manual Testing Checklist
- [ ] Admin can assign any issue to any contractor
- [ ] Contractor sees only assigned issues
- [ ] Resident can rate only their own issues
- [ ] Rating affects contractor average immediately
- [ ] Work completion updates metrics
- [ ] Filter contractors by specialization works
- [ ] Unavailable contractors marked correctly

---

## 📝 Documentation Updates

### Files to Update

#### backend/API_README.md
- [ ] Add "Contractor Management" section
- [ ] Document all 10 new endpoints
- [ ] Add request/response examples
- [ ] Document permission requirements
- [ ] Add workflow diagrams

#### REFERENCE.md
- [ ] Add ContractorProfile model
- [ ] Add ContractorRating model
- [ ] Add WorkCompletion model
- [ ] Add AvailabilityStatus enum
- [ ] Document relationships
- [ ] Add example queries

#### IMPLEMENTATION_CHECKLIST.md
- [ ] Update Phase 3 status
- [ ] Mark Contractor Management as ✅ Complete
- [ ] Add completion date

---

## 🔧 Dependencies

### New Python Packages
None required - all dependencies already in requirements.txt

### Environment Variables
No new environment variables needed

### Database
- Requires migration to add 3 new tables
- Adds relationship to existing User model

---

## 🚨 Rollback Plan

If something goes wrong:

1. **Rollback database migration**
   ```bash
   cd backend
   alembic downgrade -1
   ```

2. **Remove new files**
   - Delete `backend/app/models/contractor.py`
   - Delete `backend/app/schemas/contractor.py`
   - Delete `backend/app/services/contractor_service.py`
   - Delete `backend/app/api/v1/endpoints/contractors.py`

3. **Revert modified files**
   - Revert `backend/app/models/__init__.py`
   - Revert `backend/app/models/user.py`
   - Revert `backend/app/api/v1/api.py`

4. **Test application**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

---

## ⚠️ Risks & Considerations

### Technical Risks
1. **Performance:** Calculating contractor stats on every request
   - **Mitigation:** Cache stats, update only on rating/completion
   
2. **Data integrity:** Multiple ratings for same issue
   - **Mitigation:** Add unique constraint (contractor_id, issue_id)

3. **Assignment conflicts:** Issue assigned to multiple contractors
   - **Mitigation:** Issue can have only one assigned_to at a time

### Business Logic Considerations
1. **Rating eligibility:** Only issue reporter can rate
2. **Work completion:** Only assigned contractor can mark complete
3. **Verification required:** Work must be verified before rating (optional)
4. **Contractor deactivation:** Handle active assignments when deactivating

---

## 📊 Success Metrics

### Development Metrics
- [ ] All 3 models created and migrated
- [ ] All 10 API endpoints functional
- [ ] 25+ test cases passing
- [ ] Test coverage > 80%
- [ ] Documentation complete

### Functional Metrics
- [ ] Contractor can register profile
- [ ] Admin can assign issues
- [ ] Contractor can mark work complete
- [ ] Resident can rate contractor
- [ ] Performance stats calculate correctly
- [ ] Filtering works for all criteria

---

## 🎯 Next Steps After Completion

1. **Phase 3 - Asset Management**
   - Build on contractor system for maintenance scheduling
   - Use contractor ratings for vendor selection

2. **Phase 4 - Reports & Analytics**
   - Contractor performance reports
   - Cost analysis by contractor
   - Issue resolution trends

3. **Future Enhancements**
   - Multi-contractor assignment (for large jobs)
   - Contractor bidding system
   - Automated contractor selection based on ratings
   - Contractor mobile app integration

---

## 📌 Notes

- Contractor management builds on existing User/Issue models
- Uses existing authentication and role system
- Follows established patterns from comments/activity implementation
- Performance metrics calculated on-the-fly initially, can be cached later
- Rating system is simple but extensible (can add categories later)

---

**Ready to Proceed?** 🚀

Once approved, we'll start with Day 1 (Database Models & Schemas).
