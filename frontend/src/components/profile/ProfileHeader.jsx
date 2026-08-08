import { Box, Avatar, Typography, Paper } from '@mui/material'
import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import { ROLE_LABELS } from '../../constants/roles'
import { formatDistanceToNow } from 'date-fns'

/**
 * ProfileHeader Component
 * Large avatar, name, role, and member since date
 */
const ProfileHeader = ({ user }) => {
  const memberSince = user?.created_at
    ? formatDistanceToNow(new Date(user.created_at), { addSuffix: true })
    : 'recently'

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 4, 
        mb: 3, 
        textAlign: 'center',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
      }}
    >
      <Avatar
        sx={{
          width: 100,
          height: 100,
          margin: '0 auto',
          mb: 2,
          bgcolor: 'primary.main',
          fontSize: 48
        }}
      >
        <AccountCircleIcon fontSize="inherit" />
      </Avatar>

      <Typography variant="h4" gutterBottom fontWeight="bold">
        {user?.name || 'User'}
      </Typography>

      <Typography variant="h6" color="primary" gutterBottom>
        {ROLE_LABELS[user?.role] || user?.role || 'User'}
      </Typography>

      <Typography variant="body2" color="text.secondary">
        Member {memberSince}
      </Typography>
    </Paper>
  )
}

export default ProfileHeader
