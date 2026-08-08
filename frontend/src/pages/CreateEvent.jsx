/**
 * Create Event Page
 * Admin-only page for creating new events
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  MenuItem,
  FormControlLabel,
  Switch,
  Grid,
  Alert,
} from '@mui/material'
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material'
import { toast } from 'react-toastify'
import { eventsAPI } from '../api/events'
import { USER_ROLES } from '../constants/roles'

const EVENT_TYPES = [
  { value: 'MEETING', label: 'Meeting', icon: '📋' },
  { value: 'FESTIVAL', label: 'Festival', icon: '🎉' },
  { value: 'MAINTENANCE', label: 'Maintenance', icon: '🔧' },
  { value: 'SOCIAL', label: 'Social', icon: '🎊' },
  { value: 'SPORTS', label: 'Sports', icon: '⚽' },
  { value: 'OTHER', label: 'Other', icon: '📅' }
]

const CreateEvent = () => {
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  // Redirect if not admin
  useEffect(() => {
    if (user && user.role !== USER_ROLES.ADMIN) {
      toast.error('Access denied. Admin privileges required.')
      navigate('/events')
    }
  }, [user, navigate])

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_type: 'MEETING',
    venue: '',
    start_datetime: '',
    end_datetime: '',
    is_active: true
  })

  const handleChange = (e) => {
    const { name, value, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'is_active' ? checked : value
    }))
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }

    if (!formData.event_type) {
      newErrors.event_type = 'Event type is required'
    }

    if (!formData.start_datetime) {
      newErrors.start_datetime = 'Start date and time is required'
    }

    // Validate end date is after start date if provided
    if (formData.end_datetime && formData.start_datetime) {
      const start = new Date(formData.start_datetime)
      const end = new Date(formData.end_datetime)
      if (end <= start) {
        newErrors.end_datetime = 'End date must be after start date'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error('Please fix the errors in the form')
      return
    }

    try {
      setLoading(true)

      // Prepare data - format datetime values properly
      const submitData = {
        title: formData.title.trim(),
        description: formData.description?.trim() || null,
        event_type: formData.event_type,
        venue: formData.venue?.trim() || null,
        start_datetime: formData.start_datetime ? `${formData.start_datetime}:00` : null,
        end_datetime: formData.end_datetime ? `${formData.end_datetime}:00` : null,
        is_active: formData.is_active
      }

      console.log('Submitting event data:', submitData)
      await eventsAPI.create(submitData)
      toast.success('Event created successfully')
      navigate('/events')
    } catch (err) {
      console.error('Error creating event:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create event'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/events')}
        >
          Back
        </Button>
        <Typography variant="h4" fontWeight="bold">
          Create New Event
        </Typography>
      </Box>

      {/* Form */}
      <Paper sx={{ p: 3, maxWidth: 800 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Title */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Event Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                error={Boolean(errors.title)}
                helperText={errors.title}
                placeholder="e.g., Annual General Meeting"
              />
            </Grid>

            {/* Event Type */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                select
                label="Event Type"
                name="event_type"
                value={formData.event_type}
                onChange={handleChange}
                error={Boolean(errors.event_type)}
                helperText={errors.event_type}
              >
                {EVENT_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <span>{type.icon}</span>
                      <span>{type.label}</span>
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Venue */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Venue"
                name="venue"
                value={formData.venue}
                onChange={handleChange}
                placeholder="e.g., Community Hall"
              />
            </Grid>

            {/* Start Date & Time */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                type="datetime-local"
                label="Start Date & Time"
                name="start_datetime"
                value={formData.start_datetime}
                onChange={handleChange}
                error={Boolean(errors.start_datetime)}
                helperText={errors.start_datetime}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* End Date & Time */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="datetime-local"
                label="End Date & Time (Optional)"
                name="end_datetime"
                value={formData.end_datetime}
                onChange={handleChange}
                error={Boolean(errors.end_datetime)}
                helperText={errors.end_datetime}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Description */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Provide details about the event..."
              />
            </Grid>

            {/* Active Status */}
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleChange}
                    name="is_active"
                    color="primary"
                  />
                }
                label="Active (event will be visible to residents)"
              />
            </Grid>

            {/* Info Alert */}
            <Grid item xs={12}>
              <Alert severity="info">
                <strong>Note:</strong> Active events will be displayed on the dashboard and events page.
                Residents will receive notifications about upcoming events.
              </Alert>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/events')}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={<SaveIcon />}
                  disabled={loading}
                >
                  {loading ? 'Creating...' : 'Create Event'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  )
}

export default CreateEvent
