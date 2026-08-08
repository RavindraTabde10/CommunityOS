import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box, Container, Typography, Paper, Button, Chip, CircularProgress,
  Alert, Divider, TextField, InputAdornment, IconButton, Stack, Dialog,
  DialogTitle, DialogContent, DialogActions,
} from '@mui/material'
import QrCodeScannerIcon from '@mui/icons-material/QrCodeScanner'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import LoginIcon from '@mui/icons-material/Login'
import LogoutIcon from '@mui/icons-material/Logout'
import RefreshIcon from '@mui/icons-material/Refresh'
import KeyboardIcon from '@mui/icons-material/Keyboard'
import { toast } from 'react-toastify'
import { format, parseISO, isToday } from 'date-fns'
import { Html5Qrcode } from 'html5-qrcode'
import assetService from '../../api/assetService'
import { ASSET_TYPES, BOOKING_STATUS } from '../../constants/assets'

const SCANNER_ID = 'qr-reader-container'

const QRScanner = () => {
  const navigate = useNavigate()
  const html5QrRef = useRef(null)
  const [scanning, setScanning] = useState(false)
  const [cameraError, setCameraError] = useState(null)

  // result state
  const [step, setStep] = useState('idle') // idle | found | no_booking | done | error
  const [asset, setAsset] = useState(null)
  const [booking, setBooking] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [resultError, setResultError] = useState(null)

  // manual input fallback
  const [showManual, setShowManual] = useState(false)
  const [manualValue, setManualValue] = useState('')

  // ── Camera lifecycle ────────────────────────────────────────────────────
  const startScanner = async () => {
    setCameraError(null)
    try {
      const qr = new Html5Qrcode(SCANNER_ID)
      html5QrRef.current = qr
      await qr.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 260, height: 260 } },
        handleScanSuccess,
        () => {} // suppress per-frame decode errors
      )
      setScanning(true)
    } catch (err) {
      setCameraError('Camera access denied or unavailable. Use manual entry below.')
      setShowManual(true)
    }
  }

  const stopScanner = async () => {
    if (html5QrRef.current && scanning) {
      try {
        await html5QrRef.current.stop()
        html5QrRef.current.clear()
      } catch { /* already stopped */ }
      html5QrRef.current = null
      setScanning(false)
    }
  }

  useEffect(() => {
    startScanner()
    return () => { stopScanner() }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Scan handler ────────────────────────────────────────────────────────
  const handleScanSuccess = async (qrData) => {
    if (processing || step !== 'idle') return
    await stopScanner()
    await resolveQR(qrData)
  }

  const resolveQR = async (qrData) => {
    setProcessing(true)
    setResultError(null)
    try {
      // 1. Identify asset from QR data
      const assetRes = await assetService.scanQRCode(qrData)
      const scannedAsset = assetRes.data.asset
      setAsset(scannedAsset)

      // 2. Find today's confirmed booking for this asset by current user
      const bookingsRes = await assetService.getMyBookings({ limit: 50 })
      const all = bookingsRes.data || []
      const todayBooking = all
        .filter(b =>
          b.asset_id === scannedAsset.id &&
          (b.status === 'confirmed' || b.status === 'pending') &&
          isToday(parseISO(b.booking_date))
        )
        // prefer already-checked-in first, then earliest start
        .sort((a, b) => {
          if (a.checked_in_at && !b.checked_in_at) return -1
          if (!a.checked_in_at && b.checked_in_at) return 1
          return a.start_time.localeCompare(b.start_time)
        })[0]

      if (todayBooking) {
        setBooking(todayBooking)
        setStep('found')
      } else {
        setStep('no_booking')
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Invalid QR code or network error'
      setResultError(msg)
      setStep('error')
    } finally {
      setProcessing(false)
    }
  }

  const handleCheckIn = async () => {
    try {
      setProcessing(true)
      await assetService.checkIn(booking.id)
      setBooking((prev) => ({ ...prev, checked_in_at: new Date().toISOString() }))
      setStep('done')
      toast.success('Checked in successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Check-in failed')
    } finally {
      setProcessing(false)
    }
  }

  const handleCheckOut = async () => {
    try {
      setProcessing(true)
      await assetService.checkOut(booking.id)
      setBooking((prev) => ({ ...prev, checked_out_at: new Date().toISOString() }))
      setStep('done')
      toast.success('Checked out successfully!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Check-out failed')
    } finally {
      setProcessing(false)
    }
  }

  const handleReset = async () => {
    setStep('idle')
    setAsset(null)
    setBooking(null)
    setResultError(null)
    setManualValue('')
    await startScanner()
  }

  const fmtTime = (t) => {
    if (!t) return ''
    const [h, m] = t.split(':')
    const d = new Date(); d.setHours(+h, +m)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  // ── Render helpers ───────────────────────────────────────────────────────
  const typeInfo = asset ? (ASSET_TYPES[asset.asset_type] || ASSET_TYPES.other) : null

  const renderResult = () => {
    if (step === 'error') {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {resultError}
        </Alert>
      )
    }

    if (step === 'no_booking') {
      return (
        <Paper sx={{ p: 3, mt: 2, textAlign: 'center', border: '2px solid', borderColor: 'error.light' }}>
          <Typography fontSize={40}>{typeInfo?.icon}</Typography>
          <Typography variant="h6" fontWeight={700} mt={1}>{asset?.name}</Typography>
          <Alert severity="warning" sx={{ mt: 2, textAlign: 'left' }}>
            No active booking found for today. Please make a booking first.
          </Alert>
        </Paper>
      )
    }

    if ((step === 'found' || step === 'done') && asset && booking) {
      const statusCfg = BOOKING_STATUS[booking.status] || { label: booking.status, color: 'default' }
      const alreadyIn  = !!booking.checked_in_at
      const alreadyOut = !!booking.checked_out_at

      return (
        <Paper
          sx={{
            p: 3, mt: 2,
            border: '2px solid',
            borderColor: step === 'done' ? 'success.main' : typeInfo.color,
            borderRadius: 2,
          }}
        >
          {/* Asset header */}
          <Box display="flex" alignItems="center" gap={1.5} mb={2}>
            <Typography fontSize={40}>{typeInfo.icon}</Typography>
            <Box>
              <Typography variant="h6" fontWeight={700}>{asset.name}</Typography>
              {asset.location && (
                <Typography variant="caption" color="text.secondary">{asset.location}</Typography>
              )}
            </Box>
          </Box>

          <Divider sx={{ mb: 2 }} />

          {/* Booking info */}
          <Stack spacing={1} mb={2}>
            {[
              ['Booking Date', format(parseISO(booking.booking_date), 'dd MMM yyyy')],
              ['Time',         `${fmtTime(booking.start_time)} – ${fmtTime(booking.end_time)}`],
              ['Duration',     `${booking.duration_minutes} min`],
              ['Guests',       booking.number_of_guests],
              booking.purpose && ['Purpose', booking.purpose],
            ].filter(Boolean).map(([label, value]) => (
              <Box key={label} display="flex" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">{label}</Typography>
                <Typography variant="body2" fontWeight={600}>{value}</Typography>
              </Box>
            ))}
          </Stack>

          {/* Status badges */}
          <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
            <Chip label={statusCfg.label} color={statusCfg.color} size="small" />
            {alreadyIn && !alreadyOut && (
              <Chip label="Checked In" color="info" size="small" />
            )}
            {alreadyOut && (
              <Chip label="Checked Out" color="success" size="small" />
            )}
          </Box>

          {/* Actions */}
          {step === 'done' ? (
            <Box textAlign="center" py={1}>
              <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main' }} />
              <Typography variant="h6" color="success.main" fontWeight={700}>
                {alreadyOut ? 'Checked Out!' : 'Checked In!'}
              </Typography>
            </Box>
          ) : (
            <Stack spacing={1}>
              {!alreadyIn && (
                <Button
                  variant="contained"
                  color="success"
                  startIcon={processing ? <CircularProgress size={18} color="inherit" /> : <LoginIcon />}
                  onClick={handleCheckIn}
                  disabled={processing}
                  fullWidth
                >
                  Check In
                </Button>
              )}
              {alreadyIn && !alreadyOut && (
                <Button
                  variant="contained"
                  color="warning"
                  startIcon={processing ? <CircularProgress size={18} color="inherit" /> : <LogoutIcon />}
                  onClick={handleCheckOut}
                  disabled={processing}
                  fullWidth
                >
                  Check Out
                </Button>
              )}
              {alreadyOut && (
                <Alert severity="info">Already checked out for this booking.</Alert>
              )}
            </Stack>
          )}
        </Paper>
      )
    }

    return null
  }

  return (
    <Container maxWidth="sm" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={1} mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          size="small"
          onClick={() => navigate('/bookings')}
        >
          My Bookings
        </Button>
      </Box>

      <Typography variant="h5" fontWeight={700} gutterBottom>
        <QrCodeScannerIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Scan QR Code
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Scan the QR code at the facility entrance to check in or out of your booking.
      </Typography>

      {/* Camera error */}
      {cameraError && (
        <Alert severity="warning" sx={{ mb: 2 }}>{cameraError}</Alert>
      )}

      {/* Scanner viewport — always rendered so html5-qrcode can mount into it */}
      <Box
        sx={{
          display: step === 'idle' ? 'block' : 'none',
          borderRadius: 2,
          overflow: 'hidden',
          border: '2px solid',
          borderColor: 'primary.main',
          bgcolor: '#000',
          minHeight: 300,
        }}
      >
        <div id={SCANNER_ID} style={{ width: '100%' }} />
      </Box>

      {/* Loading overlay while resolving QR */}
      {processing && step === 'idle' && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Scan result */}
      {renderResult()}

      {/* Action buttons */}
      <Box display="flex" gap={1} mt={2} flexWrap="wrap">
        {step !== 'idle' && (
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleReset}
            disabled={processing}
          >
            Scan Again
          </Button>
        )}
        <Button
          variant="text"
          startIcon={<KeyboardIcon />}
          onClick={() => setShowManual(true)}
          size="small"
        >
          Enter code manually
        </Button>
      </Box>

      {/* Manual entry dialog */}
      <Dialog open={showManual} onClose={() => setShowManual(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Enter QR Code Manually</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Type or paste the QR code value printed below the code at the facility.
          </Typography>
          <TextField
            autoFocus
            fullWidth
            size="small"
            label="QR Code"
            value={manualValue}
            onChange={(e) => setManualValue(e.target.value)}
            placeholder="asset-xxxxxxxxxxxx"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && manualValue.trim()) {
                setShowManual(false)
                stopScanner()
                resolveQR(manualValue.trim())
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowManual(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!manualValue.trim()}
            onClick={() => {
              setShowManual(false)
              stopScanner()
              resolveQR(manualValue.trim())
            }}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default QRScanner
