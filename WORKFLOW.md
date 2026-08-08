# Development Workflow

This document defines the mandatory workflow for all code changes, feature implementations, and bug fixes in **CommunityOS.ai**.

> ⚠️ **This is a fully implemented, production-ready application.** Every workflow step must protect the 40+ live backend endpoints and 20+ live frontend pages. See [AGENTS.md](./AGENTS.md#preserving-existing-functionality) for the complete list of what must not break.

---

## 🎯 Core Principles

1. **Specification-Driven Development** - Always refer to specs before coding
2. **Plan Before Code** - Create detailed plans for all non-trivial changes
3. **Test Locally First** - Never skip local testing
4. **Document Everything** - Keep documentation in sync with code
5. **Single Responsibility** - One feature/fix per PR
6. **Preserve Existing Functionality** - Never break live endpoints, routes, or migrations

---

## 📋 Workflow Steps

### Step 1: Understand the Request

**Before writing any code:**

1. **Read the user request carefully**
   - What is the exact requirement?
   - Are there any constraints or preferences?
   - What is the expected outcome?

2. **Check existing specifications**
   - Review [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
   - Check [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)
   - Read [backend/API_IMPLEMENTATION_PLAN.md](./backend/API_IMPLEMENTATION_PLAN.md)
   - Consult [REFERENCE.md](./REFERENCE.md)

3. **Check what is already implemented** (critical step)
   - Read [AGENTS.md — Preserving Existing Functionality](./AGENTS.md#preserving-existing-functionality)
   - Does the endpoint already exist? (`grep` the `endpoints/` folder)
   - Does the service already exist? (`grep` the `services/` folder)
   - Does the frontend page/route already exist?
   - Does a migration for this schema change already exist?

4. **Identify affected components**
   - Which files need to be modified?
   - Are database changes required? (Needs a **new** migration, never edit existing)
   - Will this affect existing API signatures or frontend routes?

---

### Step 2: Create Implementation Plan

**MANDATORY for all changes except:**
- Simple typo fixes
- Documentation-only updates
- Configuration tweaks

**Use the canonical template:** Copy `.plans/FEATURE_TEMPLATE.md` → `.plans/[feature-name].md` and fill it in completely before asking an agent to implement.

The template covers every section an agent needs to execute implementation end-to-end without asking follow-up questions:

| Section | Purpose |
|---------|---------|
| Objective & User Stories | Defines scope |
| Backward Compatibility Gate | Prevents breaking live features |
| Backend Changes | Models, schemas, services, endpoints, migration |
| Frontend Changes | Pages, components, routes, API services |
| Agent Execution Order | Explicit step-by-step for the agent |
| Verification Checklist | What to run/test after each phase |
| Documentation Updates | Exact list of .md files to update |

**Save plans to:** `.plans/[feature-name].md`

---

### Step 3: Get Approval (If Needed)

**Requires user approval:**
- Breaking changes to existing APIs
- Database schema modifications
- New external dependencies
- Major architectural changes
- Production environment changes

**Present the plan to the user:**
- Explain the approach
- Highlight trade-offs
- Mention any risks
- Provide alternatives if applicable

---

### Step 4: Implementation

**Code Changes:**

1. **Follow existing patterns**
   ```python
   # ✅ Good - Follows existing pattern
   from app.models.user import User
   from app.schemas.user import UserResponse
   
   # ❌ Bad - Inconsistent with codebase
   from models import User  # Wrong import style
   ```

2. **Use proper error handling**
   ```python
   # ✅ Good
   try:
       user = db.query(User).filter(User.id == user_id).first()
       if not user:
           raise HTTPException(status_code=404, detail="User not found")
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Error fetching user: {str(e)}")
       raise HTTPException(status_code=500, detail="Internal server error")
   
   # ❌ Bad
   user = db.query(User).filter(User.id == user_id).first()  # No error handling
   ```

3. **Add proper documentation**
   ```python
   # ✅ Good
   def create_issue(issue: IssueCreate, user: User, db: Session) -> Issue:
       """
       Create a new issue in the system.
       
       Args:
           issue: Issue creation data
           user: Current authenticated user
           db: Database session
           
       Returns:
           Created issue with generated ID
           
       Raises:
           HTTPException: If validation fails
       """
       pass
   ```

4. **Follow naming conventions**
   - Functions: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private methods: `_leading_underscore`

**Database Changes:**

1. **Always use migrations**
   ```bash
   # Create migration
   alembic revision --autogenerate -m "Add contractor table"
   
   # Review generated migration
   # Edit if necessary
   
   # Test migration
   alembic upgrade head
   
   # Test rollback
   alembic downgrade -1
   alembic upgrade head
   ```

2. **Never modify database directly**
   - ❌ Don't run SQL directly on database
   - ✅ Always use Alembic migrations

3. **Test with sample data**
   ```python
   # Create test script if needed
   python scripts/test_migration.py
   ```

**Configuration Changes:**

1. **Update `.env.template`** if adding new variables
2. **Document in README** if setup changes
3. **Never commit `.env`** file

---

### Step 5: Testing

**Backend Testing Checklist:**

```markdown
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Check Swagger UI: http://127.0.0.1:8000/api/docs
- [ ] Test new endpoints manually
- [ ] Test with invalid inputs
- [ ] Test authentication flow
- [ ] Test role-based permissions
- [ ] Check database state
- [ ] Verify no console errors
```

**Frontend Testing Checklist (when applicable):**

```markdown
- [ ] Start dev server: `npm run dev`
- [ ] Test in Chrome
- [ ] Test in Firefox/Safari
- [ ] Test responsive design
- [ ] Test form validation
- [ ] Test error states
- [ ] Test loading states
```

**Integration Testing:**

```markdown
- [ ] Backend and frontend work together
- [ ] Data flows correctly between components
- [ ] Error handling works end-to-end
- [ ] Authentication/authorization enforced
```

**Test Database Connection:**
```bash
python scripts/test_local_db.py
```

**Common Test Scenarios:**

1. **Authentication Flow**
   - Register new user
   - Login with valid credentials
   - Access protected endpoint
   - Test with invalid token
   - Test token expiration

2. **CRUD Operations**
   - Create resource
   - Read resource
   - Update resource
   - Delete resource
   - Test with missing fields
   - Test with invalid data

3. **Authorization**
   - Test as regular user
   - Test as admin
   - Test cross-user access
   - Test without authentication

---

### Step 6: Documentation Updates

**Always Update When:**

| Change Type | Update These Files |
|-------------|-------------------|
| New API endpoint | `REFERENCE.md`, `backend/API_README.md` |
| Schema change | `REFERENCE.md`, database schema docs |
| New feature | `IMPLEMENTATION_CHECKLIST.md`, `DEVELOPMENT_PLAN.md` |
| Configuration | `.env.template`, README files |
| Deployment process | `QUICKSTART.md`, deployment guides |
| Breaking change | `CHANGELOG.md`, release notes |

**Documentation Standards:**

1. **API Endpoints**
   ```markdown
   ### Endpoint Name
   
   **URL:** `GET /api/v1/resource/{id}`
   
   **Description:** Brief description of what it does
   
   **Authentication:** Required / Not Required
   
   **Request:**
   ```json
   {
     "field": "value"
   }
   ```
   
   **Response:**
   ```json
   {
     "id": "123",
     "field": "value"
   }
   ```
   
   **Errors:**
   - 404: Resource not found
   - 403: Unauthorized
   ```

2. **Code Comments**
   - Explain **why**, not **what**
   - Document complex business logic
   - Reference specification sections
   - Note TODOs with context

3. **README Updates**
   - Add new setup steps
   - Update command examples
   - Include troubleshooting tips
   - Update dependency list

---

### Step 7: Code Review (Self-Review)

**Review Checklist:**

```markdown
Code Quality:
- [ ] Follows existing code patterns
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Meaningful variable names
- [ ] Functions are small and focused

Security:
- [ ] No hardcoded credentials
- [ ] Proper input validation
- [ ] SQL injection prevented (using ORM)
- [ ] XSS prevented (using proper escaping)
- [ ] Authentication/authorization checked

Performance:
- [ ] No N+1 queries
- [ ] Proper database indexes
- [ ] No unnecessary computations
- [ ] Efficient algorithms used

Documentation:
- [ ] All public functions documented
- [ ] Complex logic explained
- [ ] TODOs have context
- [ ] API docs updated

Testing:
- [ ] Manually tested locally
- [ ] Edge cases considered
- [ ] Error cases tested
- [ ] Works with existing features
```

---

### Step 8: Completion

**Mark as Complete:**

1. **Update Implementation Checklist**
   ```markdown
   # In IMPLEMENTATION_CHECKLIST.md
   - [x] Feature: User profile update endpoint
     - Completed: 2026-07-23
     - Files: app/api/v1/endpoints/auth.py, app/schemas/user.py
     - Tested: Yes
   ```

2. **Update Development Plan**
   - Move feature from "To Do" to "Done"
   - Update completion dates
   - Note any deviations from plan

3. **Create Release Note (if significant)**
   ```markdown
   # .plans/release_notes/v1.1.0.md
   
   ## Features
   - Added user profile update endpoint
   
   ## Changes
   - Enhanced user schema with new fields
   
   ## Migration Required
   - Run: alembic upgrade head
   ```

---

## 🚫 Common Mistakes to Avoid

### Don't Do This

1. **❌ Skip planning for complex changes**
   - Always create a plan first
   - Review existing code
   - Consider implications

2. **❌ Modify production directly**
   - Test locally first
   - Use proper deployment process
   - Never SSH into prod to "fix" code

3. **❌ Commit without testing**
   - Always test locally
   - Verify functionality works
   - Check for console errors

4. **❌ Leave outdated documentation**
   - Update docs immediately
   - Don't create technical debt
   - Keep REFERENCE.md current

5. **❌ Mix multiple features in one change**
   - One feature per commit/PR
   - Easier to review
   - Easier to rollback

6. **❌ Ignore error handling**
   - Always handle exceptions
   - Provide meaningful errors
   - Log for debugging

7. **❌ Hardcode values**
   - Use environment variables
   - Use configuration files
   - Make it configurable

8. **❌ Skip database migrations**
   - Use Alembic for all schema changes
   - Never modify DB directly
   - Never edit existing migration files — create new ones
   - Test migrations thoroughly

9. **❌ Rename or remove existing endpoints/routes**
   - The frontend calls backend paths by exact string — changing a path breaks the frontend silently
   - Add new routes; keep old ones
   - If a response field must be removed, mark it deprecated first

10. **❌ Change Redux slice structure without cascade**
    - `authSlice.js` is consumed by all protected pages
    - Any structural change must be reflected in every component that reads from it

---

## 🔄 Pull Request Workflow (Future)

**When PR system is active:**

### Before Creating PR

```markdown
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No console errors
- [ ] Migration tested (if applicable)
- [ ] Code self-reviewed
- [ ] Follows coding standards
```

### PR Description Template

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Tested locally
- [ ] Added unit tests
- [ ] Updated integration tests

## Documentation
- [ ] Updated README
- [ ] Updated API docs
- [ ] Added code comments

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed
- [ ] No new warnings
- [ ] Tests pass
- [ ] Documentation updated
```

### PR Review Guidelines

**As Reviewer:**
- Check against coding standards
- Verify tests cover main paths
- Ensure documentation updated
- Look for security issues
- Suggest improvements

**As Author:**
- Address all comments
- Update PR based on feedback
- Re-test after changes
- Update documentation if needed

---

## 🔧 Environment-Specific Workflows

### Local Development

```bash
# Backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

**Testing:**
- Use SQLite database
- Use localhost URLs
- Mock external services (S3, email)

### Staging (Future)

```bash
# Deploy to staging
git push staging main

# Run migrations
ssh staging "cd /app && alembic upgrade head"

# Monitor logs
ssh staging "tail -f /var/log/app.log"
```

**Testing:**
- Use staging database
- Use staging URLs
- Real external services (with test keys)

### Production (Future)

```bash
# Deploy to production
git push production main

# Health check
curl https://api.production.com/health

# Monitor
# Use monitoring dashboard
```

**Rules:**
- Never test new features on prod
- Always deploy to staging first
- Have rollback plan ready
- Monitor after deployment

---

## 📊 Quality Standards

### Code Quality Metrics

- **Test Coverage:** > 80% (when tests implemented)
- **Response Time:** < 200ms for API endpoints
- **Error Rate:** < 1%
- **Documentation:** All public APIs documented
- **Code Review:** All changes reviewed

### Performance Targets

- **API Response Time:** < 200ms (p95)
- **Database Query Time:** < 50ms (average)
- **Page Load Time:** < 2 seconds
- **Bundle Size:** < 500KB (frontend)

---

## 🆘 Troubleshooting Workflow

### When Something Breaks

1. **Don't Panic**
   - Stay calm
   - Read error messages carefully
   - Check recent changes

2. **Gather Information**
   - Error logs
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

3. **Isolate the Problem**
   - Narrow down the component
   - Test individual parts
   - Check dependencies

4. **Find the Root Cause**
   - Review recent commits
   - Check configuration
   - Verify database state
   - Look for similar issues

5. **Fix and Test**
   - Implement fix
   - Test thoroughly
   - Verify no side effects
   - Document the issue

6. **Prevent Recurrence**
   - Add tests for the bug
   - Update error handling
   - Improve documentation
   - Share learnings

---

## 📝 Summary

**Remember:**
1. 📋 Always plan before coding
2. 🧪 Test everything locally
3. 📚 Keep documentation current
4. 🔍 Review your own code
5. ✅ Complete the checklist

**Quick Reference:**
- Planning: Create `.plans/[feature].md`
- Testing: Use Swagger UI + manual testing
- Documentation: Update `REFERENCE.md` and relevant READMEs
- Completion: Update `IMPLEMENTATION_CHECKLIST.md`

---

**Last Updated:** 2026-07-23  
**Version:** 1.0
