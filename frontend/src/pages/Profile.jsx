import { Container, Typography, Box, CircularProgress } from '@mui/material'
import { useAuth } from '../hooks/useAuth'
import ProfileHeader from '../components/profile/ProfileHeader'
import ProfileCard from '../components/profile/ProfileCard'
import ProfileActions from '../components/profile/ProfileActions'

/**
 * Profile page - View user profile
 */
const Profile = () => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress sx={{ color: 'white' }} />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ color: 'white' }}>
        My Profile
      </Typography>

      {/* Profile Header */}
      <ProfileHeader user={user} />

      {/* Action Buttons */}
      <ProfileActions />

      {/* Profile Information Card */}
      <ProfileCard user={user} />
    </Container>
  )
}

export default Profile
