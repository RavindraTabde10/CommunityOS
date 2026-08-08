import { useState, useEffect, useCallback } from 'react'
import {
  Box, Container, Typography, Paper, Button, Chip, CircularProgress, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Select, MenuItem, FormControl, InputLabel, Switch, FormControlLabel,
  IconButton, Tooltip, Grid, Divider, Stack,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import QrCode2Icon from '@mui/icons-material/QrCode2'
import RefreshIcon from '@mui/icons-material/Refresh'
import BarChartIcon from '@mui/icons-material/BarChart'
import { toast } from 'react-toastify'
import QRCode from 'react-qr-code'
import assetService from '../../api/assetService'
import { ASSET_TYPES, ASSET_TYPE_OPTIONS } from '../../constants/assets'

const EMPTY_FORM = {
  name: '',
  asset_type: 'gym',
  description: '',
  location: '',
  capacity: '',
  hourly_rate: '0',
  max_guests_per_booking: '',
  is_bookable: true,
  is_active: true,
  advance_booking_days: 30,
  min_booking_duration: 60,
  max_booking_duration: 240,
  operating_hours_start: '06:00',
  operating_hours_end: '22:00',
}

const AssetManagement = () => {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [processing, setProcessing] = useState(null)

  // Create / Edit dialog
  const [formDialog, setFormDialog] = useState({ open: false, editAsset: null })
  const [form, setForm] = useState(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)

  // Stats dialog
  const [statsDialog, setStatsDialog] = useState({ open: false, stats: null, assetName: '' })
  const [statsLoading, setStatsLoading] = useState(false)

  // QR dialog
  const [qrDialog, setQrDialog] = useState({ open: false, qrData: null, assetName: '' })
  const [qrLoading, setQrLoading] = useState(false)

  const fetchAssets = useCallback(async () => {
    try {
      setLoading(true)
      const res = await assetService.getAssets({ limit: 200 })
      setAssets(res.data || [])
    } catch {
      setError('Failed to load assets.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchAssets() }, [fetchAssets])

  // ── Form helpers ─────────────────────────────────────────────────────────
  const openCreate = () => {
    setForm(EMPTY_FORM)
    setFormDialog({ open: true, editAsset: null })
  }

  const openEdit = (asset) => {
    setForm({
      name: asset.name || '',
      asset_type: asset.asset_type || 'gym',
      description: asset.description || '',
      location: asset.location || '',
      capacity: asset.capacity ?? '',
      hourly_rate: asset.hourly_rate ?? '0',
      max_guests_per_booking: asset.max_guests_per_booking ?? '',
      is_bookable: asset.is_bookable ?? true,
      is_active: asset.is_active ?? true,
      advance_booking_days: asset.advance_booking_days ?? 30,
      min_booking_duration: asset.min_booking_duration ?? 60,
      max_booking_duration: asset.max_booking_duration ?? 240,
      operating_hours_start: asset.operating_hours_start?.slice(0, 5) || '06:00',
      operating_hours_end:   asset.operating_hours_end?.slice(0, 5)   || '22:00',
    })
    setFormDialog({ open: true, editAsset: asset })
  }

  const handleFormChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    if (!form.name.trim()) { toast.error('Name is required'); return }
    try {
      setSubmitting(true)
      const payload = {
        ...form,
        capacity:               form.capacity               ? Number(form.capacity)               : null,
        hourly_rate:            form.hourly_rate            ? Number(form.hourly_rate)            : 0,
        max_guests_per_booking: form.max_guests_per_booking ? Number(form.max_guests_per_booking) : null,
        advance_booking_days:  Number(form.advance_booking_days),
        min_booking_duration:  Number(form.min_booking_duration),
        max_booking_duration:  Number(form.max_booking_duration),
        operating_hours_start: form.operating_hours_start ? form.operating_hours_start + ':00' : null,
        operating_hours_end:   form.operating_hours_end   ? form.operating_hours_end   + ':00' : null,
      }

      if (formDialog.editAsset) {
        await assetService.updateAsset(formDialog.editAsset.id, payload)
        toast.success('Asset updated')
      } else {
        await assetService.createAsset(payload)
        toast.success('Asset created')
      }
      setFormDialog({ open: false, editAsset: null })
      fetchAssets()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Save failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleToggleActive = async (asset) => {
    try {
      setProcessing(asset.id)
      await assetService.updateAsset(asset.id, { is_active: !asset.is_active })
      toast.success(asset.is_active ? 'Asset deactivated' : 'Asset activated')
      fetchAssets()
    } catch {
      toast.error('Failed to update asset status')
    } finally {
      setProcessing(null)
    }
  }

  const handleShowStats = async (asset) => {
    try {
      setStatsLoading(true)
      setStatsDialog({ open: true, stats: null, assetName: asset.name })
      const res = await assetService.getAssetStats(asset.id)
      setStatsDialog((prev) => ({ ...prev, stats: res.data }))
    } catch {
      toast.error('Failed to load stats')
      setStatsDialog({ open: false, stats: null, assetName: '' })
    } finally {
      setStatsLoading(false)
    }
  }

  const handleShowQR = async (asset) => {
    try {
      setQrLoading(true)
      setQrDialog({ open: true, qrData: null, assetName: asset.name })
      const res = await assetService.getQRCode(asset.id)
      setQrDialog((prev) => ({ ...prev, qrData: res.data.qr_code_data }))
    } catch {
      toast.error('Failed to generate QR code')
      setQrDialog({ open: false, qrData: null, assetName: '' })
    } finally {
      setQrLoading(false)
    }
  }

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
          <Typography variant="h5" fontWeight={700}>Asset Management</Typography>
          <Typography variant="body2" color="text.secondary">
            Manage community facilities and booking rules
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton size="small" onClick={fetchAssets}><RefreshIcon /></IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            Add Asset
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'grey.50' }}>
            <TableRow>
              <TableCell><strong>Asset</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Location</strong></TableCell>
              <TableCell><strong>Rate</strong></TableCell>
              <TableCell><strong>Bookable</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell align="center"><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {assets.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary" py={2}>
                    No assets yet. Click "Add Asset" to create one.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {assets.map((a) => {
              const typeInfo = ASSET_TYPES[a.asset_type] || ASSET_TYPES.other
              return (
                <TableRow key={a.id} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography fontSize={20}>{typeInfo.icon}</Typography>
                      <Typography variant="body2" fontWeight={600}>{a.name}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={typeInfo.label}
                      size="small"
                      sx={{ bgcolor: typeInfo.color + '22', color: typeInfo.color, fontWeight: 600, fontSize: 11 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{a.location || '—'}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {Number(a.hourly_rate) > 0 ? `₹${a.hourly_rate}/hr` : 'Free'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={a.is_bookable ? 'Yes' : 'No'}
                      color={a.is_bookable ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={a.is_active ? 'Active' : 'Inactive'}
                      color={a.is_active ? 'success' : 'error'}
                      size="small"
                      onClick={() => handleToggleActive(a)}
                      disabled={processing === a.id}
                      clickable
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Stack direction="row" spacing={0.5} justifyContent="center">
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => openEdit(a)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="View Stats">
                        <IconButton size="small" color="info" onClick={() => handleShowStats(a)}>
                          <BarChartIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="QR Code">
                        <IconButton size="small" color="primary" onClick={() => handleShowQR(a)}>
                          <QrCode2Icon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* ── Create / Edit Dialog ──────────────────────────────────────────── */}
      <Dialog open={formDialog.open} onClose={() => setFormDialog({ open: false, editAsset: null })} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          {formDialog.editAsset ? 'Edit Asset' : 'Add New Asset'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2.5 }}>
          <Stack spacing={2.5} mt={0.5}>
            <Grid container spacing={2}>
              <Grid item xs={8}>
                <TextField
                  label="Asset Name *"
                  value={form.name}
                  onChange={(e) => handleFormChange('name', e.target.value)}
                  fullWidth size="small"
                  inputProps={{ maxLength: 100 }}
                />
              </Grid>
              <Grid item xs={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Type *</InputLabel>
                  <Select value={form.asset_type} label="Type *" onChange={(e) => handleFormChange('asset_type', e.target.value)}>
                    {ASSET_TYPE_OPTIONS.map((o) => (
                      <MenuItem key={o.value} value={o.value}>
                        {ASSET_TYPES[o.value]?.icon} {o.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => handleFormChange('description', e.target.value)}
              multiline rows={2} fullWidth size="small"
            />

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Location"
                  value={form.location}
                  onChange={(e) => handleFormChange('location', e.target.value)}
                  fullWidth size="small"
                />
              </Grid>
              <Grid item xs={3}>
                <TextField
                  label="Capacity"
                  type="number"
                  value={form.capacity}
                  onChange={(e) => handleFormChange('capacity', e.target.value)}
                  fullWidth size="small"
                  inputProps={{ min: 1 }}
                  helperText="Total per slot"
                />
              </Grid>
              <Grid item xs={3}>
                <TextField
                  label="₹/hour"
                  type="number"
                  value={form.hourly_rate}
                  onChange={(e) => handleFormChange('hourly_rate', e.target.value)}
                  fullWidth size="small"
                  inputProps={{ min: 0, step: '0.01' }}
                />
              </Grid>
            </Grid>

            <TextField
              label="Max guests per booking"
              type="number"
              value={form.max_guests_per_booking}
              onChange={(e) => handleFormChange('max_guests_per_booking', e.target.value)}
              fullWidth size="small"
              inputProps={{ min: 1 }}
              helperText="Limit how many guests one person can book at a time (e.g. 2 for gym). Leave blank for no limit."
            />

            <Divider />
            <Typography variant="subtitle2" fontWeight={600}>Operating Hours</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Opens at"
                  type="time"
                  value={form.operating_hours_start}
                  onChange={(e) => handleFormChange('operating_hours_start', e.target.value)}
                  fullWidth size="small"
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Closes at"
                  type="time"
                  value={form.operating_hours_end}
                  onChange={(e) => handleFormChange('operating_hours_end', e.target.value)}
                  fullWidth size="small"
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>

            <Divider />
            <Typography variant="subtitle2" fontWeight={600}>Booking Rules</Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <TextField
                  label="Advance days"
                  type="number"
                  value={form.advance_booking_days}
                  onChange={(e) => handleFormChange('advance_booking_days', e.target.value)}
                  fullWidth size="small"
                  inputProps={{ min: 1, max: 365 }}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Min (min)"
                  type="number"
                  value={form.min_booking_duration}
                  onChange={(e) => handleFormChange('min_booking_duration', e.target.value)}
                  fullWidth size="small"
                  inputProps={{ min: 15 }}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Max (min)"
                  type="number"
                  value={form.max_booking_duration}
                  onChange={(e) => handleFormChange('max_booking_duration', e.target.value)}
                  fullWidth size="small"
                  inputProps={{ min: 30 }}
                />
              </Grid>
            </Grid>

            <Box display="flex" gap={2}>
              <FormControlLabel
                control={<Switch checked={form.is_bookable} onChange={(e) => handleFormChange('is_bookable', e.target.checked)} />}
                label="Online bookable"
              />
              <FormControlLabel
                control={<Switch checked={form.is_active} onChange={(e) => handleFormChange('is_active', e.target.checked)} />}
                label="Active"
              />
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid', borderColor: 'divider', px: 3, py: 2 }}>
          <Button onClick={() => setFormDialog({ open: false, editAsset: null })} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSubmit} disabled={submitting}>
            {submitting ? <CircularProgress size={20} /> : (formDialog.editAsset ? 'Save Changes' : 'Create Asset')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Stats Dialog ──────────────────────────────────────────────────── */}
      <Dialog open={statsDialog.open} onClose={() => setStatsDialog({ open: false, stats: null, assetName: '' })} maxWidth="xs" fullWidth>
        <DialogTitle>Stats – {statsDialog.assetName}</DialogTitle>
        <DialogContent>
          {statsLoading ? (
            <Box display="flex" justifyContent="center" py={3}><CircularProgress /></Box>
          ) : statsDialog.stats ? (
            <Stack spacing={1} mt={1}>
              {[
                ['Total Bookings',    statsDialog.stats.total_bookings],
                ['Completed',         statsDialog.stats.completed_bookings],
                ['Cancelled',         statsDialog.stats.cancelled_bookings],
                ['Total Revenue',     `₹${statsDialog.stats.total_revenue ?? 0}`],
                ['Avg Duration',      `${Math.round(statsDialog.stats.average_booking_duration ?? 0)} min`],
                ['Occupancy Rate',    `${(statsDialog.stats.occupancy_rate ?? 0).toFixed(1)}%`],
              ].map(([label, value]) => (
                <Box key={label} display="flex" justifyContent="space-between" py={0.5}>
                  <Typography variant="body2" color="text.secondary">{label}</Typography>
                  <Typography variant="body2" fontWeight={600}>{value}</Typography>
                </Box>
              ))}
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatsDialog({ open: false, stats: null, assetName: '' })}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* ── QR Code Dialog ────────────────────────────────────────────────── */}
      <Dialog open={qrDialog.open} onClose={() => setQrDialog({ open: false, qrData: null, assetName: '' })} maxWidth="xs" fullWidth>
        <DialogTitle>QR Code – {qrDialog.assetName}</DialogTitle>
        <DialogContent sx={{ textAlign: 'center', py: 3 }}>
          {qrLoading ? (
            <CircularProgress />
          ) : qrDialog.qrData ? (
            <>
              <Box display="inline-block" p={2} bgcolor="#fff" borderRadius={2} border="1px solid #ddd">
                <QRCode value={qrDialog.qrData} size={200} />
              </Box>
              <Typography variant="caption" display="block" color="text.secondary" mt={1}>
                Place this QR code at the facility entrance for easy check-in
              </Typography>
            </>
          ) : (
            <Typography color="text.secondary">QR code unavailable</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQrDialog({ open: false, qrData: null, assetName: '' })}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default AssetManagement
