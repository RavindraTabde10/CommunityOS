/**
 * Events Page
 * Lists all events with admin controls
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import { eventsAPI } from '../api/events'
import { USER_ROLES } from '../constants/roles'

const EVENT_TYPE_CONFIG = {
  MEETING: { color: '#1976d2', label: 'Meeting', icon: '📋' },
  FESTIVAL: { color: '#9c27b0', label: 'Festival', icon: '🎉' },
  MAINTENANCE: { color: '#ff9800', label: 'Maintenance', icon: '🔧' },
  SOCIAL: { color: '#4caf50', label: 'Social', icon: '🎊' },
  SPORTS: { color: '#009688', label: 'Sports', icon: '⚽' },
  OTHER: { color: '#757575', label: 'Other', icon: '📅' }
}

const Events = () => {
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)
  const isAdmin = user?.role === USER_ROLES.ADMIN

  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, eventId: null })

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await eventsAPI.getAll({ include_past: true, limit: 100 })
      setEvents(response.data.events || [])
    } catch (err) {
      console.error('Error fetching events:', err)
      setError('Failed to load events')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (eventId) => {
    try {
      await eventsAPI.delete(eventId)
      toast.success('Event deleted successfully')
      setDeleteDialog({ open: false, eventId: null })
      fetchEvents()
    } catch (err) {
      console.error('Error deleting event:', err)
      toast.error(err.response?.data?.detail || 'Failed to delete event')
    }
  }

  const formatDateTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const getEventTypeConfig = (type) => {
    return EVENT_TYPE_CONFIG[type] || EVENT_TYPE_CONFIG.OTHER
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Events
        </Typography>
        {isAdmin && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/events/create')}
          >
            Create Event
          </Button>
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Events Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: 'grey.100' }}>
              <TableCell><strong>Title</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Date & Time</strong></TableCell>
              <TableCell><strong>Venue</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              {isAdmin && <TableCell align="right"><strong>Actions</strong></TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {events.length === 0 ? (
              <TableRow>
                <TableCell colSpan={isAdmin ? 6 : 5} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No events found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              events.map((event) => {
                const typeConfig = getEventTypeConfig(event.event_type)
                const isPast = new Date(event.start_datetime) < new Date()
                
                return (
                  <TableRow key={event.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <span>{typeConfig.icon}</span>
                        <Typography variant="body2" fontWeight="medium">
                          {event.title}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={typeConfig.label}
                        size="small"
                        sx={{ bgcolor: typeConfig.color, color: 'white' }}
                      />
                    </TableCell>
                    <TableCell>{formatDateTime(event.start_datetime)}</TableCell>
                    <TableCell>{event.venue || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={event.is_active ? (isPast ? 'Completed' : 'Active') : 'Cancelled'}
                        size="small"
                        color={event.is_active ? (isPast ? 'default' : 'success') : 'error'}
                      />
                    </TableCell>
                    {isAdmin && (
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/events/${event.id}`)}
                          title="View Details"
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/events/${event.id}/edit`)}
                          title="Edit Event"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => setDeleteDialog({ open: true, eventId: event.id })}
                          title="Delete Event"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    )}
                  </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, eventId: null })}
      >
        <DialogTitle>Delete Event</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this event? This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, eventId: null })}>
            Cancel
          </Button>
          <Button
            onClick={() => handleDelete(deleteDialog.eventId)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Events
