/**
 * Edit Event Page
 * Admin-only page for updating existing events
 */
import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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
  CircularProgress,
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

const formatDateTimeForInput = (dateString) => {
  if (!dateString) {
    return ''
  }

  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) {
    return ''
  }

  // Convert UTC/API datetime to local datetime-local input format.
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return localDate.toISOString().slice(0, 16)
}

const EditEvent = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const { user } = useSelector((state) => state.auth)

  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [errors, setErrors] = useState({})
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_type: 'MEETING',
    venue: '',
    start_datetime: '',
    end_datetime: '',
    is_active: true
  })

  useEffect(() => {
    if (user && user.role !== USER_ROLES.ADMIN) {
      toast.error('Access denied. Admin privileges required.')
      navigate('/events')
      return
    }

    if (user?.role === USER_ROLES.ADMIN) {
      fetchEvent()
    }
  }, [user, id, navigate])

  const fetchEvent = async () => {
    try {
      setInitialLoading(true)
      const response = await eventsAPI.getById(id)
      const event = response.data

      setFormData({
        title: event.title || '',
        description: event.description || '',
        event_type: event.event_type || 'MEETING',
        venue: event.venue || '',
        start_datetime: formatDateTimeForInput(event.start_datetime),
        end_datetime: formatDateTimeForInput(event.end_datetime),
        is_active: event.is_active ?? true
      })
    } catch (err) {
      console.error('Error fetching event:', err)
      toast.error(err.response?.data?.detail || 'Failed to load event')
      navigate('/events')
    } finally {
      setInitialLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'is_active' ? checked : value
    }))

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
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

      const submitData = {
        title: formData.title.trim(),
        description: formData.description?.trim() || null,
        event_type: formData.event_type,
        venue: formData.venue?.trim() || null,
        start_datetime: formData.start_datetime ? `${formData.start_datetime}:00` : null,
        end_datetime: formData.end_datetime ? `${formData.end_datetime}:00` : null,
        is_active: formData.is_active
      }

      await eventsAPI.update(id, submitData)
      toast.success('Event updated successfully')
      navigate('/events')
    } catch (err) {
      console.error('Error updating event:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update event'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  if (initialLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/events')}>
          Back
        </Button>
        <Typography variant="h4" fontWeight="bold">
          Edit Event
        </Typography>
      </Box>

      <Paper sx={{ p: 3, maxWidth: 800 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
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

            <Grid item xs={12}>
              <Alert severity="info">
                <strong>Note:</strong> Updating this event will immediately reflect on resident views.
              </Alert>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => navigate('/events')} disabled={loading}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" startIcon={<SaveIcon />} disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  )
}

export default EditEvent
