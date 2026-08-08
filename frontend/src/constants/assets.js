export const ASSET_TYPES = {
  gym:          { label: 'Gym',           icon: '🏋️', color: '#e53935' },
  pool:         { label: 'Swimming Pool', icon: '🏊', color: '#039be5' },
  clubhouse:    { label: 'Clubhouse',     icon: '🏠', color: '#7b1fa2' },
  party_hall:   { label: 'Party Hall',    icon: '🎉', color: '#f57c00' },
  sports_court: { label: 'Sports Court',  icon: '⚽', color: '#388e3c' },
  meeting_room: { label: 'Meeting Room',  icon: '📋', color: '#5d4037' },
  parking:      { label: 'Parking',       icon: '🅿️', color: '#455a64' },
  other:        { label: 'Other',         icon: '🏢', color: '#757575' },
}

export const ASSET_TYPE_OPTIONS = Object.entries(ASSET_TYPES).map(([value, cfg]) => ({
  value,
  label: cfg.label,
}))

export const BOOKING_STATUS = {
  pending:   { label: 'Pending',   color: 'warning' },
  confirmed: { label: 'Confirmed', color: 'success' },
  cancelled: { label: 'Cancelled', color: 'error'   },
  completed: { label: 'Completed', color: 'default' },
  no_show:   { label: 'No Show',   color: 'error'   },
}
