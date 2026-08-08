import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SaveIcon from '@mui/icons-material/Save'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { profileUpdateSchema } from '../schemas/profileSchema'
import { toast } from 'react-toastify'
import { useAuth } from '../hooks/useAuth'
import userService from '../api/userService'

/**
 * EditProfile page - Edit user profile
 */
const EditProfile = () => {
  const navigate = useNavigate()
  const { user, fetchCurrentUser } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const isAdmin = user?.role === 'admin'

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({
    resolver: zodResolver(profileUpdateSchema),
    defaultValues: {
      name: user?.name || '',
      phone: user?.phone || '',
      unit_number: user?.unit_number || '',
      residency_type: user?.residency_type || ''
    }
  })

  const onSubmit = async (data) => {
    try {
      setIsSubmitting(true)
      setError(null)

      // Update profile
      await userService.updateProfile(data)

      // Refresh user data
      await fetchCurrentUser()

      toast.success('Profile updated successfully!')
      navigate('/profile')
    } catch (err) {
      console.error('Error updating profile:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to update profile'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!user) {
    return (
      <Container maxWidth="sm" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/profile')}
          sx={{ 
            mr: 2,
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.25)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            },
          }}
        >
          Back
        </Button>
        <Typography variant="h4" fontWeight="bold" sx={{ color: 'white' }}>
          Edit Profile
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {error}
        </Alert>
      )}

      {/* Form */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
        }}
      >
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          {/* Name */}
          <TextField
            {...register('name')}
            label="Full Name"
            fullWidth
            margin="normal"
            error={!!errors.name}
            helperText={errors.name?.message}
            disabled={isSubmitting}
          />

          {/* Email (read-only) */}
          <TextField
            label="Email Address"
            fullWidth
            margin="normal"
            value={user.email}
            disabled
            helperText="Email cannot be changed"
          />

          {/* Phone */}
          <TextField
            {...register('phone')}
            label="Phone Number"
            fullWidth
            margin="normal"
            placeholder="+1234567890 or 1234567890"
            error={!!errors.phone}
            helperText={errors.phone?.message || 'Enter a valid phone number (optional)'}
            disabled={isSubmitting}
          />

          {/* Unit Number */}
          <TextField
            {...register('unit_number')}
            label="Unit Number"
            fullWidth
            margin="normal"
            placeholder="A-101"
            error={!!errors.unit_number}
            helperText={isAdmin ? errors.unit_number?.message : 'Only admin can change unit number'}
            disabled={isSubmitting || !isAdmin}
            InputProps={{ readOnly: !isAdmin }}
          />

          {/* Residency Type */}
          <FormControl fullWidth margin="normal" error={!!errors.residency_type} disabled={!isAdmin}>
            <InputLabel id="residency-type-label">Occupancy Type</InputLabel>
            <Select
              {...register('residency_type')}
              labelId="residency-type-label"
              label="Occupancy Type"
              defaultValue={user?.residency_type || ''}
              disabled={isSubmitting || !isAdmin}
              inputProps={{ readOnly: !isAdmin }}
            >
              <MenuItem value="">Not specified</MenuItem>
              <MenuItem value="owner">Owner</MenuItem>
              <MenuItem value="tenant">Tenant / Renter</MenuItem>
            </Select>
            <FormHelperText>
              {errors.residency_type?.message || (!isAdmin ? 'Only admin can change occupancy type' : '')}
            </FormHelperText>
          </FormControl>

          {/* Role (read-only) */}
          <TextField
            label="Role"
            fullWidth
            margin="normal"
            value={user.role || ''}
            disabled
            helperText="Role cannot be changed"
          />

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate('/profile')}
              disabled={isSubmitting}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              variant="contained"
              fullWidth
              startIcon={isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  )
}

export default EditProfile
