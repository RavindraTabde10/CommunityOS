# Feature: Notification System

**Status:** Ready for Implementation  
**Estimated Time:** 3-4 days  
**Priority:** High (Phase 2, Feature #4)

---

## 📋 Objective

Implement a comprehensive email notification system using Resend API:
- Send transactional emails for key issue events
- User notification preferences
- Email templates for different event types
- Background email sending (async)
- Email history tracking
- Weekly digest emails (optional)

---

## 🎯 Affected Components

### Backend Files to Create
- [ ] `backend/app/services/email_service.py` - Resend integration
- [ ] `backend/app/models/notification.py` - Notification preferences & history
- [ ] `backend/app/schemas/notification.py` - Notification schemas
- [ ] `backend/app/api/v1/endpoints/notifications.py` - Notification settings endpoints
- [ ] `backend/app/templates/` - Email HTML templates folder
- [ ] `backend/app/templates/issue_created.html` - Issue creation template
- [ ] `backend/app/templates/issue_assigned.html` - Issue assignment template
- [ ] `backend/app/templates/issue_status_changed.html` - Status change template
- [ ] `backend/app/templates/issue_resolved.html` - Issue resolved template
- [ ] `backend/app/templates/comment_added.html` - New comment template
- [ ] `backend/alembic/versions/[timestamp]_add_notifications.py` - Migration

### Backend Files to Modify
- [ ] `backend/requirements.txt` - Add `resend` package
- [ ] `backend/app/core/config.py` - Add Resend API configuration
- [ ] `backend/.env.template` - Add Resend API key template
- [ ] `backend/app/models/__init__.py` - Import notification models
- [ ] `backend/app/models/user.py` - Add notification preferences
- [ ] `backend/app/api/v1/api.py` - Include notifications router
- [ ] `backend/app/api/v1/endpoints/issues.py` - Trigger notifications
- [ ] `backend/app/api/v1/endpoints/comments.py` - Trigger comment notifications

### Documentation to Update
- [ ] `backend/API_README.md` - Add notification endpoints
- [ ] `REFERENCE.md` - Add notification models & config
- [ ] `backend/API_IMPLEMENTATION_PLAN.md` - Mark as completed
- [ ] `backend/LOCAL_DB_SETUP.md` - Document Resend setup

---

## 🏗️ Implementation Steps

### 1. Install Resend Package (5 min)
```bash
pip install resend
pip freeze > requirements.txt
```

### 2. Configuration (15 min)

#### Update config.py
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Email Configuration
    RESEND_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "Riverdale Connect <noreply@yourdomain.com>"
    ADMIN_EMAIL: Optional[str] = None
    ENABLE_NOTIFICATIONS: bool = True  # Feature flag
```

#### Update .env.template
```bash
# Email Configuration (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxx
FROM_EMAIL=Riverdale Connect <noreply@yourdomain.com>
ADMIN_EMAIL=admin@yourdomain.com
ENABLE_NOTIFICATIONS=true
```

### 3. Database Models (45 min)

#### Notification Preferences (Add to User model)
```python
# backend/app/models/user.py
class User(Base):
    # ... existing fields ...
    
    # Notification Preferences
    notify_on_issue_created = Column(Boolean, default=True)
    notify_on_issue_assigned = Column(Boolean, default=True)
    notify_on_issue_status_changed = Column(Boolean, default=True)
    notify_on_issue_resolved = Column(Boolean, default=True)
    notify_on_comment_added = Column(Boolean, default=True)
    notify_weekly_digest = Column(Boolean, default=False)
```

#### Email History Model
```python
# backend/app/models/notification.py
class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    to_email = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    template_name = Column(String(100))
    status = Column(String(50), default="pending")  # pending, sent, failed
    error_message = Column(Text)
    resend_id = Column(String(255))  # Resend message ID
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Relationships
    issue = relationship("Issue")
    user = relationship("User")
```

### 4. Pydantic Schemas (30 min)

```python
# backend/app/schemas/notification.py
class NotificationPreferences(BaseModel):
    notify_on_issue_created: bool = True
    notify_on_issue_assigned: bool = True
    notify_on_issue_status_changed: bool = True
    notify_on_issue_resolved: bool = True
    notify_on_comment_added: bool = True
    notify_weekly_digest: bool = False

class NotificationPreferencesUpdate(BaseModel):
    notify_on_issue_created: Optional[bool] = None
    notify_on_issue_assigned: Optional[bool] = None
    notify_on_issue_status_changed: Optional[bool] = None
    notify_on_issue_resolved: Optional[bool] = None
    notify_on_comment_added: Optional[bool] = None
    notify_weekly_digest: Optional[bool] = None

class EmailLogResponse(BaseModel):
    id: int
    to_email: str
    subject: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

### 5. Email Service (90 min)

```python
# backend/app/services/email_service.py
import resend
from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.models.notification import EmailLog

class EmailService:
    def __init__(self):
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY
        
        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        template_name: Optional[str] = None,
        issue_id: Optional[int] = None,
        user_id: Optional[int] = None,
        db = None
    ) -> bool:
        """Send email via Resend API and log to database"""
        
        if not settings.ENABLE_NOTIFICATIONS:
            return False
        
        if not settings.RESEND_API_KEY:
            print("Warning: RESEND_API_KEY not configured")
            return False
        
        try:
            # Send via Resend
            response = resend.Emails.send({
                "from": settings.FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": html_content
            })
            
            # Log to database
            if db:
                email_log = EmailLog(
                    to_email=to_email,
                    from_email=settings.FROM_EMAIL,
                    subject=subject,
                    template_name=template_name,
                    status="sent",
                    resend_id=response.get("id"),
                    issue_id=issue_id,
                    user_id=user_id,
                    sent_at=datetime.utcnow()
                )
                db.add(email_log)
                db.commit()
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            
            # Log failure
            if db:
                email_log = EmailLog(
                    to_email=to_email,
                    from_email=settings.FROM_EMAIL,
                    subject=subject,
                    template_name=template_name,
                    status="failed",
                    error_message=str(e),
                    issue_id=issue_id,
                    user_id=user_id
                )
                db.add(email_log)
                db.commit()
            
            return False
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    # Helper methods for common emails
    
    def send_issue_created(self, db, issue, user):
        """Send email when issue is created"""
        if not user.notify_on_issue_created:
            return
        
        html = self.render_template("issue_created.html", {
            "user_name": user.name,
            "issue_number": issue.issue_number,
            "title": issue.title,
            "category": issue.category,
            "priority": issue.priority,
            "description": issue.description
        })
        
        self.send_email(
            to_email=user.email,
            subject=f"Issue #{issue.issue_number} Created: {issue.title}",
            html_content=html,
            template_name="issue_created",
            issue_id=issue.id,
            user_id=user.id,
            db=db
        )
    
    def send_issue_assigned(self, db, issue, assignee):
        """Send email when issue is assigned"""
        if not assignee.notify_on_issue_assigned:
            return
        
        html = self.render_template("issue_assigned.html", {
            "user_name": assignee.name,
            "issue_number": issue.issue_number,
            "title": issue.title,
            "category": issue.category,
            "priority": issue.priority,
            "description": issue.description
        })
        
        self.send_email(
            to_email=assignee.email,
            subject=f"Issue #{issue.issue_number} Assigned to You: {issue.title}",
            html_content=html,
            template_name="issue_assigned",
            issue_id=issue.id,
            user_id=assignee.id,
            db=db
        )
    
    def send_issue_status_changed(self, db, issue, user, old_status, new_status):
        """Send email when issue status changes"""
        if not user.notify_on_issue_status_changed:
            return
        
        html = self.render_template("issue_status_changed.html", {
            "user_name": user.name,
            "issue_number": issue.issue_number,
            "title": issue.title,
            "old_status": old_status,
            "new_status": new_status
        })
        
        self.send_email(
            to_email=user.email,
            subject=f"Issue #{issue.issue_number} Status Changed: {old_status} → {new_status}",
            html_content=html,
            template_name="issue_status_changed",
            issue_id=issue.id,
            user_id=user.id,
            db=db
        )
    
    def send_issue_resolved(self, db, issue, user):
        """Send email when issue is resolved"""
        if not user.notify_on_issue_resolved:
            return
        
        html = self.render_template("issue_resolved.html", {
            "user_name": user.name,
            "issue_number": issue.issue_number,
            "title": issue.title,
            "resolution_notes": issue.resolution_notes or "No notes provided"
        })
        
        self.send_email(
            to_email=user.email,
            subject=f"Issue #{issue.issue_number} Resolved: {issue.title}",
            html_content=html,
            template_name="issue_resolved",
            issue_id=issue.id,
            user_id=user.id,
            db=db
        )
    
    def send_comment_added(self, db, issue, comment, commenter, recipient):
        """Send email when someone comments on user's issue"""
        if not recipient.notify_on_comment_added:
            return
        
        # Don't notify user about their own comments
        if commenter.id == recipient.id:
            return
        
        html = self.render_template("comment_added.html", {
            "user_name": recipient.name,
            "commenter_name": commenter.name,
            "issue_number": issue.issue_number,
            "title": issue.title,
            "comment": comment.content
        })
        
        self.send_email(
            to_email=recipient.email,
            subject=f"New Comment on Issue #{issue.issue_number}: {issue.title}",
            html_content=html,
            template_name="comment_added",
            issue_id=issue.id,
            user_id=recipient.id,
            db=db
        )

# Singleton instance
email_service = EmailService()
```

### 6. Email Templates (60 min)

Create HTML templates using Jinja2. Each template should be responsive and professional.

#### Base Template Structure
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2196F3; color: white; padding: 20px; text-align: center; }
        .content { background: #f9f9f9; padding: 20px; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        .button { background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Riverdale Connect</h1>
        </div>
        <div class="content">
            <!-- Template-specific content -->
        </div>
        <div class="footer">
            <p>This is an automated message from Riverdale Connect.</p>
            <p>To manage your notification preferences, log in to your account.</p>
        </div>
    </div>
</body>
</html>
```

Create 5 templates:
- `issue_created.html`
- `issue_assigned.html`
- `issue_status_changed.html`
- `issue_resolved.html`
- `comment_added.html`

### 7. API Endpoints (45 min)

```python
# backend/app/api/v1/endpoints/notifications.py

# GET /api/v1/users/me/notification-preferences
# Get current user's notification preferences

# PUT /api/v1/users/me/notification-preferences
# Update notification preferences

# GET /api/v1/users/me/email-history
# Get email history for current user (pagination)
```

### 8. Integration with Existing Endpoints (60 min)

Modify existing issue endpoints to trigger notifications:

#### In `issues.py` - Create Issue
```python
# After creating issue
email_service.send_issue_created(db, issue, current_user)
```

#### In `issues.py` - Update Issue
```python
# When status changes
if old_status != new_status:
    if new_status == "resolved":
        email_service.send_issue_resolved(db, issue, reporter)
    else:
        email_service.send_issue_status_changed(db, issue, reporter, old_status, new_status)

# When assigned_to changes
if old_assigned_to != new_assigned_to and new_assigned_to:
    assignee = db.query(User).filter(User.id == new_assigned_to).first()
    email_service.send_issue_assigned(db, issue, assignee)
```

#### In `comments.py` - Create Comment
```python
# After creating comment
reporter = db.query(User).filter(User.id == issue.reported_by).first()
email_service.send_comment_added(db, issue, comment, current_user, reporter)

# Also notify assignee if different from reporter
if issue.assigned_to and issue.assigned_to != reporter.id:
    assignee = db.query(User).filter(User.id == issue.assigned_to).first()
    email_service.send_comment_added(db, issue, comment, current_user, assignee)
```

### 9. Database Migration (15 min)
```bash
alembic revision --autogenerate -m "add notification preferences and email logs"
alembic upgrade head
```

---

## 🧪 Testing Plan

### Manual Testing
- [ ] Set up Resend API account (free tier: 100 emails/day)
- [ ] Add RESEND_API_KEY to .env
- [ ] Create issue → Check email received
- [ ] Assign issue → Check assignee receives email
- [ ] Change issue status → Check email received
- [ ] Resolve issue → Check email received
- [ ] Add comment → Check issue reporter receives email
- [ ] Update notification preferences
- [ ] Disable notifications → Verify no emails sent
- [ ] Check email history endpoint

### Test Cases
```python
# backend/tests/test_notifications.py
- test_get_notification_preferences
- test_update_notification_preferences
- test_email_sent_on_issue_created (mock Resend)
- test_email_sent_on_issue_assigned
- test_email_sent_on_status_change
- test_no_email_when_notifications_disabled
- test_get_email_history
```

### Edge Cases
- [ ] Resend API key not configured
- [ ] Invalid email address
- [ ] Resend API failure (handle gracefully)
- [ ] User has notifications disabled
- [ ] Template rendering error

---

## 📚 Documentation Updates

### backend/API_README.md
Add Notification System section

### backend/LOCAL_DB_SETUP.md
Add Resend setup instructions

### REFERENCE.md
Add notification models and configuration

---

## 🔄 Dependencies

### New Packages
- `resend==0.8.0` - Email API client

### New Environment Variables
- `RESEND_API_KEY` - API key from resend.com
- `FROM_EMAIL` - Sender email address
- `ADMIN_EMAIL` - Admin contact email
- `ENABLE_NOTIFICATIONS` - Feature flag (true/false)

---

## 🚨 Rollback Plan

1. Set `ENABLE_NOTIFICATIONS=false` in .env
2. Revert migration: `alembic downgrade -1`
3. Remove email service integrations from endpoints
4. Remove resend from requirements.txt
5. Restart backend

---

## 📋 Checklist

- [ ] Install resend package
- [ ] Update config.py with email settings
- [ ] Update .env.template
- [ ] Add notification fields to User model
- [ ] Create EmailLog model
- [ ] Create notification schemas
- [ ] Implement EmailService class
- [ ] Create 5 email HTML templates
- [ ] Create notifications endpoints
- [ ] Integrate notifications into issues endpoints
- [ ] Integrate notifications into comments endpoints
- [ ] Generate and apply migration
- [ ] Set up Resend account (free tier)
- [ ] Test all email triggers manually
- [ ] Write automated tests (with mocks)
- [ ] Update documentation
- [ ] Update API_IMPLEMENTATION_PLAN.md

---

## 🎯 Success Criteria

- ✅ Emails sent for all key events (create, assign, status change, resolved, comment)
- ✅ Users can manage notification preferences
- ✅ Email history is logged in database
- ✅ Templates are professional and responsive
- ✅ Graceful fallback when Resend not configured
- ✅ No blocking of main API operations (emails are fire-and-forget)
- ✅ All tests pass
- ✅ Documentation updated
