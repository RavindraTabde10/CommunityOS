import { useState } from 'react'
import { useNavigate, useSearchParams, Link as RouterLink } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Box,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Visibility, VisibilityOff } from '@mui/icons-material'
import { resetPasswordSchema } from '../../utils/validation'
import { useToast } from '../../hooks/useToast'
import authService from '../../api/authService'
import { ROUTES } from '../../utils/constants'

/**
 * Reset password form component
 */
const ResetPasswordForm = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const toast = useToast()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState(null)

  const token = searchParams.get('token')

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  })

  const onSubmit = async (data) => {
    setError(null)

    if (!token) {
      setError('Invalid reset token')
      return
    }

    try {
      await authService.resetPassword(token, data.password)
      toast.success('Password reset successful! Please login with your new password.')
      navigate(ROUTES.LOGIN)
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to reset password'
      setError(errorMessage)
      toast.error(errorMessage)
    }
  }

  if (!token) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          Invalid or missing reset token. Please request a new password reset link.
        </Alert>
        <Button
          component={RouterLink}
          to={ROUTES.FORGOT_PASSWORD}
          fullWidth
          variant="contained"
        >
          Request New Link
        </Button>
      </Box>
    )
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Typography variant="h5" component="h2" gutterBottom align="center" fontWeight={600}>
        Reset Password
      </Typography>
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
        Enter your new password below
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Controller
        name="password"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            fullWidth
            label="New Password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="new-password"
            autoFocus
            error={!!errors.password}
            helperText={errors.password?.message}
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        )}
      />

      <Controller
        name="confirmPassword"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            fullWidth
            label="Confirm Password"
            type={showConfirmPassword ? 'text' : 'password'}
            autoComplete="new-password"
            error={!!errors.confirmPassword}
            helperText={errors.confirmPassword?.message}
            sx={{ mb: 3 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    edge="end"
                  >
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        )}
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        size="large"
        disabled={isSubmitting}
        sx={{ mb: 2 }}
      >
        {isSubmitting ? 'Resetting...' : 'Reset Password'}
      </Button>

      <Typography variant="body2" align="center">
        Remember your password?{' '}
        <Link component={RouterLink} to={ROUTES.LOGIN} underline="hover" fontWeight={600}>
          Sign in
        </Link>
      </Typography>
    </Box>
  )
}

export default ResetPasswordForm
