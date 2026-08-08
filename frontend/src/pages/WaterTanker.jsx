import { useState, useEffect, useCallback } from 'react'
import { useSelector } from 'react-redux'
import {
  Box, Container, Typography, Paper, Tabs, Tab, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Select, MenuItem, FormControl, InputLabel, IconButton, Tooltip,
  Alert, CircularProgress, Grid, Stack, Divider,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import CancelIcon from '@mui/icons-material/Cancel'
import LocalShippingIcon from '@mui/icons-material/LocalShipping'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ExitToAppIcon from '@mui/icons-material/ExitToApp'
import { toast } from 'react-toastify'
import { format, parseISO } from 'date-fns'
import waterTankerService from '../api/waterTankerService'
import { USER_ROLES } from '../constants/roles'

const STATUS_CONFIG = {
  scheduled:  { label: 'Scheduled',  color: 'info'    },
  in_transit: { label: 'In Transit', color: 'warning' },
  delivered:  { label: 'Delivered',  color: 'success' },
  cancelled:  { label: 'Cancelled',  color: 'error'   },
}

const EMPTY_ORDER = {
  supplier_id:    '',
  scheduled_date: new Date().toISOString().slice(0, 10), // default today
  scheduled_time: '',   // arrived time
  departed_time:  '',   // departed time
  vehicle_number: '',
  quantity_kl:    '',
  notes:          '',
}

const EMPTY_SUPPLIER = {
  name: '', contact_name: '', phone: '',
  capacity_kl: '', rate_per_kl: '', notes: '',
}

const WaterTanker = () => {
  const user    = useSelector(s => s.auth.user)
  const isAdmin = user?.role === USER_ROLES.ADMIN

  const [tab,       setTab]       = useState(0)
  const [orders,    setOrders]    = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)
  const [processing, setProcessing] = useState(null)

  // order dialog
  const [orderDlg, setOrderDlg] = useState({ open: false, order: null })
  const [orderForm, setOrderForm] = useState(EMPTY_ORDER)
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  // supplier dialog (admin)
  const [supplierDlg, setSupplierDlg] = useState({ open: false, supplier: null })
  const [supplierForm, setSupplierForm] = useState(EMPTY_SUPPLIER)

  // status update dialog
  const [statusDlg, setStatusDlg] = useState({ open: false, order: null })
  const [statusForm, setStatusForm] = useState({ status: '', actual_quantity_kl: '', amount: '', notes: '' })

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [o, s] = await Promise.all([
        waterTankerService.getOrders(),
        waterTankerService.getSuppliers({ active_only: false }),
      ])
      setOrders(o)
      setSuppliers(s)
    } catch {
      setError('Failed to load data.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchAll() }, [fetchAll])

  // ── Order CRUD ────────────────────────────────────────────────────────────
  // open create form with arrived time auto-filled to now
  const openCreateOrder = () => {
    const now = new Date()
    const hh  = String(now.getHours()).padStart(2, '0')
    const mm  = String(now.getMinutes()).padStart(2, '0')
    setFormErrors({})
    setOrderForm({
      ...EMPTY_ORDER,
      scheduled_date: now.toISOString().slice(0, 10),
      scheduled_time: `${hh}:${mm}`,
    })
    setOrderDlg({ open: true, order: null })
  }

  const openEditOrder = (order) => {
    setFormErrors({})
    setOrderForm({
      supplier_id:    order.supplier_id    || '',
      scheduled_date: order.scheduled_date,
      scheduled_time: order.scheduled_time?.slice(0, 5) || '',
      departed_time:  '',   // not editable post-creation
      vehicle_number: order.vehicle_number || '',
      quantity_kl:    order.quantity_kl    ?? '',
      notes:          order.notes          || '',
    })
    setOrderDlg({ open: true, order })
  }

  // one-click: stamp current time as departed and mark delivered
  const handleMarkDeparted = async (order) => {
    try {
      setProcessing(order.id + '_depart')
      const now = new Date()
      const hh  = String(now.getHours()).padStart(2, '0')
      const mm  = String(now.getMinutes()).padStart(2, '0')
      await waterTankerService.updateOrder(order.id, {
        departed_time: `${hh}:${mm}:00`,
        status:        'delivered',
        actual_quantity_kl: order.actual_quantity_kl || order.quantity_kl || 0,
      })
      toast.success(`Tanker marked as departed at ${hh}:${mm}`)
      fetchAll()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Update failed')
    } finally {
      setProcessing(null)
    }
  }

  const handleOrderSubmit = async () => {
    // validate mandatory fields
    const errors = {}
    if (!orderForm.supplier_id)    errors.supplier_id    = 'Supplier is required'
    if (!orderForm.vehicle_number?.trim()) errors.vehicle_number = 'Vehicle number is required'
    if (!orderForm.scheduled_date) errors.scheduled_date = 'Date is required'
    if (Object.keys(errors).length) {
      setFormErrors(errors)
      return
    }
    setFormErrors({})
    try {
      setSubmitting(true)
      const payload = {
        supplier_id:    orderForm.supplier_id    || null,
        scheduled_date: orderForm.scheduled_date,
        scheduled_time: orderForm.scheduled_time ? orderForm.scheduled_time + ':00' : null,
        departed_time:  orderForm.departed_time  ? orderForm.departed_time  + ':00' : null,
        vehicle_number: orderForm.vehicle_number || null,
        quantity_kl:    orderForm.quantity_kl ? Number(orderForm.quantity_kl) : 0,
        notes:          orderForm.notes         || null,
      }
      if (orderDlg.order) {
        await waterTankerService.updateOrder(orderDlg.order.id, payload)
        toast.success('Entry updated')
      } else {
        await waterTankerService.createOrder(payload)
        toast.success('Tanker arrival logged')
      }
      setOrderDlg({ open: false, order: null })
      fetchAll()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Save failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancelOrder = async (id) => {
    try {
      setProcessing(id)
      await waterTankerService.cancelOrder(id)
      toast.success('Order cancelled')
      fetchAll()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Cancel failed')
    } finally {
      setProcessing(null)
    }
  }

  const openStatusUpdate = (order) => {
    setStatusForm({
      status:             order.status,
      actual_quantity_kl: order.actual_quantity_kl ?? '',
      amount:             order.amount ?? '',
      notes:              order.notes ?? '',
    })
    setStatusDlg({ open: true, order })
  }

  const handleStatusUpdate = async () => {
    try {
      setSubmitting(true)
      const payload = {
        status:             statusForm.status,
        ...(statusForm.actual_quantity_kl && { actual_quantity_kl: Number(statusForm.actual_quantity_kl) }),
        ...(statusForm.amount && { amount: Number(statusForm.amount) }),
        ...(statusForm.notes && { notes: statusForm.notes }),
      }
      await waterTankerService.updateOrder(statusDlg.order.id, payload)
      toast.success('Status updated')
      setStatusDlg({ open: false, order: null })
      fetchAll()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Update failed')
    } finally {
      setSubmitting(false)
    }
  }

  // ── Supplier CRUD (admin) ──────────────────────────────────────────────────
  const openCreateSupplier = () => {
    setSupplierForm(EMPTY_SUPPLIER)
    setSupplierDlg({ open: true, supplier: null })
  }

  const openEditSupplier = (s) => {
    setSupplierForm({
      name: s.name, contact_name: s.contact_name || '',
      phone: s.phone || '', capacity_kl: s.capacity_kl ?? '',
      rate_per_kl: s.rate_per_kl ?? '', notes: s.notes || '',
    })
    setSupplierDlg({ open: true, supplier: s })
  }

  const handleSupplierSubmit = async () => {
    if (!supplierForm.name.trim()) { toast.error('Name required'); return }
    try {
      setSubmitting(true)
      const payload = {
        name:         supplierForm.name,
        contact_name: supplierForm.contact_name || null,
        phone:        supplierForm.phone        || null,
        capacity_kl:  supplierForm.capacity_kl  ? Number(supplierForm.capacity_kl)  : null,
        rate_per_kl:  supplierForm.rate_per_kl  ? Number(supplierForm.rate_per_kl)  : null,
        notes:        supplierForm.notes        || null,
      }
      if (supplierDlg.supplier) {
        await waterTankerService.updateSupplier(supplierDlg.supplier.id, payload)
        toast.success('Supplier updated')
      } else {
        await waterTankerService.createSupplier(payload)
        toast.success('Supplier added')
      }
      setSupplierDlg({ open: false, supplier: null })
      fetchAll()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Save failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleToggleSupplier = async (s) => {
    try {
      await waterTankerService.updateSupplier(s.id, { is_active: !s.is_active })
      toast.success(s.is_active ? 'Supplier deactivated' : 'Supplier activated')
      fetchAll()
    } catch {
      toast.error('Update failed')
    }
  }

  // ── Stats ─────────────────────────────────────────────────────────────────
  const stats = {
    total:     orders.length,
    scheduled: orders.filter(o => o.status === 'scheduled').length,
    delivered: orders.filter(o => o.status === 'delivered').length,
    totalKL:   orders.filter(o => o.status === 'delivered')
                     .reduce((s, o) => s + Number(o.actual_quantity_kl || o.quantity_kl), 0),
    totalCost: orders.filter(o => o.status === 'delivered')
                     .reduce((s, o) => s + Number(o.amount || 0), 0),
  }

  const fmtDate = (d) => { try { return format(parseISO(d), 'dd MMM yyyy') } catch { return d } }

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
      <CircularProgress />
    </Box>
  )

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3} flexWrap="wrap" gap={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <LocalShippingIcon color="primary" sx={{ fontSize: 30 }} />
          <Box>
            <Typography variant="h5" fontWeight={700}>Water Tanker Management</Typography>
            <Typography variant="caption" color="text.secondary">Track water tanker deliveries and suppliers</Typography>
          </Box>
        </Box>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh"><IconButton size="small" onClick={fetchAll}><RefreshIcon /></IconButton></Tooltip>
          <Button variant="contained" startIcon={<AddIcon />} size="small" onClick={openCreateOrder}>
            Log Tanker Entry
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Summary stats */}
      <Grid container spacing={2} mb={3}>
        {[
          ['Total Orders',   stats.total,                    '#1976d2'],
          ['Scheduled',      stats.scheduled,                '#f57c00'],
          ['Delivered',      stats.delivered,                '#388e3c'],
          ['Total Water',    `${stats.totalKL.toFixed(1)} KL`, '#0288d1'],
          ['Total Spent',    `₹${stats.totalCost.toFixed(0)}`, '#7b1fa2'],
        ].map(([label, val, color]) => (
          <Grid item xs={6} sm={4} md={2.4} key={label}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">{label}</Typography>
              <Typography variant="h5" fontWeight={700} sx={{ color }}>{val}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label={`Orders (${orders.length})`} />
          <Tab label={`Suppliers (${suppliers.length})`} />
        </Tabs>
      </Box>

      {/* ── Orders tab ───────────────────────────────────────────────── */}
      {tab === 0 && (
        orders.length === 0 ? (
          <Paper sx={{ p: 5, textAlign: 'center' }}>
            <LocalShippingIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography color="text.secondary">No entries yet.</Typography>
            <Button variant="outlined" sx={{ mt: 2 }} onClick={openCreateOrder}>Log Tanker Entry</Button>
          </Paper>
        ) : (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell><strong>Date</strong></TableCell>
                  <TableCell><strong>Supplier</strong></TableCell>
                  <TableCell><strong>Vehicle / Driver</strong></TableCell>
                  <TableCell><strong>Ordered (KL)</strong></TableCell>
                  <TableCell><strong>Delivered (KL)</strong></TableCell>
                  <TableCell><strong>Amount</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell align="center"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map(o => {
                  const sc = STATUS_CONFIG[o.status] || { label: o.status, color: 'default' }
                  return (
                    <TableRow key={o.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>{fmtDate(o.scheduled_date)}</Typography>
                        <Box display="flex" gap={1} mt={0.3}>
                          {o.scheduled_time && (
                            <Typography variant="caption" color="text.secondary">
                              🟢 {o.scheduled_time.slice(0, 5)}
                            </Typography>
                          )}
                          {o.departed_time && (
                            <Typography variant="caption" color="text.secondary">
                              🔴 {o.departed_time.slice(0, 5)}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{o.supplier?.name || '—'}</Typography>
                        {o.supplier?.phone && (
                          <Typography variant="caption" color="text.secondary">{o.supplier.phone}</Typography>
                        )}
                      </TableCell>                      <TableCell>
                        {o.vehicle_number && (
                          <Typography variant="body2" fontWeight={600}>{o.vehicle_number}</Typography>
                        )}
                        {o.driver_name && (
                          <Typography variant="caption" display="block">{o.driver_name}</Typography>
                        )}
                        {o.driver_phone && (
                          <Typography variant="caption" color="text.secondary">{o.driver_phone}</Typography>
                        )}
                        {!o.vehicle_number && !o.driver_name && (
                          <Typography variant="caption" color="text.disabled">\u2014</Typography>
                        )}
                      </TableCell>                      <TableCell><Typography variant="body2">{o.quantity_kl} KL</Typography></TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {o.actual_quantity_kl ? `${o.actual_quantity_kl} KL` : '—'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {Number(o.amount) > 0 ? `₹${Number(o.amount).toFixed(0)}` : '—'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={sc.label} color={sc.color} size="small" />
                      </TableCell>
                      <TableCell align="center">
                        {/* Delivered/cancelled rows are locked — no actions */}
                        {(o.status === 'delivered' || o.status === 'cancelled') ? (
                          <Chip
                            label={o.status === 'delivered' ? '🔒 Locked' : '—'}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: 10, color: 'text.disabled', borderColor: 'divider' }}
                          />
                        ) : (
                          <Stack direction="row" spacing={0.5} justifyContent="center">
                            {/* Mark Departed — fills current time + sets delivered */}
                            <Tooltip title={`Mark Departed (now)`}>
                              <span>
                                <IconButton
                                  size="small"
                                  color="success"
                                  disabled={!!processing}
                                  onClick={() => handleMarkDeparted(o)}
                                  sx={{ bgcolor: 'success.50' }}
                                >
                                  {processing === o.id + '_depart'
                                    ? <CircularProgress size={14} />
                                    : <ExitToAppIcon fontSize="small" />}
                                </IconButton>
                              </span>
                            </Tooltip>

                            {/* Edit – only for scheduled entries */}
                            {o.status === 'scheduled' && (
                              <Tooltip title="Edit">
                                <IconButton size="small" onClick={() => openEditOrder(o)}>
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}

                            {/* Cancel */}
                            <Tooltip title="Cancel">
                              <span>
                                <IconButton
                                  size="small" color="error"
                                  disabled={processing === o.id}
                                  onClick={() => handleCancelOrder(o.id)}
                                >
                                  {processing === o.id
                                    ? <CircularProgress size={14} />
                                    : <CancelIcon fontSize="small" />}
                                </IconButton>
                              </span>
                            </Tooltip>
                          </Stack>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )
      )}

      {/* ── Suppliers tab ────────────────────────────────────────────── */}
      {tab === 1 && (
        <Box>
          {isAdmin && (
            <Box mb={2} display="flex" justifyContent="flex-end">
              <Button variant="contained" startIcon={<AddIcon />} size="small" onClick={openCreateSupplier}>
                Add Supplier
              </Button>
            </Box>
          )}
          {suppliers.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">No suppliers yet.</Typography>
            </Paper>
          ) : (
            <Grid container spacing={2}>
              {suppliers.map(s => (
                <Grid item xs={12} sm={6} md={4} key={s.id}>
                  <Paper sx={{ p: 2.5, opacity: s.is_active ? 1 : 0.6 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                      <Typography fontWeight={700}>{s.name}</Typography>
                      <Chip
                        label={s.is_active ? 'Active' : 'Inactive'}
                        color={s.is_active ? 'success' : 'default'}
                        size="small"
                        onClick={isAdmin ? () => handleToggleSupplier(s) : undefined}
                        clickable={isAdmin}
                      />
                    </Box>
                    <Divider sx={{ my: 1 }} />
                    <Stack spacing={0.5}>
                      {s.contact_name && (
                        <Typography variant="caption">Contact: {s.contact_name}</Typography>
                      )}
                      {s.phone && (
                        <Typography variant="caption">📞 {s.phone}</Typography>
                      )}
                      {s.capacity_kl && (
                        <Typography variant="caption">Capacity: {s.capacity_kl} KL</Typography>
                      )}
                      {s.rate_per_kl && (
                        <Typography variant="caption">Rate: ₹{s.rate_per_kl}/KL</Typography>
                      )}
                    </Stack>
                    {isAdmin && (
                      <Box mt={1.5} display="flex" gap={1}>
                        <Button size="small" startIcon={<EditIcon />} onClick={() => openEditSupplier(s)}>
                          Edit
                        </Button>
                      </Box>
                    )}
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {/* ── Schedule / Edit Order Dialog ─────────────────────────────── */}
      <Dialog open={orderDlg.open} onClose={() => setOrderDlg({ open: false, order: null })} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          {orderDlg.order ? 'Edit Entry' : 'Log Water Tanker Delivery'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2.5 }}>
          <Stack spacing={2.5} mt={0.5}>

            {/* Supplier */}
            <FormControl fullWidth size="small" error={!!formErrors.supplier_id}>
              <InputLabel>Supplier Name *</InputLabel>
              <Select value={orderForm.supplier_id} label="Supplier Name *"
                onChange={e => {
                  setOrderForm(p => ({ ...p, supplier_id: e.target.value }))
                  if (e.target.value) setFormErrors(p => ({ ...p, supplier_id: undefined }))
                }}>
                <MenuItem value=""><em>— Select Supplier —</em></MenuItem>
                {suppliers.filter(s => s.is_active).map(s => (
                  <MenuItem key={s.id} value={s.id}>
                    {s.name}{s.capacity_kl ? ` (${s.capacity_kl} KL)` : ''}
                  </MenuItem>
                ))}
              </Select>
              {formErrors.supplier_id && (
                <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.5 }}>
                  ⚠ {formErrors.supplier_id}
                </Typography>
              )}
            </FormControl>

            {/* Vehicle Number */}
            <TextField label="Vehicle Number *" fullWidth size="small"
              placeholder="e.g. MH-12-AB-1234"
              value={orderForm.vehicle_number}
              error={!!formErrors.vehicle_number}
              helperText={formErrors.vehicle_number ? `⚠ ${formErrors.vehicle_number}` : undefined}
              onChange={e => {
                setOrderForm(p => ({ ...p, vehicle_number: e.target.value }))
                if (e.target.value.trim()) setFormErrors(p => ({ ...p, vehicle_number: undefined }))
              }} />

            {/* Date */}
            <TextField label="Delivery Date" type="date" fullWidth size="small"
              value={orderForm.scheduled_date}
              onChange={e => setOrderForm(p => ({ ...p, scheduled_date: e.target.value }))}
              InputLabelProps={{ shrink: true }} />

            {/* Arrived time (auto-filled, editable) */}
            <TextField label="Arrived Time" type="time" fullWidth size="small"
              value={orderForm.scheduled_time}
              onChange={e => setOrderForm(p => ({ ...p, scheduled_time: e.target.value }))}
              InputLabelProps={{ shrink: true }}
              helperText="Auto-filled with current time" />

            {/* Quantity – optional */}
            <TextField label="Quantity (KL) — optional" type="number" fullWidth size="small"
              value={orderForm.quantity_kl}
              onChange={e => setOrderForm(p => ({ ...p, quantity_kl: e.target.value }))}
              inputProps={{ min: 0, step: 0.5 }} />

          </Stack>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid', borderColor: 'divider', px: 3, py: 2 }}>
          <Button onClick={() => setOrderDlg({ open: false, order: null })} disabled={submitting}>Cancel</Button>
          <Button variant="contained" onClick={handleOrderSubmit} disabled={submitting}>
            {submitting ? <CircularProgress size={20} /> : (orderDlg.order ? 'Save Changes' : 'Log Entry')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Status Update Dialog ─────────────────────────────────────── */}
      <Dialog open={statusDlg.open} onClose={() => setStatusDlg({ open: false, order: null })} maxWidth="xs" fullWidth>
        <DialogTitle>Update Delivery Status</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select value={statusForm.status} label="Status"
                onChange={e => setStatusForm(p => ({ ...p, status: e.target.value }))}>
                {Object.entries(STATUS_CONFIG).map(([v, c]) => (
                  <MenuItem key={v} value={v}>{c.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            {statusForm.status === 'delivered' && (
              <>
                <TextField label="Actual Quantity (KL)" type="number" fullWidth size="small"
                  value={statusForm.actual_quantity_kl}
                  onChange={e => setStatusForm(p => ({ ...p, actual_quantity_kl: e.target.value }))}
                  inputProps={{ min: 0, step: 0.5 }} />
                <TextField label="Amount Paid (₹)" type="number" fullWidth size="small"
                  value={statusForm.amount}
                  onChange={e => setStatusForm(p => ({ ...p, amount: e.target.value }))}
                  inputProps={{ min: 0 }} />
              </>
            )}
            <TextField label="Notes (optional)" multiline rows={2} fullWidth size="small"
              value={statusForm.notes}
              onChange={e => setStatusForm(p => ({ ...p, notes: e.target.value }))} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatusDlg({ open: false, order: null })}>Cancel</Button>
          <Button variant="contained" onClick={handleStatusUpdate} disabled={submitting}>
            {submitting ? <CircularProgress size={20} /> : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Supplier Create / Edit Dialog ────────────────────────────── */}
      <Dialog open={supplierDlg.open} onClose={() => setSupplierDlg({ open: false, supplier: null })} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
          {supplierDlg.supplier ? 'Edit Supplier' : 'Add Supplier'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2.5 }}>
          <Stack spacing={2.5} mt={0.5}>
            <TextField label="Supplier Name *" fullWidth size="small"
              value={supplierForm.name}
              onChange={e => setSupplierForm(p => ({ ...p, name: e.target.value }))} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField label="Contact Person" fullWidth size="small"
                  value={supplierForm.contact_name}
                  onChange={e => setSupplierForm(p => ({ ...p, contact_name: e.target.value }))} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Phone" fullWidth size="small"
                  value={supplierForm.phone}
                  onChange={e => setSupplierForm(p => ({ ...p, phone: e.target.value }))} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Tanker Capacity (KL)" type="number" fullWidth size="small"
                  value={supplierForm.capacity_kl}
                  onChange={e => setSupplierForm(p => ({ ...p, capacity_kl: e.target.value }))}
                  inputProps={{ min: 0, step: 0.5 }} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Rate per KL (₹)" type="number" fullWidth size="small"
                  value={supplierForm.rate_per_kl}
                  onChange={e => setSupplierForm(p => ({ ...p, rate_per_kl: e.target.value }))}
                  inputProps={{ min: 0 }} />
              </Grid>
            </Grid>
            <TextField label="Notes" multiline rows={2} fullWidth size="small"
              value={supplierForm.notes}
              onChange={e => setSupplierForm(p => ({ ...p, notes: e.target.value }))} />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid', borderColor: 'divider', px: 3, py: 2 }}>
          <Button onClick={() => setSupplierDlg({ open: false, supplier: null })} disabled={submitting}>Cancel</Button>
          <Button variant="contained" onClick={handleSupplierSubmit} disabled={submitting}>
            {submitting ? <CircularProgress size={20} /> : (supplierDlg.supplier ? 'Save Changes' : 'Add Supplier')}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default WaterTanker
