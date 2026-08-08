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
  InputAdornment,
  IconButton,
  LinearProgress
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import LockIcon from '@mui/icons-material/Lock'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { changePasswordSchema } from '../schemas/profileSchema'
import { toast } from 'react-toastify'
import userService from '../api/userService'

/**
 * Calculate password strength
 */
const calculatePasswordStrength = (password) => {
  if (!password) return 0
  let strength = 0
  
  if (password.length >= 8) strength += 25
  if (password.length >= 12) strength += 15
  if (/[A-Z]/.test(password)) strength += 20
  if (/[a-z]/.test(password)) strength += 20
  if (/[0-9]/.test(password)) strength += 20
  if (/[^A-Za-z0-9]/.test(password)) strength += 20
  
  return Math.min(strength, 100)
}

/**
 * Get password strength color
 */
const getStrengthColor = (strength) => {
  if (strength < 40) return 'error'
  if (strength < 70) return 'warning'
  return 'success'
}

/**
 * ChangePassword page - Change user password
 */
const ChangePassword = () => {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  })

  const newPassword = watch('new_password', '')
  const passwordStrength = calculatePasswordStrength(newPassword)

  const onSubmit = async (data) => {
    try {
      setIsSubmitting(true)
      setError(null)

      // Change password
      await userService.changePassword(data.current_password, data.new_password)

      toast.success('Password changed successfully!')
      reset()
      navigate('/profile')
    } catch (err) {
      console.error('Error changing password:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to change password'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
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
          Change Password
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
          {/* Current Password */}
          <TextField
            {...register('current_password')}
            label="Current Password"
            type={showCurrentPassword ? 'text' : 'password'}
            fullWidth
            margin="normal"
            error={!!errors.current_password}
            helperText={errors.current_password?.message}
            disabled={isSubmitting}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    edge="end"
                  >
                    {showCurrentPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />

          {/* New Password */}
          <TextField
            {...register('new_password')}
            label="New Password"
            type={showNewPassword ? 'text' : 'password'}
            fullWidth
            margin="normal"
            error={!!errors.new_password}
            helperText={errors.new_password?.message}
            disabled={isSubmitting}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    edge="end"
                  >
                    {showNewPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />

          {/* Password Strength Indicator */}
          {newPassword && (
            <Box sx={{ mt: 1, mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Password Strength
                </Typography>
                <Typography variant="caption" color={getStrengthColor(passwordStrength)}>
                  {passwordStrength < 40 ? 'Weak' : passwordStrength < 70 ? 'Medium' : 'Strong'}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={passwordStrength}
                color={getStrengthColor(passwordStrength)}
              />
            </Box>
          )}

          {/* Confirm Password */}
          <TextField
            {...register('confirm_password')}
            label="Confirm New Password"
            type={showConfirmPassword ? 'text' : 'password'}
            fullWidth
            margin="normal"
            error={!!errors.confirm_password}
            helperText={errors.confirm_password?.message}
            disabled={isSubmitting}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    edge="end"
                  >
                    {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />

          {/* Password Requirements */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="caption" component="div" gutterBottom>
              Password must contain:
            </Typography>
            <Typography variant="caption" component="ul" sx={{ pl: 2, m: 0 }}>
              <li>At least 8 characters</li>
              <li>One uppercase letter</li>
              <li>One lowercase letter</li>
              <li>One number</li>
            </Typography>
          </Alert>

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
              startIcon={isSubmitting ? <CircularProgress size={20} /> : <LockIcon />}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Changing...' : 'Change Password'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  )
}

export default ChangePassword
