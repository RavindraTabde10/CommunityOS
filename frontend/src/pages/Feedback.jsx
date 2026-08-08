import { useState, useEffect, useCallback } from 'react'
import { useSelector } from 'react-redux'
import {
  Container, Typography, Box, Paper, Grid, TextField, Button,
  Select, MenuItem, FormControl, InputLabel, Chip, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Dialog, DialogTitle,
  DialogContent, DialogActions, DialogContentText, CircularProgress,
  IconButton, Tooltip, Divider, Alert,
} from '@mui/material'
import {
  Send as SendIcon,
  Reply as ReplyIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import feedbackService from '../api/feedbackService'
import { USER_ROLES } from '../constants/roles'

const CATEGORIES = [
  { value: 'process', label: 'Process Improvement' },
  { value: 'facility', label: 'Facility & Maintenance' },
  { value: 'communication', label: 'Communication' },
  { value: 'safety', label: 'Safety' },
  { value: 'general', label: 'General Suggestion' },
]

const STATUS_CONFIG = {
  pending:      { label: 'Pending',      color: 'default' },
  acknowledged: { label: 'Acknowledged', color: 'info' },
  in_review:    { label: 'In Review',    color: 'warning' },
  implemented:  { label: 'Implemented',  color: 'success' },
  rejected:     { label: 'Rejected',     color: 'error' },
}

const EMPTY_FORM = { title: '', category: 'general', description: '' }

const Feedback = () => {
  const { user } = useSelector((state) => state.auth)
  const isAdmin = user?.role === USER_ROLES.ADMIN

  const [list, setList] = useState([])
  const [loadingList, setLoadingList] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState(EMPTY_FORM)
  const [formErrors, setFormErrors] = useState({})

  // Admin respond dialog
  const [respondDialog, setRespondDialog] = useState({ open: false, item: null })
  const [respondData, setRespondData] = useState({ status: '', admin_response: '' })
  const [responding, setResponding] = useState(false)

  // Admin delete confirm
  const [deleteDialog, setDeleteDialog] = useState({ open: false, id: null, title: '' })
  const [deleting, setDeleting] = useState(false)

  // View full feedback details
  const [viewDialog, setViewDialog] = useState({ open: false, item: null })

  // Edit own feedback
  const [editDialog, setEditDialog] = useState({ open: false, item: null })
  const [editData, setEditData] = useState({ title: '', category: 'general', description: '' })
  const [editErrors, setEditErrors] = useState({})
  const [editing, setEditing] = useState(false)

  const fetchList = useCallback(async () => {
    try {
      setLoadingList(true)
      const res = await feedbackService.getAll()
      setList(res.data?.feedback || [])
    } catch {
      toast.error('Failed to load feedback')
    } finally {
      setLoadingList(false)
    }
  }, [])

  useEffect(() => { fetchList() }, [fetchList])

  const validate = () => {
    const errs = {}
    if (!formData.title.trim()) errs.title = 'Title is required'
    if (!formData.description.trim() || formData.description.trim().length < 10)
      errs.description = 'Description must be at least 10 characters'
    setFormErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    try {
      setSubmitting(true)
      await feedbackService.create({
        title: formData.title.trim(),
        category: formData.category,
        description: formData.description.trim(),
      })
      toast.success('Feedback submitted successfully!')
      setFormData(EMPTY_FORM)
      fetchList()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit feedback')
    } finally {
      setSubmitting(false)
    }
  }

  const openRespondDialog = (item) => {
    setRespondData({ status: item.status, admin_response: item.admin_response || '' })
    setRespondDialog({ open: true, item })
  }

  const handleRespond = async () => {
    try {
      setResponding(true)
      await feedbackService.update(respondDialog.item.id, respondData)
      toast.success('Response saved')
      setRespondDialog({ open: false, item: null })
      fetchList()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save response')
    } finally {
      setResponding(false)
    }
  }

  const handleDeleteConfirm = async () => {
    try {
      setDeleting(true)
      await feedbackService.delete(deleteDialog.id)
      setList((prev) => prev.filter((f) => f.id !== deleteDialog.id))
      toast.success('Feedback deleted')
      setDeleteDialog({ open: false, id: null, title: '' })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete')
    } finally {
      setDeleting(false)
    }
  }

  const openEditDialog = (item) => {
    setEditData({ title: item.title, category: item.category, description: item.description })
    setEditErrors({})
    setEditDialog({ open: true, item })
  }

  const validateEdit = () => {
    const errs = {}
    if (!editData.title.trim()) errs.title = 'Title is required'
    if (!editData.description.trim() || editData.description.trim().length < 10)
      errs.description = 'Description must be at least 10 characters'
    setEditErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleEditSave = async () => {
    if (!validateEdit()) return
    try {
      setEditing(true)
      const res = await feedbackService.edit(editDialog.item.id, {
        title: editData.title.trim(),
        category: editData.category,
        description: editData.description.trim(),
      })
      setList((prev) => prev.map((f) => (f.id === editDialog.item.id ? res.data : f)))
      toast.success('Feedback updated')
      setEditDialog({ open: false, item: null })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update feedback')
    } finally {
      setEditing(false)
    }
  }

  const formatDate = (str) =>
    str ? new Date(str).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—'

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      <Typography variant="h4" fontWeight="bold" sx={{ color: 'white', mb: 3 }}>
        Feedback &amp; Suggestions
      </Typography>

      <Grid container spacing={3}>
        {/* Submission form */}
        <Grid item xs={12} lg={4}>
          <Paper
            elevation={3}
            sx={{ p: 3, background: 'rgba(255,255,255,0.97)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.5)' }}
          >
            <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
              Submit Feedback
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
              Share your suggestions for improving society processes, facilities, or communication.
              All feedback is reviewed by the admin team.
            </Typography>

            <form onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    required
                    label="Title"
                    value={formData.title}
                    onChange={(e) => setFormData((p) => ({ ...p, title: e.target.value }))}
                    error={Boolean(formErrors.title)}
                    helperText={formErrors.title}
                    placeholder="Brief summary of your suggestion"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={formData.category}
                      label="Category"
                      onChange={(e) => setFormData((p) => ({ ...p, category: e.target.value }))}
                    >
                      {CATEGORIES.map((c) => (
                        <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    required
                    multiline
                    rows={5}
                    label="Description"
                    value={formData.description}
                    onChange={(e) => setFormData((p) => ({ ...p, description: e.target.value }))}
                    error={Boolean(formErrors.description)}
                    helperText={formErrors.description || 'Minimum 10 characters'}
                    placeholder="Describe your suggestion in detail..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    startIcon={<SendIcon />}
                    disabled={submitting}
                  >
                    {submitting ? 'Submitting...' : 'Submit Feedback'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </Paper>
        </Grid>

        {/* Submissions list */}
        <Grid item xs={12} lg={8}>
          <Paper
            elevation={3}
            sx={{ p: 3, background: 'rgba(255,255,255,0.97)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.5)' }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight="bold">
                {isAdmin ? 'All Submissions' : 'My Submissions'}
              </Typography>
              <Tooltip title="Refresh">
                <IconButton size="small" onClick={fetchList} disabled={loadingList}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>

            {loadingList ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                <CircularProgress />
              </Box>
            ) : list.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <Typography color="text.secondary">No feedback submitted yet</Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell><strong>Title</strong></TableCell>
                      <TableCell><strong>Category</strong></TableCell>
                      {isAdmin && <TableCell><strong>Submitted By</strong></TableCell>}
                      <TableCell><strong>Date</strong></TableCell>
                      <TableCell><strong>Status</strong></TableCell>
                      <TableCell align="right"><strong>Actions</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {list.map((item) => {
                      const sc = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending
                      const cat = CATEGORIES.find((c) => c.value === item.category)
                      return (
                        <TableRow key={item.id} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">{item.title}</Typography>
                            {item.admin_response && (
                              <Typography variant="caption" color="success.main" display="block" sx={{ mt: 0.25 }}>
                                💬 Admin responded
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption">{cat?.label || item.category}</Typography>
                          </TableCell>
                          {isAdmin && (
                            <TableCell>
                              <Typography variant="caption">{item.submitter?.name || '—'}</Typography>
                            </TableCell>
                          )}
                          <TableCell>
                            <Typography variant="caption">{formatDate(item.created_at)}</Typography>
                          </TableCell>
                          <TableCell>
                            <Chip size="small" label={sc.label} color={sc.color} />
                          </TableCell>
                          <TableCell align="right">
                            {/* View full details */}
                            {isAdmin && (
                              <Tooltip title="View Details">
                                <IconButton size="small" onClick={() => setViewDialog({ open: true, item })}>
                                  <ViewIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            {/* Edit: own pending feedback only */}
                            {String(item.submitted_by) === String(user?.id) && item.status === 'pending' && (
                              <Tooltip title="Edit">
                                <IconButton size="small" color="primary" onClick={() => openEditDialog(item)}>
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            {isAdmin && (
                              <>
                                <Tooltip title="Respond / Update Status">
                                  <IconButton size="small" color="primary" onClick={() => openRespondDialog(item)} sx={{ ml: 0.5 }}>
                                    <ReplyIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Delete">
                                  <IconButton
                                    size="small"
                                    color="error"
                                    sx={{ ml: 0.5 }}
                                    onClick={() => setDeleteDialog({ open: true, id: item.id, title: item.title })}
                                  >
                                    <DeleteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </>
                            )}
                            {!isAdmin && item.admin_response && (
                              <Tooltip title={`Admin: ${item.admin_response}`}>
                                <Chip size="small" label="View Reply" color="info" variant="outlined" sx={{ ml: 0.5 }} />
                              </Tooltip>
                            )}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* View full feedback details dialog (admin) */}
      <Dialog open={viewDialog.open} onClose={() => setViewDialog({ open: false, item: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Feedback Details</DialogTitle>
        <DialogContent dividers>
          {viewDialog.item && (() => {
            const item = viewDialog.item
            const sc = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending
            const cat = CATEGORIES.find((c) => c.value === item.category)
            return (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">Title</Typography>
                  <Typography variant="body1" fontWeight="bold">{item.title}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Category</Typography>
                  <Typography variant="body2">{cat?.label || item.category}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Status</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <Chip size="small" label={sc.label} color={sc.color} />
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Submitted By</Typography>
                  <Typography variant="body2">{item.submitter?.name || '—'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">Date</Typography>
                  <Typography variant="body2">{formatDate(item.created_at)}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Divider />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">Description</Typography>
                  <Typography variant="body2" sx={{ mt: 0.5, whiteSpace: 'pre-wrap' }}>{item.description}</Typography>
                </Grid>
                {item.admin_response && (
                  <Grid item xs={12}>
                    <Alert severity="info" sx={{ mt: 1 }}>
                      <Typography variant="caption" fontWeight="bold" display="block">Admin Response</Typography>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{item.admin_response}</Typography>
                    </Alert>
                  </Grid>
                )}
              </Grid>
            )
          })()}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog({ open: false, item: null })}>Close</Button>
          <Button
            variant="contained"
            startIcon={<ReplyIcon />}
            onClick={() => {
              setViewDialog({ open: false, item: null })
              openRespondDialog(viewDialog.item)
            }}
          >
            Respond
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit own feedback dialog */}
      <Dialog open={editDialog.open} onClose={() => !editing && setEditDialog({ open: false, item: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Feedback</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ pt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Title"
                value={editData.title}
                onChange={(e) => setEditData((p) => ({ ...p, title: e.target.value }))}
                error={Boolean(editErrors.title)}
                helperText={editErrors.title}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={editData.category}
                  label="Category"
                  onChange={(e) => setEditData((p) => ({ ...p, category: e.target.value }))}
                >
                  {CATEGORIES.map((c) => (
                    <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                multiline
                rows={5}
                label="Description"
                value={editData.description}
                onChange={(e) => setEditData((p) => ({ ...p, description: e.target.value }))}
                error={Boolean(editErrors.description)}
                helperText={editErrors.description || 'Minimum 10 characters'}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, item: null })} disabled={editing}>Cancel</Button>
          <Button variant="contained" onClick={handleEditSave} disabled={editing}>
            {editing ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Admin respond dialog */}
      <Dialog open={respondDialog.open} onClose={() => !responding && setRespondDialog({ open: false, item: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Respond to Feedback</DialogTitle>
        <DialogContent dividers>
          <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 0.5 }}>
            {respondDialog.item?.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {respondDialog.item?.description}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Update Status</InputLabel>
                <Select
                  value={respondData.status}
                  label="Update Status"
                  onChange={(e) => setRespondData((p) => ({ ...p, status: e.target.value }))}
                >
                  {Object.entries(STATUS_CONFIG).map(([val, cfg]) => (
                    <MenuItem key={val} value={val}>{cfg.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Admin Response (Optional)"
                value={respondData.admin_response}
                onChange={(e) => setRespondData((p) => ({ ...p, admin_response: e.target.value }))}
                placeholder="Explain the decision or update..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRespondDialog({ open: false, item: null })} disabled={responding}>Cancel</Button>
          <Button variant="contained" onClick={handleRespond} disabled={responding}>
            {responding ? 'Saving...' : 'Save Response'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirm dialog */}
      <Dialog open={deleteDialog.open} onClose={() => !deleting && setDeleteDialog({ open: false, id: null, title: '' })} maxWidth="xs" fullWidth>
        <DialogTitle>Delete Feedback</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Delete <strong>&ldquo;{deleteDialog.title}&rdquo;</strong>? This cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, id: null, title: '' })} disabled={deleting}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDeleteConfirm} disabled={deleting}>
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Feedback
