import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box, Container, Typography, Paper, Chip, Button, CircularProgress, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Tabs, Tab,
  IconButton, Tooltip, Divider, Stack,
} from '@mui/material'
import QrCode2Icon from '@mui/icons-material/QrCode2'
import QrCodeScannerIcon from '@mui/icons-material/QrCodeScanner'
import LoginIcon from '@mui/icons-material/Login'
import LogoutIcon from '@mui/icons-material/Logout'
import CancelIcon from '@mui/icons-material/Cancel'
import RefreshIcon from '@mui/icons-material/Refresh'
import EventSeatIcon from '@mui/icons-material/EventSeat'
import { toast } from 'react-toastify'
import { format, isToday, isFuture, isPast, parseISO } from 'date-fns'
import QRCode from 'react-qr-code'
import assetService from '../../api/assetService'
import { ASSET_TYPES, BOOKING_STATUS } from '../../constants/assets'

const TAB_FILTERS = ['upcoming', 'past', 'cancelled']

const MyBookings = () => {
  const navigate = useNavigate()
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState(0)
  const [processing, setProcessing] = useState(null)

  // cancel dialog
  const [cancelDialog, setCancelDialog] = useState({ open: false, booking: null })
  const [cancelReason, setCancelReason] = useState('')

  // QR dialog
  const [qrDialog, setQrDialog] = useState({ open: false, booking: null, qrData: null })
  const [qrLoading, setQrLoading] = useState(false)

  const fetchBookings = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await assetService.getMyBookings({ limit: 200 })
      setBookings(res.data || [])
    } catch {
      setError('Failed to load bookings.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchBookings() }, [fetchBookings])

  const filteredBookings = bookings.filter((b) => {
    if (tab === 0) return b.status === 'pending' || b.status === 'confirmed'
    if (tab === 1) return b.status === 'completed' || b.status === 'no_show'
    if (tab === 2) return b.status === 'cancelled'
    return true
  })

  const handleCheckIn = async (bookingId) => {
    try {
      setProcessing(bookingId + '_checkin')
      await assetService.checkIn(bookingId)
      toast.success('Checked in successfully!')
      fetchBookings()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Check-in failed')
    } finally {
      setProcessing(null)
    }
  }

  const handleCheckOut = async (bookingId) => {
    try {
      setProcessing(bookingId + '_checkout')
      await assetService.checkOut(bookingId)
      toast.success('Checked out successfully!')
      fetchBookings()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Check-out failed')
    } finally {
      setProcessing(null)
    }
  }

  const handleCancel = async () => {
    if (!cancelDialog.booking) return
    try {
      setProcessing(cancelDialog.booking.id + '_cancel')
      await assetService.cancelBooking(cancelDialog.booking.id, cancelReason)
      toast.success('Booking cancelled')
      setCancelDialog({ open: false, booking: null })
      setCancelReason('')
      fetchBookings()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Cancellation failed')
    } finally {
      setProcessing(null)
    }
  }

  const handleShowQR = async (booking) => {
    try {
      setQrLoading(true)
      setQrDialog({ open: true, booking, qrData: null })
      const res = await assetService.getQRCode(booking.asset_id)
      setQrDialog((prev) => ({ ...prev, qrData: res.data.qr_code_data }))
    } catch {
      toast.error('Failed to load QR code')
      setQrDialog({ open: false, booking: null, qrData: null })
    } finally {
      setQrLoading(false)
    }
  }

  const fmtDate = (d) => {
    try { return format(parseISO(d), 'dd MMM yyyy') } catch { return d }
  }
  const fmtTime = (t) => {
    if (!t) return ''
    const [h, m] = t.split(':')
    const dt = new Date(); dt.setHours(+h, +m)
    return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  const canCheckIn  = (b) => (b.status === 'confirmed') && (isToday(parseISO(b.booking_date)) || isFuture(parseISO(b.booking_date))) && !b.checked_in_at
  const canCheckOut = (b) => b.status === 'confirmed' && b.checked_in_at && !b.checked_out_at
  const canCancel   = (b) => b.status === 'pending' || b.status === 'confirmed'

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={700}>My Bookings</Typography>
          <Typography variant="body2" color="text.secondary">
            Manage your facility reservations
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchBookings} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<QrCodeScannerIcon />}
            size="small"
            onClick={() => navigate('/assets/scan')}
          >
            Scan QR
          </Button>
          <Button
            variant="contained"
            startIcon={<EventSeatIcon />}
            size="small"
            onClick={() => navigate('/assets')}
          >
            Book a Facility
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label={`Upcoming (${bookings.filter(b => b.status === 'pending' || b.status === 'confirmed').length})`} />
          <Tab label={`Past (${bookings.filter(b => b.status === 'completed' || b.status === 'no_show').length})`} />
          <Tab label={`Cancelled (${bookings.filter(b => b.status === 'cancelled').length})`} />
        </Tabs>
      </Box>

      {filteredBookings.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <EventSeatIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
          <Typography variant="h6" color="text.secondary">No bookings found</Typography>
          {tab === 0 && (
            <Button variant="outlined" onClick={() => navigate('/assets')} sx={{ mt: 2 }}>
              Browse Facilities
            </Button>
          )}
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead sx={{ bgcolor: 'grey.50' }}>
              <TableRow>
                <TableCell><strong>Facility</strong></TableCell>
                <TableCell><strong>Date</strong></TableCell>
                <TableCell><strong>Time</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Amount</strong></TableCell>
                <TableCell align="center"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredBookings.map((b) => {
                const typeInfo = b.asset ? (ASSET_TYPES[b.asset.asset_type] || ASSET_TYPES.other) : ASSET_TYPES.other
                const statusCfg = BOOKING_STATUS[b.status] || { label: b.status, color: 'default' }
                const isProcessing = processing?.startsWith(b.id)

                return (
                  <TableRow key={b.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography fontSize={20}>{typeInfo.icon}</Typography>
                        <Box>
                          <Typography variant="body2" fontWeight={600}>
                            {b.asset?.name || '—'}
                          </Typography>
                          {b.asset?.location && (
                            <Typography variant="caption" color="text.secondary">
                              {b.asset.location}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{fmtDate(b.booking_date)}</Typography>
                      {isToday(parseISO(b.booking_date)) && (
                        <Chip label="Today" size="small" color="primary" sx={{ mt: 0.5 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {fmtTime(b.start_time)} – {fmtTime(b.end_time)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {b.duration_minutes} min
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={statusCfg.label} color={statusCfg.color} size="small" />
                      {b.checked_in_at && !b.checked_out_at && (
                        <Chip label="Checked In" color="info" size="small" sx={{ ml: 0.5 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {Number(b.payment_amount) > 0 ? `₹${b.payment_amount}` : 'Free'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Stack direction="row" spacing={0.5} justifyContent="center">
                        {/* QR code – for upcoming confirmed */}
                        {b.status === 'confirmed' && (
                          <Tooltip title="Show QR Code">
                            <IconButton
                              size="small"
                              onClick={() => handleShowQR(b)}
                              color="primary"
                            >
                              <QrCode2Icon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}

                        {/* Check-in */}
                        {canCheckIn(b) && (
                          <Tooltip title="Check In">
                            <span>
                              <IconButton
                                size="small"
                                color="success"
                                disabled={isProcessing}
                                onClick={() => handleCheckIn(b.id)}
                              >
                                {isProcessing ? <CircularProgress size={16} /> : <LoginIcon fontSize="small" />}
                              </IconButton>
                            </span>
                          </Tooltip>
                        )}

                        {/* Check-out */}
                        {canCheckOut(b) && (
                          <Tooltip title="Check Out">
                            <span>
                              <IconButton
                                size="small"
                                color="warning"
                                disabled={isProcessing}
                                onClick={() => handleCheckOut(b.id)}
                              >
                                {isProcessing ? <CircularProgress size={16} /> : <LogoutIcon fontSize="small" />}
                              </IconButton>
                            </span>
                          </Tooltip>
                        )}

                        {/* Cancel */}
                        {canCancel(b) && (
                          <Tooltip title="Cancel Booking">
                            <span>
                              <IconButton
                                size="small"
                                color="error"
                                disabled={isProcessing}
                                onClick={() => { setCancelDialog({ open: true, booking: b }); setCancelReason('') }}
                              >
                                <CancelIcon fontSize="small" />
                              </IconButton>
                            </span>
                          </Tooltip>
                        )}
                      </Stack>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Cancel Confirmation Dialog */}
      <Dialog open={cancelDialog.open} onClose={() => setCancelDialog({ open: false, booking: null })} maxWidth="xs" fullWidth>
        <DialogTitle>Cancel Booking</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Cancel your booking for <strong>{cancelDialog.booking?.asset?.name}</strong> on{' '}
            {cancelDialog.booking && fmtDate(cancelDialog.booking.booking_date)}?
          </Typography>
          <TextField
            label="Reason (optional)"
            value={cancelReason}
            onChange={(e) => setCancelReason(e.target.value)}
            fullWidth
            size="small"
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialog({ open: false, booking: null })}>Keep Booking</Button>
          <Button variant="contained" color="error" onClick={handleCancel} disabled={!!processing}>
            {processing ? <CircularProgress size={20} /> : 'Cancel Booking'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* QR Code Dialog */}
      <Dialog open={qrDialog.open} onClose={() => setQrDialog({ open: false, booking: null, qrData: null })} maxWidth="xs" fullWidth>
        <DialogTitle>
          Facility Access QR Code
        </DialogTitle>
        <DialogContent sx={{ textAlign: 'center', py: 3 }}>
          {qrLoading ? (
            <CircularProgress />
          ) : qrDialog.qrData ? (
            <>
              <Box display="inline-block" p={2} bgcolor="#fff" borderRadius={2} border="1px solid #ddd">
                <QRCode value={qrDialog.qrData} size={200} />
              </Box>
              <Typography variant="body2" color="text.secondary" mt={2}>
                Show this QR code at the facility entrance
              </Typography>
              <Divider sx={{ my: 1.5 }} />
              <Typography variant="subtitle2" fontWeight={600}>
                {qrDialog.booking?.asset?.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {qrDialog.booking && fmtDate(qrDialog.booking.booking_date)} •{' '}
                {qrDialog.booking && fmtTime(qrDialog.booking.start_time)} – {qrDialog.booking && fmtTime(qrDialog.booking.end_time)}
              </Typography>
            </>
          ) : (
            <Typography color="text.secondary">QR code unavailable</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQrDialog({ open: false, booking: null, qrData: null })}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default MyBookings
