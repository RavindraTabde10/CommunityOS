import { Paper, Grid, Box, Typography } from '@mui/material'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'
import HomeIcon from '@mui/icons-material/Home'
import BadgeIcon from '@mui/icons-material/Badge'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import { ROLE_LABELS } from '../../constants/roles'

/**
 * ProfileCard Component
 * Displays user information in a grid layout
 */
const ProfileCard = ({ user }) => {
  const InfoItem = ({ icon, label, value }) => (
    <Grid item xs={12} sm={6}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box
          sx={{
            mr: 2,
            color: 'primary.main',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" display="block">
            {label}
          </Typography>
          <Typography variant="body1" fontWeight="500">
            {value || 'N/A'}
          </Typography>
        </Box>
      </Box>
    </Grid>
  )

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 4,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
      }}
    >
      <Typography variant="h6" gutterBottom fontWeight="bold">
        Personal Information
      </Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        <InfoItem
          icon={<BadgeIcon />}
          label="Full Name"
          value={user?.name}
        />

        <InfoItem
          icon={<EmailIcon />}
          label="Email Address"
          value={user?.email}
        />

        <InfoItem
          icon={<PhoneIcon />}
          label="Phone Number"
          value={user?.phone}
        />

        <InfoItem
          icon={<HomeIcon />}
          label="Unit Number"
          value={user?.unit_number}
        />

        <InfoItem
          icon={<BadgeIcon />}
          label="Role"
          value={ROLE_LABELS[user?.role] || user?.role}
        />

        <InfoItem
          icon={<CalendarTodayIcon />}
          label="Member Since"
          value={formatDate(user?.created_at)}
        />
      </Grid>
    </Paper>
  )
}

export default ProfileCard
