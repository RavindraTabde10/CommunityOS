import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Container, Typography, Grid, Paper, Button, Chip, CircularProgress,
  Alert, Divider, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, Select, FormControl, InputLabel, Tooltip, Stack,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import PeopleIcon from '@mui/icons-material/People'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import EventSeatIcon from '@mui/icons-material/EventSeat'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import InfoIcon from '@mui/icons-material/Info'
import { toast } from 'react-toastify'
import { format, addDays } from 'date-fns'
import assetService from '../../api/assetService'
import { ASSET_TYPES, BOOKING_STATUS } from '../../constants/assets'

const AssetDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()

  const [asset, setAsset] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // booking dialog state
  const [bookingOpen, setBookingOpen] = useState(false)
  const [bookingForm, setBookingForm] = useState({
    booking_date: format(addDays(new Date(), 1), 'yyyy-MM-dd'),
    start_time: '09:00',
    end_time: '10:00',
    purpose: '',
    number_of_guests: 1,
  })
  const [availability, setAvailability] = useState(null)
  const [checkingAvail, setCheckingAvail] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchAsset()
  }, [id])

  const fetchAsset = async () => {
    try {
      setLoading(true)
      const res = await assetService.getAsset(id)
      setAsset(res.data)
    } catch {
      setError('Failed to load facility details.')
    } finally {
      setLoading(false)
    }
  }

  const fmtTime = (t) => {
    if (!t) return null
    const [h, m] = t.split(':')
    const d = new Date(); d.setHours(+h, +m)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const handleFieldChange = (field, value) => {
    setBookingForm((prev) => ({ ...prev, [field]: value }))
    setAvailability(null)
  }

  const checkAvailability = useCallback(async () => {
    if (!bookingForm.booking_date || !bookingForm.start_time || !bookingForm.end_time) return
    try {
      setCheckingAvail(true)
      const res = await assetService.checkAvailability(
        id,
        bookingForm.booking_date,
        bookingForm.start_time,
        bookingForm.end_time,
        Number(bookingForm.number_of_guests) || 1,
      )
      setAvailability(res.data)
    } catch {
      setAvailability(null)
      toast.error('Could not check availability')
    } finally {
      setCheckingAvail(false)
    }
  }, [id, bookingForm.booking_date, bookingForm.start_time, bookingForm.end_time, bookingForm.number_of_guests])

  const handleBook = async () => {
    try {
      setSubmitting(true)
      await assetService.createBooking({
        asset_id: id,
        booking_date: bookingForm.booking_date,
        start_time: bookingForm.start_time + ':00',
        end_time:   bookingForm.end_time   + ':00',
        purpose:    bookingForm.purpose    || undefined,
        number_of_guests: Number(bookingForm.number_of_guests),
      })
      toast.success('Booking created successfully!')
      setBookingOpen(false)
      navigate('/bookings')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to create booking'
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    )
  }

  if (error || !asset) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Asset not found'}</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/assets')} sx={{ mt: 2 }}>
          Back to Facilities
        </Button>
      </Container>
    )
  }

  const typeInfo = ASSET_TYPES[asset.asset_type] || ASSET_TYPES.other

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      {/* Back nav */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/assets')}
        sx={{ mb: 2 }}
        size="small"
      >
        All Facilities
      </Button>

      {/* Hero banner */}
      <Box
        sx={{
          bgcolor: typeInfo.color,
          borderRadius: 2,
          p: 3,
          mb: 3,
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Typography fontSize={48}>{typeInfo.icon}</Typography>
        <Box>
          <Typography variant="h5" fontWeight={700}>
            {asset.name}
          </Typography>
          <Chip
            label={typeInfo.label}
            size="small"
            sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: '#fff', fontWeight: 600, mt: 0.5 }}
          />
          {!asset.is_active && (
            <Chip label="Inactive" size="small" color="error" sx={{ ml: 1 }} />
          )}
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Left column – details */}
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Facility Details
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {asset.description && (
              <Typography variant="body2" color="text.secondary" mb={2}>
                {asset.description}
              </Typography>
            )}

            <Stack spacing={1.5}>
              {asset.location && (
                <Box display="flex" alignItems="center" gap={1}>
                  <LocationOnIcon color="action" fontSize="small" />
                  <Typography variant="body2"><strong>Location:</strong> {asset.location}</Typography>
                </Box>
              )}
              {asset.capacity && (
                <Box display="flex" alignItems="center" gap={1}>
                  <PeopleIcon color="action" fontSize="small" />
                  <Typography variant="body2"><strong>Capacity:</strong> {asset.capacity} people</Typography>
                </Box>
              )}
              {asset.operating_hours_start && asset.operating_hours_end && (
                <Box display="flex" alignItems="center" gap={1}>
                  <AccessTimeIcon color="action" fontSize="small" />
                  <Typography variant="body2">
                    <strong>Hours:</strong> {fmtTime(asset.operating_hours_start)} – {fmtTime(asset.operating_hours_end)}
                  </Typography>
                </Box>
              )}
              {Number(asset.hourly_rate) > 0 && (
                <Box display="flex" alignItems="center" gap={1}>
                  <AttachMoneyIcon color="action" fontSize="small" />
                  <Typography variant="body2"><strong>Rate:</strong> ₹{asset.hourly_rate} / hour</Typography>
                </Box>
              )}
              {Number(asset.hourly_rate) === 0 && (
                <Box display="flex" alignItems="center" gap={1}>
                  <AttachMoneyIcon color="action" fontSize="small" />
                  <Typography variant="body2"><strong>Rate:</strong> Free</Typography>
                </Box>
              )}
            </Stack>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Booking Rules
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="caption" color="text.secondary">
                • Min duration: {asset.min_booking_duration} min
              </Typography>
              <Typography variant="caption" color="text.secondary">
                • Max duration: {asset.max_booking_duration} min
              </Typography>
              <Typography variant="caption" color="text.secondary">
                • Book up to {asset.advance_booking_days} days in advance
              </Typography>
            </Stack>
          </Paper>
        </Grid>

        {/* Right column – booking CTA */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            {asset.is_bookable && asset.is_active ? (
              <>
                <CalendarTodayIcon sx={{ fontSize: 48, color: typeInfo.color, mb: 1 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Book This Facility
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Reserve your slot by picking a date and time
                </Typography>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  startIcon={<EventSeatIcon />}
                  onClick={() => setBookingOpen(true)}
                  sx={{ bgcolor: typeInfo.color, '&:hover': { bgcolor: typeInfo.color + 'dd' } }}
                >
                  Make a Booking
                </Button>

                <Button
                  variant="outlined"
                  size="small"
                  fullWidth
                  sx={{ mt: 1.5 }}
                  onClick={() => navigate('/bookings')}
                >
                  My Bookings
                </Button>
              </>
            ) : (
              <Box>
                <InfoIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                <Typography variant="body1" color="text.secondary">
                  This facility is currently not available for booking.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* ── Booking Dialog ─────────────────────────────────────────────────── */}
      <Dialog open={bookingOpen} onClose={() => setBookingOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          Book {asset.name}
        </DialogTitle>
        <DialogContent sx={{ pt: 2.5 }}>
          <Stack spacing={2.5} mt={0.5}>
            {/* Date */}
            <TextField
              label="Booking Date"
              type="date"
              value={bookingForm.booking_date}
              onChange={(e) => handleFieldChange('booking_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
              inputProps={{
                min: format(addDays(new Date(), 1), 'yyyy-MM-dd'),
                max: format(addDays(new Date(), asset.advance_booking_days || 30), 'yyyy-MM-dd'),
              }}
              fullWidth
              size="small"
            />

            {/* Start / End */}
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Start Time"
                  type="time"
                  value={bookingForm.start_time}
                  onChange={(e) => handleFieldChange('start_time', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="End Time"
                  type="time"
                  value={bookingForm.end_time}
                  onChange={(e) => handleFieldChange('end_time', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                  size="small"
                />
              </Grid>
            </Grid>

            {/* Check availability button */}
            <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
              <Button
                variant="outlined"
                size="small"
                onClick={checkAvailability}
                disabled={checkingAvail}
              >
                {checkingAvail ? <CircularProgress size={16} /> : 'Check Availability'}
              </Button>
              {availability !== null && (
                <Chip
                  icon={availability.is_available ? <CheckCircleIcon /> : <InfoIcon />}
                  label={
                    availability.is_available
                      ? availability.remaining_capacity !== null && availability.remaining_capacity !== undefined
                        ? `Available – ${availability.remaining_capacity} spot(s) left`
                        : 'Available'
                      : availability.remaining_capacity === 0
                        ? 'Capacity full – try another slot'
                        : 'Slot unavailable'
                  }
                  color={availability.is_available ? 'success' : 'error'}
                  size="small"
                />
              )}
            </Box>

            {/* Guests */}
            <TextField
              label="Number of Guests"
              type="number"
              value={bookingForm.number_of_guests}
              onChange={(e) => handleFieldChange('number_of_guests', e.target.value)}
              inputProps={{ min: 1, max: asset.capacity || 100 }}
              fullWidth
              size="small"
            />

            {/* Purpose */}
            <TextField
              label="Purpose (optional)"
              multiline
              rows={2}
              value={bookingForm.purpose}
              onChange={(e) => handleFieldChange('purpose', e.target.value)}
              fullWidth
              size="small"
              inputProps={{ maxLength: 500 }}
            />

            {/* Cost estimate */}
            {Number(asset.hourly_rate) > 0 && bookingForm.start_time && bookingForm.end_time && (() => {
              const [sh, sm] = bookingForm.start_time.split(':').map(Number)
              const [eh, em] = bookingForm.end_time.split(':').map(Number)
              const mins = (eh * 60 + em) - (sh * 60 + sm)
              if (mins > 0) {
                const cost = ((mins / 60) * Number(asset.hourly_rate)).toFixed(2)
                return (
                  <Alert severity="info" icon={<AttachMoneyIcon />}>
                    Estimated cost: <strong>₹{cost}</strong> ({mins} min × ₹{asset.hourly_rate}/hr)
                  </Alert>
                )
              }
              return null
            })()}
          </Stack>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid', borderColor: 'divider', px: 3, py: 2 }}>
          <Button onClick={() => setBookingOpen(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleBook}
            disabled={submitting || (availability !== null && !availability.is_available)}
            sx={{ bgcolor: typeInfo.color, '&:hover': { bgcolor: typeInfo.color + 'dd' } }}
          >
            {submitting ? <CircularProgress size={20} /> : 'Confirm Booking'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default AssetDetail
