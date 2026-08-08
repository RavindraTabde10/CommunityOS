/**
 * UpcomingEvents Component
 * Displays next upcoming community events on the dashboard
 */
import { useState, useEffect } from 'react'
import {
  Paper,
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Skeleton,
  Alert
} from '@mui/material'
import {
  Event as EventIcon,
  LocationOn as LocationIcon,
  AccessTime as TimeIcon,
  ChevronRight as ChevronRightIcon
} from '@mui/icons-material'
import { eventsAPI } from '../../api/events'

// Event type colors
const EVENT_TYPE_CONFIG = {
  MEETING: { color: '#1976d2', label: 'Meeting', icon: '📋' },
  FESTIVAL: { color: '#9c27b0', label: 'Festival', icon: '🎉' },
  MAINTENANCE: { color: '#ff9800', label: 'Maintenance', icon: '🔧' },
  SOCIAL: { color: '#4caf50', label: 'Social', icon: '🎊' },
  SPORTS: { color: '#009688', label: 'Sports', icon: '⚽' },
  OTHER: { color: '#757575', label: 'Other', icon: '📅' }
}

const UpcomingEvents = () => {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔍 Fetching events from API...')
      
      // Check if user is logged in
      const token = localStorage.getItem('access_token')
      console.log('🔑 Auth token:', token ? 'Present' : 'Missing')
      
      const response = await eventsAPI.getUpcoming(3)
      console.log('✅ Events API response:', response)
      
      // Handle response - it might be response.data or just response
      const eventsData = response.data || response || []
      console.log('📊 Events data:', eventsData)
      
      setEvents(Array.isArray(eventsData) ? eventsData : [])
    } catch (err) {
      console.error('❌ Error fetching events:', err)
      console.error('Error name:', err.name)
      console.error('Error message:', err.message)
      console.error('Error response:', err.response?.data)
      console.error('Error status:', err.response?.status)
      
      // Provide more specific error messages
      let errorMessage = 'Failed to load events'
      if (err.message === 'Network Error') {
        errorMessage = 'Cannot connect to server. Please check if backend is running.'
      } else if (err.response?.status === 401) {
        errorMessage = 'Authentication required. Please log in again.'
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (dateString) => {
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        return { date: 'Invalid date', time: '' }
      }
      return {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        time: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
      }
    } catch {
      return { date: 'Invalid date', time: '' }
    }
  }

  const getEventConfig = (eventType) => {
    return EVENT_TYPE_CONFIG[eventType] || EVENT_TYPE_CONFIG.OTHER
  }

  return (
    <Paper
      elevation={3}
      sx={{
        p: 1.5,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <EventIcon sx={{ fontSize: 20, color: 'primary.main' }} />
          <Typography variant="body1" fontWeight="bold">
            Upcoming Events
          </Typography>
        </Box>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {loading ? (
          <>
            {[1, 2, 3].map((n) => (
              <Skeleton key={n} variant="rectangular" height={80} sx={{ borderRadius: 2, mb: 1 }} />
            ))}
          </>
        ) : error ? (
          <Alert severity="error" sx={{ fontSize: '0.85rem' }}>
            {error}
          </Alert>
        ) : events.length === 0 ? (
          <Box
            sx={{
              textAlign: 'center',
              py: 3,
              color: 'text.secondary'
            }}
          >
            <EventIcon sx={{ fontSize: 48, opacity: 0.3, mb: 1 }} />
            <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
              No upcoming events
            </Typography>
          </Box>
        ) : (
          events.map((event) => {
            const config = getEventConfig(event.event_type)
            const { date, time } = formatDateTime(event.start_datetime)

            return (
              <Card
                key={event.id}
                sx={{
                  mb: 1,
                  '&:last-child': { mb: 0 },
                  borderLeft: 4,
                  borderColor: config.color,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    transform: 'translateX(4px)',
                    boxShadow: 2
                  }
                }}
              >
                <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                  {/* Event type badge */}
                  <Chip
                    label={`${config.icon} ${config.label}`}
                    size="small"
                    sx={{
                      height: 18,
                      fontSize: '0.65rem',
                      fontWeight: 'bold',
                      bgcolor: `${config.color}20`,
                      color: config.color,
                      mb: 0.5
                    }}
                  />

                  {/* Event title */}
                  <Typography
                    variant="body2"
                    fontWeight="bold"
                    sx={{
                      mb: 0.5,
                      fontSize: '0.9rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}
                  >
                    {event.title}
                  </Typography>

                  {/* Event details */}
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <TimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                        {date} at {time}
                      </Typography>
                    </Box>
                    {event.venue && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <LocationIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                          {event.venue}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            )
          })
        )}
      </Box>
    </Paper>
  )
}

export default UpcomingEvents
