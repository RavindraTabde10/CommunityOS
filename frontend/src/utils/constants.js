// Application constants

export const APP_NAME = import.meta.env.VITE_APP_NAME || 'Riverdale Grove Connect'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

// Local storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
}

// API routes
export const API_ROUTES = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  USERS: {
    BASE: '/users',
    ME: '/users/me',
    UPDATE_PASSWORD: '/users/me/password',
  },
  ISSUES: {
    BASE: '/issues',
    PHOTOS: (id) => `/issues/${id}/photos`,
    COMMENTS: (id) => `/issues/${id}/comments`,
    ACTIVITY: (id) => `/issues/${id}/activity`,
  },
}

// Navigation routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  DASHBOARD: '/dashboard',
  ISSUES: '/issues',
  ISSUES_CREATE: '/issues/new',
  ISSUES_DETAIL: (id) => `/issues/${id}`,
  ISSUES_EDIT: (id) => `/issues/${id}/edit`,
  PROFILE: '/profile',
  PROFILE_EDIT: '/profile/edit',
  PROFILE_CHANGE_PASSWORD: '/profile/change-password',
  RESIDENTS: '/residents',
  POLLS: '/polls',
  POLLS_CREATE: '/polls/create',
  POLLS_EDIT: (id) => `/polls/${id}/edit`,
  FEEDBACK: '/feedback',
  SECURITY: '/security/visitors',
  VISITOR_APPROVAL: '/security/my-visitors',
  ASSETS: '/assets',
  ASSET_DETAIL: (id) => `/assets/${id}`,
  SCAN_QR: '/assets/scan',
  BOOKINGS: '/bookings',
  WATER_TANKER: '/water-tanker',
  ADMIN: {
    USERS: '/admin/users',
    PENDING_USERS: '/admin/pending-users',
    REPORTS: '/admin/reports',
    SETTINGS: '/admin/settings',
    COMMITTEE: '/admin/committee',
    ASSETS: '/admin/assets',
  },
  REPORTS: {
    DASHBOARD:   '/reports',
    ISSUES:      '/reports/issues',
    ASSETS:      '/reports/assets',
    CONTRACTORS: '/reports/contractors',
    EXPORT:      '/reports/export',
  },
}

// Issue status
export const ISSUE_STATUS = {
  OPEN: 'OPEN',
  IN_PROGRESS: 'IN_PROGRESS',
  RESOLVED: 'RESOLVED',
  CLOSED: 'CLOSED',
}

export const ISSUE_STATUS_LABELS = {
  [ISSUE_STATUS.OPEN]: 'Open',
  [ISSUE_STATUS.IN_PROGRESS]: 'In Progress',
  [ISSUE_STATUS.RESOLVED]: 'Resolved',
  [ISSUE_STATUS.CLOSED]: 'Closed',
}

export const ISSUE_STATUS_COLORS = {
  [ISSUE_STATUS.OPEN]: 'error',
  [ISSUE_STATUS.IN_PROGRESS]: 'warning',
  [ISSUE_STATUS.RESOLVED]: 'success',
  [ISSUE_STATUS.CLOSED]: 'default',
}

// Issue priority
export const ISSUE_PRIORITY = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL',
}

export const ISSUE_PRIORITY_LABELS = {
  [ISSUE_PRIORITY.LOW]: 'Low',
  [ISSUE_PRIORITY.MEDIUM]: 'Medium',
  [ISSUE_PRIORITY.HIGH]: 'High',
  [ISSUE_PRIORITY.CRITICAL]: 'Critical',
}

export const ISSUE_PRIORITY_COLORS = {
  [ISSUE_PRIORITY.LOW]: 'info',
  [ISSUE_PRIORITY.MEDIUM]: 'warning',
  [ISSUE_PRIORITY.HIGH]: 'error',
  [ISSUE_PRIORITY.CRITICAL]: 'error',
}

// Issue category
export const ISSUE_CATEGORY = {
  PLUMBING: 'PLUMBING',
  ELECTRICAL: 'ELECTRICAL',
  CARPENTRY: 'CARPENTRY',
  PAINTING: 'PAINTING',
  FLOORING: 'FLOORING',
  CIVIL: 'CIVIL',
  OTHER: 'OTHER',
}

export const ISSUE_CATEGORY_LABELS = {
  [ISSUE_CATEGORY.PLUMBING]: 'Plumbing',
  [ISSUE_CATEGORY.ELECTRICAL]: 'Electrical',
  [ISSUE_CATEGORY.CARPENTRY]: 'Carpentry',
  [ISSUE_CATEGORY.PAINTING]: 'Painting',
  [ISSUE_CATEGORY.FLOORING]: 'Flooring',
  [ISSUE_CATEGORY.CIVIL]: 'Civil Work',
  [ISSUE_CATEGORY.OTHER]: 'Other',
}
