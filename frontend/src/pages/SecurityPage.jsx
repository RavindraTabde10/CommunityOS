import { useState, useEffect, useCallback, useRef } from 'react'
import { useSelector } from 'react-redux'
import {
  Container, Typography, Box, Paper, Grid, TextField, Button,
  Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress,
  IconButton, Tooltip, Divider, Alert, InputAdornment, ToggleButtonGroup,
  ToggleButton, Avatar,
} from '@mui/material'
import {
  PersonAdd as PersonAddIcon,
  Refresh as RefreshIcon,
  Logout as CheckOutIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Phone as PhoneIcon,
  Home as HomeIcon,
  DirectionsCar as CarIcon,
  Info as InfoIcon,
  Notes as NotesIcon,
  Security as SecurityIcon,
  Call as CallIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import { format } from 'date-fns'
import visitorService from '../api/visitorService'
import { USER_ROLES } from '../constants/roles'

// ── Translations ────────────────────────────────────────────────────────────
const LANG = {
  en: {
    code: 'EN',
    title: 'Log New Visitor',
    subtitle: 'Fill in visitor details below',
    sectionVisitor: 'Visitor Information',
    sectionVisit: 'Visit Details',
    visitorName: 'Visitor Name',
    visitorNamePlaceholder: 'Enter full name',
    phone: 'Phone Number',
    phonePlaceholder: 'e.g. 9876543210',
    hostUnit: 'Host Unit',
    hostUnitPlaceholder: 'e.g. B6-1801',
    vehicle: 'Vehicle Number',
    vehiclePlaceholder: 'e.g. MH12AB1234',
    purpose: 'Purpose of Visit',
    purposePlaceholder: 'e.g. Delivery, Personal, Work',
    notes: 'Additional Notes',
    notesPlaceholder: 'Any other details…',
    required: 'Required',
    cancel: 'Cancel',
    submit: 'Log Visitor',
  },
  hi: {
    code: 'हिं',
    title: 'नई आगंतुक प्रविष्टि',
    subtitle: 'नीचे आगंतुक की जानकारी भरें',
    sectionVisitor: 'आगंतुक की जानकारी',
    sectionVisit: 'भेट विवरण',
    visitorName: 'आगंतुक का नाम',
    visitorNamePlaceholder: 'पूरा नाम दर्ज करें',
    phone: 'फ़ोन नंबर',
    phonePlaceholder: 'जैसे. 9876543210',
    hostUnit: 'होस्ट यूनिट',
    hostUnitPlaceholder: 'जैसे. B6-1801',
    vehicle: 'वाहन संख्या',
    vehiclePlaceholder: 'जैसे. MH12AB1234',
    purpose: 'आने का उद्देश्य',
    purposePlaceholder: 'जैसे. डिलीवरी, व्यक्तिगत, काम',
    notes: 'अतिरिक्त नोट्स',
    notesPlaceholder: 'कोई अन्य विवरण…',
    required: 'आवश्यक',
    cancel: 'रद्द करें',
    submit: 'प्रविष्टि दर्ज करें',
  },
  mr: {
    code: 'म',
    title: 'नवीन अभ्यागत नोंद',
    subtitle: 'खाली अभ्यागताची माहिती भरा',
    sectionVisitor: 'अभ्यागताची माहिती',
    sectionVisit: 'भेट तपशील',
    visitorName: 'अभ्यागताचे नाव',
    visitorNamePlaceholder: 'पूर्ण नाव लिहा',
    phone: 'फोन नंबर',
    phonePlaceholder: 'उदा. 9876543210',
    hostUnit: 'होस्ट युनिट',
    hostUnitPlaceholder: 'उदा. B6-1801',
    vehicle: 'वाहन क्रमांक',
    vehiclePlaceholder: 'उदा. MH12AB1234',
    purpose: 'भेटीचे कारण',
    purposePlaceholder: 'उदा. डिलिव्हरी, वैयक्तिक, काम',
    notes: 'अतिरिक्त टिपा',
    notesPlaceholder: 'इतर कोणतेही तपशील…',
    required: 'आवश्यक',
    cancel: 'रद्द करा',
    submit: 'नोंद करा',
  },
}

const STATUS_CONFIG = {
  pending:     { label: 'Pending',      color: 'warning' },
  approved:    { label: 'Approved',     color: 'success' },
  denied:      { label: 'Denied',       color: 'error' },
  checked_out: { label: 'Checked Out',  color: 'default' },
}

const EMPTY_FORM = {
  visitor_name: '',
  visitor_phone: '',
  vehicle_number: '',
  purpose: '',
  host_unit: '',
  notes: '',
}

// Labelled field with leading icon
const FormField = ({ icon, label, required, ...props }) => (
  <TextField
    label={required ? `${label} *` : label}
    fullWidth
    size="small"
    InputProps={{
      startAdornment: (
        <InputAdornment position="start">
          <Box sx={{ color: 'primary.main', display: 'flex' }}>{icon}</Box>
        </InputAdornment>
      ),
    }}
    {...props}
  />
)

const SecurityPage = () => {
  const { user } = useSelector((s) => s.auth)
  const canLog = user?.role === USER_ROLES.SECURITY || user?.role === USER_ROLES.ADMIN

  const [visitors, setVisitors] = useState([])
  const [loading, setLoading] = useState(true)
  const [logDialog, setLogDialog] = useState(false)
  const [lang, setLang] = useState('en')
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [viewDialog, setViewDialog] = useState({ open: false, item: null })
  const [editDialog, setEditDialog] = useState({ open: false, item: null })
  const [editForm, setEditForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')
  const [residentInfo, setResidentInfo] = useState(null)   // { name, phone } for form lookup
  const [residentLoading, setResidentLoading] = useState(false)
  const [elapsed, setElapsed] = useState({})               // { [visitor_id]: seconds_elapsed }
  const unitDebounceRef = useRef(null)
  const tickRef = useRef(null)

  const t = LANG[lang]

  const fetchVisitors = useCallback(async () => {
    try {
      setLoading(true)
      const res = await visitorService.getAll()
      setVisitors(res.data || [])
    } catch {
      toast.error('Failed to load visitor log')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchVisitors() }, [fetchVisitors])

  // Tick elapsed seconds for all pending visitors; run once immediately then every second
  useEffect(() => {
    const tick = () => {
      const now = Date.now()
      const next = {}
      visitors.forEach((v) => {
        if (v.status === 'pending') {
          const checkIn = new Date(v.check_in_time.endsWith('Z') ? v.check_in_time : v.check_in_time + 'Z').getTime()
          next[v.id] = Math.floor((now - checkIn) / 1000)
        }
      })
      setElapsed(next)
    }
    tick()
    tickRef.current = setInterval(tick, 1000)
    return () => clearInterval(tickRef.current)
  }, [visitors])

  // Debounced resident lookup when host_unit changes in the form
  const lookupResident = (unit) => {
    clearTimeout(unitDebounceRef.current)
    setResidentInfo(null)
    if (!unit || unit.trim().length < 2) return
    unitDebounceRef.current = setTimeout(async () => {
      try {
        setResidentLoading(true)
        const res = await visitorService.residentByUnit(unit.trim())
        setResidentInfo(res.data)
      } catch {
        setResidentInfo(null)
      } finally {
        setResidentLoading(false)
      }
    }, 500)
  }

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }))
    if (name === 'host_unit') lookupResident(value)
  }

  const validate = () => {
    const e = {}
    if (!form.visitor_name.trim()) e.visitor_name = t.required
    if (!form.host_unit.trim()) e.host_unit = t.required
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleLogVisitor = async () => {
    if (!validate()) return
    try {
      setSubmitting(true)
      await visitorService.logVisitor(form)
      toast.success('Visitor logged successfully')
      setLogDialog(false)
      setForm(EMPTY_FORM)
      setErrors({})
      fetchVisitors()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to log visitor')
    } finally {
      setSubmitting(false)
    }
  }

  const handleCheckOut = async (id) => {
    try {
      await visitorService.updateStatus(id, 'checked_out')
      toast.success('Visitor checked out')
      fetchVisitors()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to check out visitor')
    }
  }

  const openEditDialog = (v) => {
    setEditForm({
      visitor_name: v.visitor_name,
      visitor_phone: v.visitor_phone || '',
      vehicle_number: v.vehicle_number || '',
      purpose: v.purpose || '',
      host_unit: v.host_unit,
      notes: v.notes || '',
    })
    setEditDialog({ open: true, item: v })
  }

  const handleEditSave = async () => {
    if (!editForm.visitor_name.trim() || !editForm.host_unit.trim()) {
      toast.error('Visitor name and host unit are required')
      return
    }
    try {
      setSaving(true)
      await visitorService.editVisitor(editDialog.item.id, editForm)
      toast.success('Entry updated')
      setEditDialog({ open: false, item: null })
      fetchVisitors()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update entry')
    } finally {
      setSaving(false)
    }
  }

  const filtered = visitors.filter((v) => {
    const q = search.toLowerCase()
    return (
      v.visitor_name.toLowerCase().includes(q) ||
      v.host_unit.toLowerCase().includes(q) ||
      (v.visitor_phone || '').toLowerCase().includes(q)
    )
  })

  const fmtTime = (dt) => dt ? format(new Date(dt.endsWith('Z') ? dt : dt + 'Z'), 'dd MMM yyyy, HH:mm') : '—'

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
          <Box>
            <Typography variant="h5" fontWeight={700}>Security – Visitor Log</Typography>
            <Typography variant="body2" color="text.secondary">Log and track all visitors entering the society</Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh">
              <IconButton onClick={fetchVisitors}><RefreshIcon /></IconButton>
            </Tooltip>
            {canLog && (
              <Button variant="contained" startIcon={<PersonAddIcon />} onClick={() => setLogDialog(true)}>
                Log Visitor
              </Button>
            )}
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Search */}
        <TextField
          placeholder="Search by name, unit, or phone…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          sx={{ mb: 2, width: { xs: '100%', sm: 320 } }}
          InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment> }}
        />

        {/* Table */}
        {loading ? (
          <Box sx={{ textAlign: 'center', py: 4 }}><CircularProgress /></Box>
        ) : filtered.length === 0 ? (
          <Alert severity="info">No visitor records found.</Alert>
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Visitor</strong></TableCell>
                  <TableCell><strong>Phone</strong></TableCell>
                  <TableCell><strong>Host Unit</strong></TableCell>
                  <TableCell><strong>Purpose</strong></TableCell>
                  <TableCell><strong>Check In</strong></TableCell>
                  <TableCell><strong>Check Out</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell><strong>Resident / Call</strong></TableCell>
                  <TableCell align="right"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filtered.map((v) => (
                  <TableRow key={v.id} hover>
                    <TableCell>{v.visitor_name}</TableCell>
                    <TableCell>{v.visitor_phone || '—'}</TableCell>
                    <TableCell>{v.host_unit}</TableCell>
                    <TableCell>{v.purpose || '—'}</TableCell>
                    <TableCell>{fmtTime(v.check_in_time)}</TableCell>
                    <TableCell>{fmtTime(v.check_out_time)}</TableCell>
                    <TableCell>
                      <Chip
                        label={STATUS_CONFIG[v.status]?.label || v.status}
                        color={STATUS_CONFIG[v.status]?.color || 'default'}
                        size="small"
                      />
                    </TableCell>
                    {/* Show countdown, then reveal phone only after 60 s */}
                    <TableCell>
                      {v.status === 'pending' && (() => {
                        const secs = elapsed[v.id] ?? 0
                        const overdue = secs >= 60
                        const remaining = Math.max(0, 60 - secs)
                        return (
                          <Box>
                            {overdue ? (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'error.main' }}>
                                <WarningIcon fontSize="small" />
                                <Typography variant="caption" fontWeight={700}>No reply!</Typography>
                              </Box>
                            ) : (
                              <Typography variant="caption" color="text.secondary">
                                {`${remaining}s`}
                              </Typography>
                            )}
                            {overdue && v.host_phone && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.3 }}>
                                <CallIcon fontSize="small" color="error" />
                                <Typography
                                  variant="caption"
                                  fontWeight={700}
                                  color="error.main"
                                  component="a"
                                  href={`tel:${v.host_phone}`}
                                  sx={{ textDecoration: 'none', cursor: 'pointer' }}
                                >
                                  {v.host_phone}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        )
                      })()}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => setViewDialog({ open: true, item: v })}>
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {canLog && v.status === 'pending' && (
                        <Tooltip title="Edit Entry">
                          <IconButton size="small" color="primary" onClick={() => openEditDialog(v)}>
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      {canLog && (v.status === 'approved' || v.status === 'pending') && (
                        <Tooltip title="Mark Check Out">
                          <IconButton size="small" color="warning" onClick={() => handleCheckOut(v.id)}>
                            <CheckOutIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* ── Log Visitor Dialog ─────────────────────────────────────────────── */}
      <Dialog
        open={logDialog}
        onClose={() => { setLogDialog(false); setErrors({}); setResidentInfo(null) }}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3, overflow: 'visible' } }}
      >
        {/* Coloured header banner */}
        <Box
          sx={{
            background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
            borderRadius: '12px 12px 0 0',
            px: 3, py: 2,
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.25)', width: 40, height: 40 }}>
              <SecurityIcon sx={{ color: '#fff' }} />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={700} color="#fff">{t.title}</Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>{t.subtitle}</Typography>
            </Box>
          </Box>
          {/* Language toggle */}
          <ToggleButtonGroup
            value={lang}
            exclusive
            onChange={(_, v) => v && setLang(v)}
            size="small"
            sx={{
              bgcolor: 'rgba(255,255,255,0.15)',
              '& .MuiToggleButton-root': {
                color: 'rgba(255,255,255,0.7)',
                border: 'none',
                px: 1.5,
                fontWeight: 600,
                fontSize: '0.75rem',
                '&.Mui-selected': { bgcolor: 'rgba(255,255,255,0.3)', color: '#fff' },
              },
            }}
          >
            {Object.entries(LANG).map(([key, val]) => (
              <ToggleButton key={key} value={key}>{val.code}</ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>

        <DialogContent sx={{ pt: 3, pb: 1 }}>
          {/* Section: Visitor Information */}
          <Typography variant="overline" color="primary" fontWeight={700} sx={{ letterSpacing: 1.2 }}>
            {t.sectionVisitor}
          </Typography>
          <Divider sx={{ mb: 2, mt: 0.5 }} />
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={7}>
              <FormField
                icon={<PersonIcon fontSize="small" />}
                label={t.visitorName}
                required
                name="visitor_name"
                value={form.visitor_name}
                onChange={handleFormChange}
                placeholder={t.visitorNamePlaceholder}
                error={!!errors.visitor_name}
                helperText={errors.visitor_name}
              />
            </Grid>
            <Grid item xs={12} sm={5}>
              <FormField
                icon={<PhoneIcon fontSize="small" />}
                label={t.phone}
                name="visitor_phone"
                value={form.visitor_phone}
                onChange={handleFormChange}
                placeholder={t.phonePlaceholder}
                inputProps={{ inputMode: 'tel' }}
              />
            </Grid>
          </Grid>

          {/* Section: Visit Details */}
          <Typography variant="overline" color="primary" fontWeight={700} sx={{ letterSpacing: 1.2 }}>
            {t.sectionVisit}
          </Typography>
          <Divider sx={{ mb: 2, mt: 0.5 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormField
                icon={<HomeIcon fontSize="small" />}
                label={t.hostUnit}
                required
                name="host_unit"
                value={form.host_unit}
                onChange={handleFormChange}
                placeholder={t.hostUnitPlaceholder}
                error={!!errors.host_unit}
                helperText={errors.host_unit}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormField
                icon={<CarIcon fontSize="small" />}
                label={t.vehicle}
                name="vehicle_number"
                value={form.vehicle_number}
                onChange={handleFormChange}
                placeholder={t.vehiclePlaceholder}
                inputProps={{ style: { textTransform: 'uppercase' } }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormField
                icon={<InfoIcon fontSize="small" />}
                label={t.purpose}
                name="purpose"
                value={form.purpose}
                onChange={handleFormChange}
                placeholder={t.purposePlaceholder}
              />
            </Grid>
            <Grid item xs={12}>
              <FormField
                icon={<NotesIcon fontSize="small" />}
                label={t.notes}
                name="notes"
                value={form.notes}
                onChange={handleFormChange}
                placeholder={t.notesPlaceholder}
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
          <Button
            onClick={() => { setLogDialog(false); setErrors({}) }}
            variant="outlined"
            color="inherit"
            sx={{ minWidth: 100 }}
          >
            {t.cancel}
          </Button>
          <Button
            variant="contained"
            onClick={handleLogVisitor}
            disabled={submitting}
            startIcon={!submitting && <PersonAddIcon />}
            sx={{ minWidth: 140 }}
          >
            {submitting ? <CircularProgress size={20} /> : t.submit}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Details Dialog */}
      <Dialog open={viewDialog.open} onClose={() => setViewDialog({ open: false, item: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Visitor Details</DialogTitle>
        <DialogContent dividers>
          {viewDialog.item && (
            <Grid container spacing={1.5}>
              {[
                ['Name', viewDialog.item.visitor_name],
                ['Phone', viewDialog.item.visitor_phone || '—'],
                ['Vehicle', viewDialog.item.vehicle_number || '—'],
                ['Purpose', viewDialog.item.purpose || '—'],
                ['Host Unit', viewDialog.item.host_unit],
                ['Status', STATUS_CONFIG[viewDialog.item.status]?.label || viewDialog.item.status],
                ['Check In', fmtTime(viewDialog.item.check_in_time)],
                ['Check Out', fmtTime(viewDialog.item.check_out_time)],
                ['Notes', viewDialog.item.notes || '—'],
              ].map(([label, value]) => (
                <Grid item xs={12} sm={6} key={label}>
                  <Typography variant="caption" color="text.secondary">{label}</Typography>
                  <Typography variant="body2">{value}</Typography>
                </Grid>
              ))}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog({ open: false, item: null })}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Entry Dialog */}
      <Dialog open={editDialog.open} onClose={() => setEditDialog({ open: false, item: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Visitor Entry</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Visitor Name *"
                name="visitor_name"
                value={editForm.visitor_name}
                onChange={(e) => setEditForm((p) => ({ ...p, visitor_name: e.target.value }))}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Phone Number"
                name="visitor_phone"
                value={editForm.visitor_phone}
                onChange={(e) => setEditForm((p) => ({ ...p, visitor_phone: e.target.value }))}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Host Unit *"
                name="host_unit"
                value={editForm.host_unit}
                onChange={(e) => setEditForm((p) => ({ ...p, host_unit: e.target.value }))}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Vehicle Number"
                name="vehicle_number"
                value={editForm.vehicle_number}
                onChange={(e) => setEditForm((p) => ({ ...p, vehicle_number: e.target.value }))}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Purpose of Visit"
                name="purpose"
                value={editForm.purpose}
                onChange={(e) => setEditForm((p) => ({ ...p, purpose: e.target.value }))}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Notes"
                name="notes"
                value={editForm.notes}
                onChange={(e) => setEditForm((p) => ({ ...p, notes: e.target.value }))}
                fullWidth
                size="small"
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, item: null })}>Cancel</Button>
          <Button variant="contained" onClick={handleEditSave} disabled={saving}>
            {saving ? <CircularProgress size={20} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default SecurityPage
