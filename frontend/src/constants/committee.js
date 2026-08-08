/**
 * Committee Constants
 * Constants for committee roles, labels, and icons
 */

// Role value constants
export const COMMITTEE_ROLES = {
  PRESIDENT: 'president',
  VICE_PRESIDENT: 'vice_president',
  SECRETARY: 'secretary',
  TREASURER: 'treasurer',
  MEMBER: 'member'
}

// Array of role values (for dropdowns and mapping)
export const COMMITTEE_ROLES_ARRAY = [
  'president',
  'vice_president',
  'secretary',
  'treasurer',
  'member'
]

export const ROLE_LABELS = {
  president: 'President',
  vice_president: 'Vice President',
  secretary: 'Secretary',
  treasurer: 'Treasurer',
  member: 'Committee Member'
}

export const ROLE_ICONS = {
  president: '👑',
  vice_president: '🥈',
  secretary: '📝',
  treasurer: '💰',
  member: '👤'
}

export const getRoleLabel = (role) => ROLE_LABELS[role] || role
export const getRoleIcon = (role) => ROLE_ICONS[role] || '👤'
