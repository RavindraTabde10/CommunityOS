import { useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Box, TextField, Button, Typography, Link, Alert } from '@mui/material'
import { forgotPasswordSchema } from '../../utils/validation'
import { useToast } from '../../hooks/useToast'
import authService from '../../api/authService'
import { ROUTES } from '../../utils/constants'

/**
 * Forgot password form component
 */
const ForgotPasswordForm = () => {
  const toast = useToast()
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  })

  const onSubmit = async (data) => {
    setError(null)
    setSuccess(false)

    try {
      await authService.forgotPassword(data.email)
      setSuccess(true)
      toast.success('Password reset link sent to your email!')
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to send reset link'
      setError(errorMessage)
      toast.error(errorMessage)
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Typography variant="h5" component="h2" gutterBottom align="center" fontWeight={600}>
        Forgot Password?
      </Typography>
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
        Enter your email address and we'll send you a link to reset your password
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Password reset link has been sent to your email. Please check your inbox.
        </Alert>
      )}

      <Controller
        name="email"
        control={control}
        render={({ field }) => (
          <TextField
            {...field}
            fullWidth
            label="Email Address"
            type="email"
            autoComplete="email"
            autoFocus
            error={!!errors.email}
            helperText={errors.email?.message}
            sx={{ mb: 3 }}
            disabled={success}
          />
        )}
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        size="large"
        disabled={isSubmitting || success}
        sx={{ mb: 2 }}
      >
        {isSubmitting ? 'Sending...' : 'Send Reset Link'}
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

export default ForgotPasswordForm
