# Feature: Issue Comments & Activity Log

**Status:** Ready for Implementation  
**Estimated Time:** 2 days  
**Priority:** High (Phase 2, Feature #3)

---

## 📋 Objective

Implement a comprehensive commenting and activity tracking system for issues:
- Users can add, view, update, and delete comments on issues
- System automatically tracks all issue changes (status, priority, assignment, etc.)
- Activity log provides audit trail for issue lifecycle
- Role-based permissions for comment management

---

## 🎯 Affected Components

### Backend Files to Create
- [ ] `backend/app/models/comment.py` - Comment model
- [ ] `backend/app/models/activity.py` - Activity log model
- [ ] `backend/app/schemas/comment.py` - Comment schemas
- [ ] `backend/app/schemas/activity.py` - Activity schemas
- [ ] `backend/app/api/v1/endpoints/comments.py` - Comment endpoints
- [ ] `backend/alembic/versions/[timestamp]_add_comments_and_activity.py` - Migration

### Backend Files to Modify
- [ ] `backend/app/models/__init__.py` - Import new models
- [ ] `backend/app/api/v1/api.py` - Include comment router
- [ ] `backend/app/api/v1/endpoints/issues.py` - Add activity logging on updates

### Documentation to Update
- [ ] `backend/API_README.md` - Add comment endpoints
- [ ] `REFERENCE.md` - Add Comment and Activity models
- [ ] `backend/API_IMPLEMENTATION_PLAN.md` - Mark as completed

---

## 🏗️ Implementation Steps

### 1. Database Models (30 min)

#### Comment Model
```python
# backend/app/models/comment.py
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")
    user = relationship("User", back_populates="comments")
```

#### Activity Model
```python
# backend/app/models/activity.py
class IssueActivity(Base):
    __tablename__ = "issue_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(50), nullable=False)  # created, updated, status_changed, etc.
    field_name = Column(String(50))  # What changed
    old_value = Column(Text)
    new_value = Column(Text)
    description = Column(Text)  # Human-readable description
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    issue = relationship("Issue", back_populates="activities")
    user = relationship("User")
```

### 2. Update Issue Model (10 min)
Add relationships to Issue model:
```python
# backend/app/models/issue.py
comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
activities = relationship("IssueActivity", back_populates="issue", cascade="all, delete-orphan")
```

### 3. Pydantic Schemas (30 min)

#### Comment Schemas
```python
# backend/app/schemas/comment.py
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class CommentResponse(CommentBase):
    id: int
    issue_id: int
    user_id: int
    user_name: str
    user_email: str
    created_at: datetime
    updated_at: datetime
    is_own: bool = False  # Set dynamically
    
    class Config:
        from_attributes = True
```

#### Activity Schemas
```python
# backend/app/schemas/activity.py
class ActivityResponse(BaseModel):
    id: int
    issue_id: int
    user_id: Optional[int]
    user_name: Optional[str]
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 4. Database Migration (15 min)
Create migration for comments and activities tables:
```bash
alembic revision --autogenerate -m "add comments and activity tables"
alembic upgrade head
```

### 5. API Endpoints - Comments (60 min)

#### POST /api/v1/issues/{issue_id}/comments
- Create new comment on issue
- Validate user has access to issue
- Log activity: "commented on issue"
- Return CommentResponse

#### GET /api/v1/issues/{issue_id}/comments
- List all comments for issue
- Pagination support (skip/limit)
- Order by created_at DESC
- Mark is_own flag for current user's comments

#### PUT /api/v1/comments/{comment_id}
- Update comment content
- Only comment owner or admin can update
- Check if comment exists and not deleted
- Update updated_at timestamp
- Log activity: "edited comment"

#### DELETE /api/v1/comments/{comment_id}
- Soft delete (set is_deleted=True)
- Only comment owner or admin can delete
- Log activity: "deleted comment"
- Alternative: Hard delete with CASCADE

### 6. API Endpoints - Activity (30 min)

#### GET /api/v1/issues/{issue_id}/activity
- List all activities for issue
- Order by created_at DESC
- Pagination support
- Include user names for each activity

### 7. Activity Logging Helper (45 min)

Create helper function in issues.py:
```python
def log_issue_activity(
    db: Session,
    issue_id: int,
    user_id: int,
    action: str,
    field_name: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    description: Optional[str] = None
):
    activity = IssueActivity(
        issue_id=issue_id,
        user_id=user_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        description=description or f"User {action} the issue"
    )
    db.add(activity)
    db.commit()
```

Integrate into existing endpoints:
- Issue created → log_activity(..., action="created")
- Issue updated → log_activity(..., action="updated", field_name="status", old_value, new_value)
- Issue deleted → log_activity(..., action="deleted")
- Issue assigned → log_activity(..., action="assigned")

---

## 🧪 Testing Plan

### Manual Testing via Swagger UI
- [ ] Create comment on own issue
- [ ] Create comment on another user's issue (should work for admins)
- [ ] List comments for issue with pagination
- [ ] Update own comment
- [ ] Try to update another user's comment (should fail unless admin)
- [ ] Delete own comment
- [ ] Try to delete another user's comment (should fail unless admin)
- [ ] View activity log after creating/updating/deleting issue
- [ ] Verify activity log tracks all changes

### Test Cases to Write
```python
# backend/tests/test_comments.py
- test_create_comment_success
- test_create_comment_on_nonexistent_issue
- test_create_comment_no_auth
- test_list_comments_with_pagination
- test_update_own_comment
- test_update_other_user_comment_forbidden
- test_admin_can_update_any_comment
- test_delete_own_comment
- test_delete_other_user_comment_forbidden
- test_admin_can_delete_any_comment
- test_get_issue_activity_log
- test_activity_log_tracks_issue_changes
```

### Edge Cases
- [ ] Empty comment content
- [ ] Very long comment (>2000 chars)
- [ ] Delete already deleted comment
- [ ] Comment on deleted issue
- [ ] Pagination with no comments

---

## 📚 Documentation Updates

### backend/API_README.md
Add new section: "Comments & Activity"
```markdown
## Comments

### Create Comment
POST /api/v1/issues/{issue_id}/comments

### List Comments
GET /api/v1/issues/{issue_id}/comments?skip=0&limit=50

### Update Comment
PUT /api/v1/comments/{comment_id}

### Delete Comment
DELETE /api/v1/comments/{comment_id}

## Activity Log

### Get Issue Activity
GET /api/v1/issues/{issue_id}/activity?skip=0&limit=50
```

### REFERENCE.md
Add Comment and Activity models to database schema section

---

## 🔄 Dependencies

### New Packages
- None (uses existing dependencies)

### Environment Variables
- None (uses existing configuration)

---

## 🚨 Rollback Plan

If issues arise:
1. Revert migration: `alembic downgrade -1`
2. Remove comment router from api.py
3. Delete comment and activity model files
4. Restart backend: `uvicorn app.main:app --reload`

---

## 📋 Checklist

- [ ] Create Comment model
- [ ] Create Activity model
- [ ] Update Issue model relationships
- [ ] Create comment schemas
- [ ] Create activity schemas
- [ ] Generate database migration
- [ ] Apply migration
- [ ] Implement comment endpoints
- [ ] Implement activity endpoint
- [ ] Add activity logging to issue endpoints
- [ ] Test all endpoints manually
- [ ] Write automated tests
- [ ] Update API_README.md
- [ ] Update REFERENCE.md
- [ ] Update API_IMPLEMENTATION_PLAN.md
- [ ] Commit changes

---

## 🎯 Success Criteria

- ✅ Users can comment on issues
- ✅ Comments have proper permissions (owner/admin can edit/delete)
- ✅ Activity log tracks all issue changes
- ✅ Pagination works for comments and activities
- ✅ All tests pass
- ✅ Documentation is updated
- ✅ No breaking changes to existing functionality
