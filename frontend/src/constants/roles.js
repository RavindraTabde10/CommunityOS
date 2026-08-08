// User roles (must match backend enum values)
export const USER_ROLES = {
  ADMIN: 'admin',
  RESIDENT: 'resident',
  CONTRACTOR: 'contractor',
  BUILDER: 'builder',
  SECURITY: 'security',
}

// Role display names
export const ROLE_LABELS = {
  [USER_ROLES.ADMIN]: 'Administrator',
  [USER_ROLES.RESIDENT]: 'Resident',
  [USER_ROLES.CONTRACTOR]: 'Contractor',
  [USER_ROLES.BUILDER]: 'Builder',
}

// Role descriptions
export const ROLE_DESCRIPTIONS = {
  [USER_ROLES.ADMIN]: 'Full access to all features and user management',
  [USER_ROLES.RESIDENT]: 'Can create and manage own issues',
  [USER_ROLES.CONTRACTOR]: 'Can view and update assigned issues',
  [USER_ROLES.BUILDER]: 'Can view all issues and assign contractors',
}

// Role options for registration/selection
export const ROLE_OPTIONS = [
  {
    value: USER_ROLES.RESIDENT,
    label: ROLE_LABELS[USER_ROLES.RESIDENT],
    description: ROLE_DESCRIPTIONS[USER_ROLES.RESIDENT],
  },
  {
    value: USER_ROLES.CONTRACTOR,
    label: ROLE_LABELS[USER_ROLES.CONTRACTOR],
    description: ROLE_DESCRIPTIONS[USER_ROLES.CONTRACTOR],
  },
  {
    value: USER_ROLES.BUILDER,
    label: ROLE_LABELS[USER_ROLES.BUILDER],
    description: ROLE_DESCRIPTIONS[USER_ROLES.BUILDER],
  },
]
