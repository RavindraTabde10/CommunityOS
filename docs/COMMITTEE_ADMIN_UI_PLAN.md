# Committee Member Admin UI - Implementation Plan

**Feature:** Admin UI for Committee Member Management (CRUD Operations)  
**Date:** 2026-07-29  
**Status:** Planning → Implementation

---

## 📋 Overview

Add a complete admin interface for managing committee members through the UI, removing the need to use Swagger API for CRUD operations.

### Current State:
- ✅ Backend API endpoints exist (POST, GET, PUT, DELETE)
- ✅ Frontend API service exists (`committeeService.js`)
- ✅ Committee members display on dashboard
- ❌ No admin UI for management

### Target State:
- ✅ Admin-only Committee Management page
- ✅ Create new committee members via form dialog
- ✅ Edit existing committee members
- ✅ Delete committee members with confirmation
- ✅ View all committee members in table/list
- ✅ Form validation and error handling

---

## 🎯 Requirements

### Functional Requirements:
1. **Access Control:** Only ADMIN users can access
2. **Create:** Form dialog to add new committee member
3. **Read:** List/table view of all committee members (active + inactive)
4. **Update:** Edit existing committee member details
5. **Delete:** Remove committee member with confirmation dialog
6. **Validation:** Form validation for all fields
7. **Feedback:** Success/error notifications for all operations

### UI Requirements:
1. Clean, professional Material-UI design
2. Responsive layout (mobile-friendly)
3. Clear action buttons (Add, Edit, Delete)
4. Role badges with emoji icons
5. Active/Inactive status indicators
6. Search/filter functionality (optional, Phase 2)

---

## 🏗️ Architecture

### New Components:

```
frontend/src/pages/admin/
  └── CommitteeManagement.jsx       # Main management page

frontend/src/components/admin/
  └── CommitteeMemberDialog.jsx     # Create/Edit dialog form
  └── CommitteeMemberTable.jsx      # Table view of members
  └── DeleteConfirmDialog.jsx       # Reusable delete confirmation
```

### Component Hierarchy:
```
CommitteeManagement (Page)
├── PageHeader (title, Add button)
├── CommitteeMemberTable
│   ├── TableRow (for each member)
│   │   ├── Member info display
│   │   ├── Edit button → Opens CommitteeMemberDialog
│   │   └── Delete button → Opens DeleteConfirmDialog
└── CommitteeMemberDialog (shared for Create & Edit)
    └── Form with validation
```

---

## 📝 Implementation Steps

### Step 1: Create Committee Member Dialog (Form)
**File:** `frontend/src/components/admin/CommitteeMemberDialog.jsx`

**Features:**
- Material-UI Dialog with form
- Mode: "create" or "edit"
- Fields:
  - User selection (dropdown of all users)
  - Role selection (dropdown: president, vice_president, secretary, treasurer, member)
  - Position name (text input)
  - Responsibilities (multiline text)
  - Contact email (email validation)
  - Contact phone (phone validation)
  - Display order (number)
  - Term start date (date picker)
  - Term end date (date picker)
  - Active status (checkbox)
- Form validation using Yup schema
- Submit handler calls `committeeService.createMember()` or `updateMember()`
- Success/error notifications using snackbar

**Dependencies:**
- React Hook Form or Formik
- Yup for validation
- Material-UI components: Dialog, TextField, Select, Button, etc.
- Date picker from Material-UI or react-datepicker

### Step 2: Create Committee Member Table
**File:** `frontend/src/components/admin/CommitteeMemberTable.jsx`

**Features:**
- Material-UI Table or DataGrid
- Columns:
  - Avatar (first letter of user name)
  - User Name
  - Role (with badge and emoji)
  - Position Name
  - Contact (email/phone)
  - Term (start - end dates)
  - Status (Active/Inactive chip)
  - Actions (Edit, Delete buttons)
- Empty state: "No committee members found"
- Loading state: Skeleton or spinner
- Action handlers:
  - `onEdit(member)` → Opens dialog in edit mode
  - `onDelete(member)` → Opens delete confirmation

**Styling:**
- Alternating row colors
- Hover effects
- Status chips with colors (Active: green, Inactive: gray)
- Role badges matching dashboard design

### Step 3: Create Delete Confirmation Dialog
**File:** `frontend/src/components/admin/DeleteConfirmDialog.jsx`

**Features:**
- Simple confirmation dialog
- Props: `open`, `onClose`, `onConfirm`, `memberName`
- Shows member name in message: "Are you sure you want to remove [Name] from the committee?"
- Two buttons: Cancel (secondary) and Delete (error color)
- Calls `committeeService.deleteMember(id)` on confirm

### Step 4: Create Committee Management Page
**File:** `frontend/src/pages/admin/CommitteeManagement.jsx`

**Features:**
- Page container with header
- "Add Committee Member" button (top right)
- CommitteeMemberTable component
- State management:
  - `members` - list of all committee members
  - `loading` - loading state
  - `dialogOpen` - dialog visibility
  - `dialogMode` - "create" or "edit"
  - `selectedMember` - member being edited
  - `deleteDialogOpen` - delete confirmation visibility
- API calls:
  - `loadMembers()` - GET /api/v1/committee (all members)
  - `handleCreate()` - Opens dialog in create mode
  - `handleEdit(member)` - Opens dialog in edit mode with data
  - `handleDelete(member)` - Opens delete confirmation
  - `handleSave(data)` - Creates or updates member
  - `handleConfirmDelete()` - Deletes member and reloads
- Error handling and notifications

### Step 5: Add Routing
**File:** `frontend/src/App.jsx` (or routes config)

**Changes:**
- Add route: `/admin/committee` → `<CommitteeManagement />`
- Protected route (admin only)

### Step 6: Update Navigation
**File:** `frontend/src/components/layout/Sidebar.jsx` or Navigation component

**Changes:**
- Add menu item: "Committee Management" (admin only)
- Icon: Groups or People icon
- Link to `/admin/committee`

---

## 🎨 UI Mockup

### Committee Management Page:

```
┌─────────────────────────────────────────────────────────────────┐
│  🏛️ Committee Management                    [+ Add Member]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Avatar │ Name    │ Role       │ Position  │ Term    │ Status││
│  ├─────────────────────────────────────────────────────────────┤│
│  │   J    │ John D  │ 👑 PRES   │ President │ 2026-27 │ ✓     ││
│  │        │         │            │           │         │ [✏️][🗑️]││
│  ├─────────────────────────────────────────────────────────────┤│
│  │   S    │ Sarah M │ 📝 SEC    │ Secretary │ 2026-27 │ ✓     ││
│  │        │         │            │           │         │ [✏️][🗑️]││
│  ├─────────────────────────────────────────────────────────────┤│
│  │   M    │ Mike T  │ 💰 TREAS  │ Treasurer │ 2026-27 │ ✓     ││
│  │        │         │            │           │         │ [✏️][🗑️]││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Add/Edit Dialog:

```
┌───────────────────────────────────────┐
│  Add Committee Member           [✕]   │
├───────────────────────────────────────┤
│                                       │
│  Select User: [Dropdown ▼]           │
│                                       │
│  Role: [President ▼]                  │
│                                       │
│  Position Name: [____________]        │
│                                       │
│  Responsibilities:                    │
│  [_____________________________]      │
│  [_____________________________]      │
│                                       │
│  Contact Email: [____________]        │
│                                       │
│  Contact Phone: [____________]        │
│                                       │
│  Display Order: [1]                   │
│                                       │
│  Term Start: [📅 2026-01-01]          │
│                                       │
│  Term End: [📅 2027-12-31]            │
│                                       │
│  ☐ Active                             │
│                                       │
│         [Cancel]  [Save Member]       │
└───────────────────────────────────────┘
```

---

## 📊 Data Flow

### Create Member Flow:
1. Admin clicks "Add Member" button
2. Dialog opens with empty form
3. Admin fills form and clicks "Save"
4. Validation runs (client-side)
5. If valid: `committeeService.createMember(data)`
6. Success: Close dialog, reload table, show success notification
7. Error: Show error message in dialog

### Edit Member Flow:
1. Admin clicks Edit button on table row
2. Dialog opens with pre-filled form data
3. Admin modifies fields and clicks "Save"
4. Validation runs
5. If valid: `committeeService.updateMember(id, data)`
6. Success: Close dialog, reload table, show success notification
7. Error: Show error message in dialog

### Delete Member Flow:
1. Admin clicks Delete button on table row
2. Confirmation dialog opens with member name
3. Admin clicks "Delete" button
4. `committeeService.deleteMember(id)`
5. Success: Close dialog, reload table, show success notification
6. Error: Show error message

---

## ✅ Validation Rules

### Required Fields:
- User selection
- Role
- Position name

### Optional Fields:
- Responsibilities
- Contact email (but if provided, must be valid email)
- Contact phone (but if provided, must be valid phone format)
- Display order (defaults to 99)
- Term dates
- Active status (defaults to true)

### Validation Rules:
```javascript
const validationSchema = Yup.object({
  user_id: Yup.number().required('User is required'),
  role: Yup.string()
    .oneOf(['president', 'vice_president', 'secretary', 'treasurer', 'member'])
    .required('Role is required'),
  position_name: Yup.string()
    .required('Position name is required')
    .max(100, 'Position name too long'),
  responsibilities: Yup.string()
    .max(500, 'Responsibilities too long'),
  contact_email: Yup.string()
    .email('Invalid email format')
    .nullable(),
  contact_phone: Yup.string()
    .matches(/^[\d\s\-\+\(\)]+$/, 'Invalid phone format')
    .nullable(),
  display_order: Yup.number()
    .min(1)
    .max(999)
    .nullable(),
  term_start_date: Yup.date().nullable(),
  term_end_date: Yup.date()
    .nullable()
    .min(Yup.ref('term_start_date'), 'End date must be after start date'),
  is_active: Yup.boolean()
});
```

---

## 🔐 Access Control

### Route Protection:
```javascript
// In App.jsx or routes config
<Route 
  path="/admin/committee" 
  element={
    <ProtectedRoute requiredRole="admin">
      <CommitteeManagement />
    </ProtectedRoute>
  } 
/>
```

### Navigation Visibility:
```javascript
// Only show menu item if user is admin
{user?.role === 'admin' && (
  <MenuItem component={Link} to="/admin/committee">
    <GroupsIcon /> Committee Management
  </MenuItem>
)}
```

---

## 🧪 Testing Checklist

### Create Operation:
- [ ] Dialog opens when clicking "Add Member"
- [ ] User dropdown populated with all users
- [ ] Role dropdown shows all 5 roles
- [ ] Form validation works (required fields)
- [ ] Email validation works
- [ ] Phone validation works
- [ ] Date validation works (end > start)
- [ ] Success notification on save
- [ ] Table refreshes with new member
- [ ] Dialog closes on success
- [ ] Error handling for API failures

### Edit Operation:
- [ ] Dialog opens with pre-filled data
- [ ] All fields editable
- [ ] Validation works
- [ ] Success notification on save
- [ ] Table refreshes with updated data
- [ ] Changes reflected on dashboard

### Delete Operation:
- [ ] Confirmation dialog appears
- [ ] Shows correct member name
- [ ] Cancel button works
- [ ] Delete button removes member
- [ ] Success notification shown
- [ ] Table refreshes
- [ ] Member removed from dashboard

### Access Control:
- [ ] Non-admin users cannot access /admin/committee
- [ ] Navigation item hidden for non-admins
- [ ] API returns 403 for non-admin requests

### UI/UX:
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Loading states shown
- [ ] Empty states shown
- [ ] Error messages clear and helpful
- [ ] Icons and badges consistent with dashboard

---

## 📦 Dependencies

### New Packages (if needed):
```bash
# Already installed (should be):
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install react-router-dom

# For form handling (optional, can use plain React):
npm install react-hook-form yup @hookform/resolvers

# For date picker:
npm install @mui/x-date-pickers dayjs
```

---

## 📚 File Changes Summary

### New Files (4):
1. `frontend/src/pages/admin/CommitteeManagement.jsx` - Main page
2. `frontend/src/components/admin/CommitteeMemberDialog.jsx` - Form dialog
3. `frontend/src/components/admin/CommitteeMemberTable.jsx` - Table component
4. `frontend/src/components/admin/DeleteConfirmDialog.jsx` - Delete confirmation

### Modified Files (3):
1. `frontend/src/App.jsx` - Add route
2. `frontend/src/components/layout/Sidebar.jsx` - Add navigation item
3. `frontend/src/components/admin/index.js` - Export new components

### No Backend Changes Required:
- All API endpoints already exist
- No schema changes needed
- No migration required

---

## 🚀 Implementation Order

1. **Phase 1: Core Components** (1-2 hours)
   - Create CommitteeMemberDialog.jsx
   - Create CommitteeMemberTable.jsx
   - Create DeleteConfirmDialog.jsx

2. **Phase 2: Page Integration** (30 mins)
   - Create CommitteeManagement.jsx
   - Integrate all components
   - Add state management

3. **Phase 3: Routing & Navigation** (30 mins)
   - Add route in App.jsx
   - Update Sidebar navigation
   - Add access control

4. **Phase 4: Testing** (1 hour)
   - Manual testing of all CRUD operations
   - Test validation
   - Test access control
   - Test responsive design

**Total Estimated Time:** 3-4 hours

---

## 📖 Documentation Updates

After implementation, update:
1. **FRONTEND_DEVELOPMENT_PLAN.md** - Add Phase 3.5: Admin Committee UI
2. **API_IMPLEMENTATION_PLAN.md** - Mark committee endpoints as "UI Complete"
3. **IMPLEMENTATION_CHECKLIST.md** - Check off admin UI for committee
4. Create **COMMITTEE_ADMIN_UI_SUMMARY.md** - Implementation summary

---

## 🎯 Success Criteria

✅ **Implementation Complete When:**
- [ ] Admin can create committee members via UI
- [ ] Admin can edit existing members
- [ ] Admin can delete members with confirmation
- [ ] All validation rules enforced
- [ ] Success/error notifications working
- [ ] Access control enforced (admin only)
- [ ] Navigation item added and visible to admins
- [ ] UI responsive and polished
- [ ] No console errors
- [ ] Dashboard reflects changes immediately

---

**Next Step:** Begin implementation with Phase 1 (Core Components)
