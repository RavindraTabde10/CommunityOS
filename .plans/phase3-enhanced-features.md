# Phase 3: Enhanced Features - Implementation Plan

**Created:** 2026-07-28  
**Status:** 🟡 Planning  
**Estimated Duration:** 10-12 days  
**Dependencies:** Phase 2 Complete ✅

---

## 📋 Overview

### Objective
Implement enhanced features including comments system, activity timeline, enhanced user profile management, and improved photo gallery with lightbox viewer.

### Success Criteria
- ✅ Users can add, edit, and delete comments on issues
- ✅ Activity timeline displays all issue changes
- ✅ Users can update their profile information
- ✅ Users can change their password
- ✅ Enhanced photo gallery with lightbox viewer
- ✅ All features are responsive and accessible
- ✅ Role-based permissions enforced

---

## 🎯 Phase 3 Components

### 3.1 Comments System (Day 1-4)
**Backend Status:** ✅ FULLY IMPLEMENTED

**Available Endpoints:**
- `POST /api/v1/issues/{issue_id}/comments` - Create comment
- `GET /api/v1/issues/{issue_id}/comments` - List comments
- `PUT /api/v1/issues/comments/{comment_id}` - Update comment
- `DELETE /api/v1/issues/comments/{comment_id}` - Delete comment

**Frontend Implementation:**

**Files to Create:**
```
frontend/src/
├── api/
│   └── commentService.js                 # Comment API calls
├── components/
│   └── comments/
│       ├── CommentSection.jsx            # Comments container
│       ├── CommentList.jsx               # List of comments
│       ├── CommentItem.jsx               # Single comment display
│       ├── CommentForm.jsx               # Add/edit comment form
│       └── CommentActions.jsx            # Edit/delete buttons
└── schemas/
    └── commentSchema.js                  # Zod validation for comments
```

**Features:**
- Display comments in chronological order
- Add new comments with validation
- Edit own comments (inline editing)
- Delete own comments (with confirmation)
- Show "edited" indicator if modified
- Relative timestamps (e.g., "2 hours ago")
- Character counter (1-2000 chars)
- Loading states for async operations
- Permission checking (owner or admin)

**Component Details:**

1. **CommentSection.jsx**
   - Container for all comment functionality
   - Fetches comments on mount
   - Handles pagination if needed
   - Props: `issueId`, `currentUser`

2. **CommentList.jsx**
   - Renders list of CommentItem components
   - Handles empty state
   - Shows loading skeleton
   - Props: `comments`, `loading`, `onEdit`, `onDelete`

3. **CommentItem.jsx**
   - Displays single comment
   - Shows user name, timestamp, content
   - Edit/delete buttons (conditional)
   - "Edited" badge if modified
   - Props: `comment`, `currentUser`, `onEdit`, `onDelete`

4. **CommentForm.jsx**
   - Textarea with character counter
   - Submit/cancel buttons
   - Validation feedback
   - Works for both add and edit modes
   - Props: `onSubmit`, `onCancel`, `initialValue`, `isEdit`

5. **CommentActions.jsx**
   - Edit and delete icon buttons
   - Only shown to comment owner or admin
   - Props: `onEdit`, `onDelete`, `canEdit`, `canDelete`

**API Service (commentService.js):**
```javascript
// GET /api/v1/issues/{issue_id}/comments
export const getComments = async (issueId, skip = 0, limit = 50) => {}

// POST /api/v1/issues/{issue_id}/comments
export const createComment = async (issueId, content) => {}

// PUT /api/v1/issues/comments/{comment_id}
export const updateComment = async (commentId, content) => {}

// DELETE /api/v1/issues/comments/{comment_id}
export const deleteComment = async (commentId) => {}
```

**Validation Schema (commentSchema.js):**
```javascript
import { z } from 'zod'

export const commentSchema = z.object({
  content: z.string()
    .min(1, 'Comment cannot be empty')
    .max(2000, 'Comment must be less than 2000 characters')
})
```

**Integration:**
- Add CommentSection to IssueDetail.jsx
- Place below issue information
- Above activity timeline

---

### 3.2 Activity Timeline (Day 5-6)
**Backend Status:** ✅ FULLY IMPLEMENTED

**Available Endpoint:**
- `GET /api/v1/issues/{issue_id}/activity` - Get activity log

**Frontend Implementation:**

**Files to Create:**
```
frontend/src/
├── api/
│   └── activityService.js                # Activity API calls
└── components/
    └── activity/
        ├── ActivityTimeline.jsx          # Timeline container
        ├── ActivityItem.jsx              # Single activity entry
        └── ActivityIcon.jsx              # Icon based on activity type
```

**Features:**
- Chronological timeline (newest first)
- Different icons for different activity types
- Field change display (old → new values)
- User name and relative timestamp
- Expandable/collapsible for long timelines
- Color-coded by activity type

**Activity Types:**
- `created` - Issue created
- `updated` - Issue updated (show field changes)
- `status_changed` - Status changed
- `commented` - Comment added
- `photo_uploaded` - Photo uploaded
- `assigned` - Issue assigned to contractor
- `deleted` - Issue deleted

**Component Details:**

1. **ActivityTimeline.jsx**
   - Container with timeline layout
   - Fetches activity on mount
   - Vertical timeline with connecting lines
   - Pagination or "Load More"
   - Props: `issueId`

2. **ActivityItem.jsx**
   - Single activity entry
   - Icon, user, timestamp, description
   - Shows field changes if applicable
   - Props: `activity`

3. **ActivityIcon.jsx**
   - Returns appropriate icon for activity type
   - Color-coded by action
   - Props: `activityType`

**Icon Mapping:**
```javascript
const activityIcons = {
  created: <AddCircleIcon color="success" />,
  updated: <EditIcon color="info" />,
  status_changed: <ChangeCircleIcon color="warning" />,
  commented: <CommentIcon color="primary" />,
  photo_uploaded: <PhotoIcon color="secondary" />,
  assigned: <AssignmentIcon color="info" />,
  deleted: <DeleteIcon color="error" />
}
```

**API Service (activityService.js):**
```javascript
// GET /api/v1/issues/{issue_id}/activity
export const getActivityLog = async (issueId, skip = 0, limit = 50) => {}
```

**Integration:**
- Add ActivityTimeline to IssueDetail.jsx
- Place below comments section
- Collapsible accordion or separate tab

---

### 3.3 User Profile Management (Day 7-9)
**Backend Status:** ✅ FULLY IMPLEMENTED

**Available Endpoints:**
- `PUT /api/v1/users/me` - Update profile
- `PUT /api/v1/users/me/password` - Change password

**Frontend Implementation:**

**Files to Modify/Create:**
```
frontend/src/
├── pages/
│   ├── Profile.jsx                       # VIEW - Enhanced profile page
│   ├── EditProfile.jsx                   # NEW - Edit profile form
│   └── ChangePassword.jsx                # NEW - Change password form
├── components/
│   └── profile/
│       ├── ProfileCard.jsx               # NEW - Profile info display
│       ├── ProfileHeader.jsx             # NEW - Profile header with avatar
│       └── ProfileActions.jsx            # NEW - Edit/password buttons
└── schemas/
    └── profileSchema.js                  # NEW - Zod validation
```

**Features:**

**Profile View (Profile.jsx):**
- Display all user information
- Edit Profile button
- Change Password button
- Account statistics (issues created, comments)
- Member since date

**Edit Profile (EditProfile.jsx):**
- Form with validation
- Editable fields: name, phone, unit_number
- Read-only fields: email, role
- Cancel/Save buttons
- Success/error notifications
- Redirect to profile after save

**Change Password (ChangePassword.jsx):**
- Current password field
- New password field
- Confirm new password field
- Password strength indicator
- Form validation
- Success/error notifications

**Component Details:**

1. **ProfileCard.jsx**
   - Card displaying user info
   - Grid layout with icons
   - Props: `user`

2. **ProfileHeader.jsx**
   - Large avatar/icon
   - User name and role
   - Member since date
   - Props: `user`

3. **ProfileActions.jsx**
   - Edit and Change Password buttons
   - Props: `onEdit`, `onChangePassword`

**Validation Schemas:**

```javascript
// profileSchema.js
export const profileUpdateSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number').optional(),
  unit_number: z.string().optional()
})

export const changePasswordSchema = z.object({
  current_password: z.string().min(1, 'Current password required'),
  new_password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[a-z]/, 'Must contain lowercase letter')
    .regex(/[0-9]/, 'Must contain number'),
  confirm_password: z.string()
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"]
})
```

**API Service Updates (userService.js):**
```javascript
// PUT /api/v1/users/me
export const updateProfile = async (data) => {}

// PUT /api/v1/users/me/password
export const changePassword = async (currentPassword, newPassword) => {}
```

**Routes:**
```
/profile                  - View profile
/profile/edit             - Edit profile
/profile/change-password  - Change password
```

---

### 3.4 Enhanced Photo Management (Day 10-11)

**Files to Create:**
```
frontend/src/
└── components/
    └── photos/
        ├── PhotoGallery.jsx              # Enhanced gallery grid
        ├── PhotoLightbox.jsx             # Full-screen viewer
        └── PhotoThumbnail.jsx            # Thumbnail with lazy loading
```

**Features:**

**PhotoGallery.jsx:**
- Grid layout (responsive)
- Click to open lightbox
- Image count badge
- Empty state if no photos
- Props: `photos`, `onPhotoClick`

**PhotoLightbox.jsx:**
- Full-screen modal
- Navigation arrows (prev/next)
- Keyboard navigation (arrow keys, ESC)
- Zoom in/out controls
- Image counter (e.g., "3 of 10")
- Close button
- Touch/swipe gestures for mobile
- Props: `photos`, `currentIndex`, `onClose`

**PhotoThumbnail.jsx:**
- Lazy loading with intersection observer
- Loading skeleton placeholder
- Error state if image fails
- Aspect ratio maintained
- Props: `photo`, `onClick`

**Key Features:**
- Responsive grid (1, 2, 3, or 4 columns based on screen size)
- Lazy loading for performance
- Image optimization
- Keyboard accessibility
- Mobile swipe gestures
- Download option
- Delete option (owner/admin only)

**Integration:**
- Replace existing photo display in IssueDetail.jsx
- Use PhotoGallery component

---

### 3.5 Testing & Refinement (Day 12)

**Manual Testing Checklist:**

**Comments:**
- [ ] Add comment on own issue
- [ ] Add comment on issue as admin
- [ ] Edit own comment
- [ ] Delete own comment with confirmation
- [ ] Cannot edit/delete other's comments (non-admin)
- [ ] Admin can delete any comment
- [ ] Character limit validation works
- [ ] Timestamps display correctly
- [ ] "Edited" indicator shows when appropriate

**Activity Timeline:**
- [ ] All activity types display correctly
- [ ] Field changes show old → new values
- [ ] Icons display for each activity type
- [ ] Timeline is chronological
- [ ] Pagination works if implemented
- [ ] No duplicate activities

**Profile Management:**
- [ ] View profile displays all information
- [ ] Edit profile form pre-populates
- [ ] Can update name, phone, unit_number
- [ ] Cannot edit email or role
- [ ] Validation errors display correctly
- [ ] Success message after update
- [ ] Changes reflect immediately

**Change Password:**
- [ ] Current password validation
- [ ] New password strength validation
- [ ] Confirm password matching
- [ ] Success message after change
- [ ] Can login with new password
- [ ] Old password no longer works

**Photo Gallery:**
- [ ] Gallery displays in grid
- [ ] Click opens lightbox
- [ ] Arrow navigation works
- [ ] Keyboard navigation works (arrows, ESC)
- [ ] Zoom in/out works
- [ ] Close button works
- [ ] Swipe gestures on mobile
- [ ] Image counter accurate
- [ ] Responsive on all screen sizes

**Responsive Design:**
- [ ] Mobile (320px-767px)
- [ ] Tablet (768px-1023px)
- [ ] Desktop (1024px+)

**Performance:**
- [ ] No console errors
- [ ] Fast page loads
- [ ] Smooth transitions
- [ ] Images load efficiently

---

## 🗂️ Affected Components

### New Files (25 files)
```
frontend/src/
├── api/
│   ├── commentService.js
│   └── activityService.js
├── components/
│   ├── comments/
│   │   ├── CommentSection.jsx
│   │   ├── CommentList.jsx
│   │   ├── CommentItem.jsx
│   │   ├── CommentForm.jsx
│   │   └── CommentActions.jsx
│   ├── activity/
│   │   ├── ActivityTimeline.jsx
│   │   ├── ActivityItem.jsx
│   │   └── ActivityIcon.jsx
│   ├── profile/
│   │   ├── ProfileCard.jsx
│   │   ├── ProfileHeader.jsx
│   │   └── ProfileActions.jsx
│   └── photos/
│       ├── PhotoGallery.jsx
│       ├── PhotoLightbox.jsx
│       └── PhotoThumbnail.jsx
├── pages/
│   ├── EditProfile.jsx
│   └── ChangePassword.jsx
└── schemas/
    ├── commentSchema.js
    └── profileSchema.js
```

### Modified Files (3 files)
```
frontend/src/
├── pages/
│   ├── Profile.jsx                       # ENHANCE - Full profile UI
│   └── issues/IssueDetail.jsx            # ADD - Comments, activity, gallery
└── api/
    └── userService.js                     # ADD - Update profile, change password
```

### Configuration Files
```
frontend/src/
└── App.jsx                                # ADD - Routes for edit profile, change password
```

---

## 📦 Dependencies

### Required (Already Installed)
- `@mui/material` - UI components
- `@mui/icons-material` - Icons
- `react-hook-form` - Form handling
- `zod` - Validation
- `axios` - API calls
- `react-toastify` - Notifications
- `date-fns` - Date formatting

### Optional (Consider Adding)
- `react-image-lightbox` - Advanced lightbox (OR build custom)
- `react-markdown` - Markdown support for comments (future)
- `react-intersection-observer` - Lazy loading images

---

## 🔄 Implementation Order

### Day 1-2: Comments Foundation
1. Create commentService.js
2. Create commentSchema.js
3. Create CommentItem.jsx (display only)
4. Create CommentList.jsx
5. Test with mock data

### Day 3-4: Comments Functionality
1. Create CommentForm.jsx
2. Create CommentActions.jsx
3. Create CommentSection.jsx (integrate all)
4. Add to IssueDetail.jsx
5. Test CRUD operations

### Day 5-6: Activity Timeline
1. Create activityService.js
2. Create ActivityIcon.jsx
3. Create ActivityItem.jsx
4. Create ActivityTimeline.jsx
5. Add to IssueDetail.jsx
6. Test all activity types

### Day 7-8: Profile Management
1. Enhance Profile.jsx (view mode)
2. Create ProfileCard.jsx
3. Create ProfileHeader.jsx
4. Create ProfileActions.jsx
5. Test profile view

### Day 9: Edit Profile & Password
1. Create profileSchema.js
2. Create EditProfile.jsx
3. Create ChangePassword.jsx
4. Update userService.js
5. Add routes to App.jsx
6. Test update and password change

### Day 10-11: Photo Gallery Enhancement
1. Create PhotoThumbnail.jsx
2. Create PhotoGallery.jsx
3. Create PhotoLightbox.jsx
4. Replace gallery in IssueDetail.jsx
5. Test on all devices

### Day 12: Testing & Polish
1. Complete testing checklist
2. Fix bugs
3. Optimize performance
4. Improve accessibility
5. Update documentation

---

## 🧪 Testing Strategy

### Unit Testing (Future)
- Comment form validation
- Profile form validation
- Password validation
- Date formatting utilities

### Integration Testing
- Comment CRUD operations
- Activity log fetching
- Profile update flow
- Password change flow

### Manual Testing
- Complete testing checklist above
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Responsive design testing
- Accessibility testing (keyboard navigation, screen reader)

---

## 📚 Documentation Updates

### Files to Update
- [x] `.plans/phase3-enhanced-features.md` (this file)
- [ ] `FRONTEND_DEVELOPMENT_PLAN.md` - Update Phase 3 status
- [ ] `IMPLEMENTATION_CHECKLIST.md` - Check off Phase 3 items
- [ ] `frontend/README.md` - Document new components
- [ ] `frontend/PHASE3_COMPLETION_SUMMARY.md` - Create upon completion

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Comment Permissions
**Problem:** Users might try to edit/delete others' comments  
**Solution:** Implement strict permission checking on frontend + backend validates

### Issue 2: Activity Log Performance
**Problem:** Large number of activities could slow page  
**Solution:** Implement pagination, lazy loading, or "Load More" button

### Issue 3: Photo Lightbox Mobile UX
**Problem:** Lightbox might not work well on small screens  
**Solution:** Test extensively on mobile, add swipe gestures, optimize touch targets

### Issue 4: Password Change Security
**Problem:** Need to validate current password  
**Solution:** Backend validates current password before allowing change

### Issue 5: Form State Management
**Problem:** Multiple forms might have conflicting state  
**Solution:** Use React Hook Form with proper cleanup, unique form IDs

---

## 🎯 Success Metrics

### Functionality
- ✅ All CRUD operations work for comments
- ✅ Activity timeline displays all events correctly
- ✅ Profile updates save successfully
- ✅ Password changes work and are validated
- ✅ Photo gallery provides excellent UX

### Performance
- ✅ Comments load in < 1 second
- ✅ Activity timeline loads in < 1 second
- ✅ Photo gallery responsive on all devices
- ✅ No lag when scrolling or interacting

### User Experience
- ✅ Intuitive and easy to use
- ✅ Clear feedback for all actions
- ✅ Responsive on mobile, tablet, desktop
- ✅ Accessible via keyboard
- ✅ No confusing error messages

### Code Quality
- ✅ Components are reusable
- ✅ Consistent with existing patterns
- ✅ Well-documented with comments
- ✅ No console warnings or errors
- ✅ Follows React best practices

---

## 🚀 Ready to Begin?

This plan provides a complete roadmap for Phase 3 implementation. Each section is detailed with:
- Specific files to create/modify
- Component specifications
- API integrations
- Validation rules
- Testing requirements

**Next Steps:**
1. Review and approve this plan
2. Begin Day 1-2: Comments Foundation
3. Follow implementation order systematically
4. Test thoroughly at each milestone
5. Update documentation as you go

**Estimated Timeline:** 10-12 days (can be adjusted based on progress)

---

**Plan Created By:** GitHub Copilot  
**Date:** 2026-07-28  
**Phase:** Phase 3 - Enhanced Features  
**Status:** Ready for Implementation 🚀
