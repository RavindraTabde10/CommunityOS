import { Box, Button } from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import LockIcon from '@mui/icons-material/Lock'
import { useNavigate } from 'react-router-dom'

/**
 * ProfileActions Component
 * Edit Profile and Change Password buttons
 */
const ProfileActions = () => {
  const navigate = useNavigate()

  return (
    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 3 }}>
      <Button
        variant="contained"
        startIcon={<EditIcon />}
        onClick={() => navigate('/profile/edit')}
      >
        Edit Profile
      </Button>

      <Button
        variant="outlined"
        startIcon={<LockIcon />}
        onClick={() => navigate('/profile/change-password')}
      >
        Change Password
      </Button>
    </Box>
  )
}

export default ProfileActions
