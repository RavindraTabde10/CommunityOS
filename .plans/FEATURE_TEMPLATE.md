# Feature Plan: [FEATURE NAME]

<!--
HOW TO USE THIS TEMPLATE
────────────────────────
1. Copy this file → .plans/[feature-name].md
2. Fill in EVERY section (leave nothing as placeholder).
3. Paste the filled plan into Copilot chat with:
   "Read AGENTS.md, then implement everything in .plans/[feature-name].md"
4. The agent will execute phases in order, verify at each step, and update all docs.
-->

**Feature:** [Short name]
**Date:** [YYYY-MM-DD]
**Priority:** High / Medium / Low
**Estimated Complexity:** Small (< 1 day) / Medium (1–3 days) / Large (3+ days)
**Status:** 📋 Planning

---

## 1. Objective

> One paragraph describing what this feature does, why it's needed, and what a user can do after it's implemented.

**User Stories:**
- As a [role], I can [action] so that [benefit].
- As a [role], I can [action] so that [benefit].

**Out of Scope (for this plan):**
- [what will NOT be built]

---

## 2. Backward Compatibility Gate ⚠️

> The agent MUST verify all items below before writing any code.
> If any item is already covered, note it here and skip that step.

- [ ] Does a backend endpoint for this already exist? (`grep -r "[keyword]" backend/app/api/`)
- [ ] Does a service for this already exist? (`grep -r "[keyword]" backend/app/services/`)
- [ ] Does a frontend page/route for this already exist? (`grep -r "[route]" frontend/src/`)
- [ ] Does a model for this already exist? (`grep -r "[ModelName]" backend/app/models/`)
- [ ] Does an Alembic migration for this schema change already exist?
- [ ] Will any existing endpoint path change? (must be NO — add new, never rename)
- [ ] Will any existing Pydantic field be removed? (must be NO — only add Optional fields)
- [ ] Will any existing Redux action be removed? (must be NO — only add new ones)

---

## 3. Backend Changes

### 3a. New Database Model(s)

> File: `backend/app/models/[model_name].py`
> If adding to an existing model, specify the file and fields to ADD (never remove).

```python
# New model definition here
# Include all columns, relationships, and __tablename__
```

**Relationships to add to existing models (if any):**
- In `backend/app/models/[existing_model].py`: add `[field_name] = relationship(...)`

---

### 3b. Alembic Migration

> A NEW migration file must be created. Never edit existing ones.

**Migration description string:** `"[short description of schema change]"`

**Tables created:** [list]
**Columns added:** [model.field — type]
**Columns removed:** NONE (removing breaks existing data)

---

### 3c. Pydantic Schemas

> File: `backend/app/schemas/[schema_name].py`

**Schemas to create:**

| Schema class | Purpose | Key fields |
|-------------|---------|-----------|
| `[Name]Create` | POST request body | field1, field2 |
| `[Name]Update` | PUT/PATCH request body | field1 (Optional) |
| `[Name]Response` | API response | all fields + id, timestamps |
| `[Name]ListResponse` | Paginated list | items: List[Response], total, skip, limit |

**Rule:** New fields added to existing response schemas must be `Optional` with a default.

---

### 3d. Service Layer

> File: `backend/app/services/[name]_service.py`

**Functions to implement:**

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `create_[name]` | db, data, user_id | [Name] | Create new record |
| `get_[name]` | db, id | [Name] \| None | Get by ID |
| `list_[names]` | db, skip, limit, filters | List[[Name]] | Paginated list |
| `update_[name]` | db, id, data, user_id | [Name] | Update record |
| `delete_[name]` | db, id, user_id | bool | Soft/hard delete |

---

### 3e. API Endpoints

> File: `backend/app/api/v1/endpoints/[name].py`
> Register in: `backend/app/api/v1/api.py`

**New router prefix:** `/api/v1/[resource]/`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/` | ✅ | any | Create |
| GET | `/` | ✅ | any | List (paginated) |
| GET | `/{id}` | ✅ | any | Get by ID |
| PUT | `/{id}` | ✅ | owner/admin | Update |
| DELETE | `/{id}` | ✅ | admin | Delete |

**Register router in `api.py`:**
```python
from app.api.v1.endpoints.[name] import router as [name]_router
api_router.include_router([name]_router, prefix="/[resource]", tags=["[Resource]"])
```

---

## 4. Frontend Changes

### 4a. API Service

> File: `frontend/src/api/[name]Service.js`
> Import in pages that need it.

```javascript
// Functions to implement:
// export const create[Name] = (data) => client.post('/[resource]/', data)
// export const get[Names] = (params) => client.get('/[resource]/', { params })
// export const get[Name] = (id) => client.get(`/[resource]/${id}`)
// export const update[Name] = (id, data) => client.put(`/[resource]/${id}`, data)
// export const delete[Name] = (id) => client.delete(`/[resource]/${id}`)
```

---

### 4b. New Pages

> Base path: `frontend/src/pages/`

| File | Route | Purpose |
|------|-------|---------|
| `[Name]List.jsx` | `/[resource]` | List view with filters |
| `[Name]Detail.jsx` | `/[resource]/:id` | Detail / read view |
| `Create[Name].jsx` | `/[resource]/create` | Create form |
| `Edit[Name].jsx` | `/[resource]/edit/:id` | Edit form |

**UI Pattern to follow:** Look at `frontend/src/pages/issues/` as the reference implementation (list, detail, create, edit pattern).

---

### 4c. New Components (if needed)

> Base path: `frontend/src/components/`

| Component | File | Used by |
|-----------|------|---------|
| [ComponentName] | `[folder]/[File].jsx` | [which pages] |

---

### 4d. Route Registration

> File: `frontend/src/App.jsx`
> Add inside the `<Routes>` block, within `<ProtectedRoute>`.

```jsx
// Routes to add:
<Route path="/[resource]" element={<[Name]List />} />
<Route path="/[resource]/:id" element={<[Name]Detail />} />
<Route path="/[resource]/create" element={<Create[Name] />} />
<Route path="/[resource]/edit/:id" element={<Edit[Name] />} />
```

---

### 4e. Sidebar Navigation

> File: `frontend/src/components/layout/Sidebar.jsx`
> Add a new nav item. Do NOT remove or reorder existing items.

```jsx
// Nav item to add:
{ label: '[Feature Name]', path: '/[resource]', icon: <[Icon] />, roles: ['resident', 'admin'] }
```

---

### 4f. Dashboard Widget (optional)

> File: `frontend/src/components/dashboard/`
> Only if the feature needs a dashboard summary card.

- [ ] New widget needed? Yes / No
- [ ] Widget name: `[Name]Widget.jsx`
- [ ] Add to `frontend/src/pages/Dashboard.jsx`

---

## 5. Agent Execution Order

> The agent MUST follow this order exactly. Do not jump ahead.

```
Phase 1 — Backend Foundation
  1. Create model file: backend/app/models/[name].py
  2. Add import to backend/app/models/__init__.py
  3. Add relationship to existing model (if any)
  4. Create migration: alembic revision --autogenerate -m "[description]"
  5. Apply migration: alembic upgrade head
  6. ✅ VERIFY: backend starts without error (uvicorn app.main:app --reload)

Phase 2 — Backend API
  7. Create schema file: backend/app/schemas/[name].py
  8. Create service file: backend/app/services/[name]_service.py
  9. Create endpoint file: backend/app/api/v1/endpoints/[name].py
  10. Register router in backend/app/api/v1/api.py
  11. ✅ VERIFY: new endpoints appear in Swagger UI (http://127.0.0.1:8000/api/docs)
  12. ✅ VERIFY: CRUD operations work via Swagger UI

Phase 3 — Frontend
  13. Create API service: frontend/src/api/[name]Service.js
  14. Create page components (List → Detail → Create → Edit)
  15. Register routes in frontend/src/App.jsx
  16. Add sidebar nav item in frontend/src/components/layout/Sidebar.jsx
  17. Add dashboard widget (if needed)
  18. ✅ VERIFY: frontend compiles without error (npm run dev)
  19. ✅ VERIFY: new pages load and API calls succeed

Phase 4 — Documentation
  20. Update REFERENCE.md → add new endpoints to "Additional Live Endpoints" table
  21. Update AGENTS.md → add new endpoint row to "Backend — Live Endpoints" table
  22. Update AGENTS.md → add new page rows to "Frontend — Live Pages" table
  23. Update AGENTS.md → add to "Backend Services" and "Frontend Features" lists
  24. Update IMPLEMENTATION_CHECKLIST.md → mark feature as complete
  25. Update INDEX.md → add new files to backend/frontend trees if significant
  26. ✅ VERIFY: no stale "Planned" or "To be implemented" text in updated docs
```

---

## 6. Verification Checklist

> Run these after Phase 4 is complete.

**Backend:**
- [ ] `uvicorn app.main:app --reload` starts without error
- [ ] New endpoints visible in Swagger UI
- [ ] CRUD: create, read, update, delete all work
- [ ] Auth enforced (test with/without token)
- [ ] Role restrictions enforced (test with resident vs admin)
- [ ] Existing endpoints still work (spot-check 3 unrelated endpoints)

**Frontend:**
- [ ] `npm run dev` compiles without error or warnings
- [ ] New pages load without console errors
- [ ] List page shows data from API
- [ ] Create form submits and redirects correctly
- [ ] Edit form pre-fills and saves correctly
- [ ] Sidebar nav item visible and routes correctly
- [ ] Mobile responsive (resize browser to 375px)
- [ ] Existing pages still work (Dashboard, Issues, Profile)

**Database:**
- [ ] Migration applied cleanly (`alembic upgrade head` reports no errors)
- [ ] `alembic downgrade -1` then `alembic upgrade head` succeeds (rollback test)

---

## 7. Documentation Updates

> The agent updates ALL of these at Phase 4. Mark each when done.

| File | What to update |
|------|---------------|
| `REFERENCE.md` | Add new endpoint module to "Additional Live Endpoints" table |
| `AGENTS.md` | Add row to "Backend — Live Endpoints" table |
| `AGENTS.md` | Add row to "Frontend — Live Pages" table |
| `AGENTS.md` | Add bullet to "Backend Services" list |
| `AGENTS.md` | Add bullet to "Frontend Features" list |
| `IMPLEMENTATION_CHECKLIST.md` | Mark feature complete with date |
| `INDEX.md` | Add new endpoint file, model, service to backend trees (if significant) |
| `backend/API_README.md` | Add endpoint documentation section |

---

## 8. New Dependencies

> List any NEW packages. If none, write "None".

**Backend (`requirements.txt`):**
- None

**Frontend (`package.json`):**
- None

**New environment variables (add to `backend/.env.template`):**
- None

---

## 9. Rollback Plan

If something breaks after implementation:

1. **Database:** `alembic downgrade -1` (reverts last migration)
2. **Backend code:** Revert the new endpoint/service/model files; remove router registration from `api.py`
3. **Frontend code:** Remove new pages and route entries from `App.jsx`; remove sidebar item
4. **No existing files were modified** (only new files added) — so existing functionality is unaffected
