/**
 * AnnouncementManagement Page
 * Admin-only page for managing event announcements
 */

import { useState, useEffect } from 'react'
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Grid,
  Skeleton
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import { toast } from 'react-toastify'
import { format } from 'date-fns'
import { useSelector } from 'react-redux'
import announcementService from '../api/announcementService'
import { PRIORITY_LEVELS, getPriorityColor } from '../constants/announcements'

const AnnouncementManagement = () => {
  const user = useSelector((state) => state.auth.user)
  const isAdmin = user?.role === 'admin'
  const [announcements, setAnnouncements] = useState([])
  const [loading, setLoading] = useState(true)
  const [formOpen, setFormOpen] = useState(false)
  const [selectedAnnouncement, setSelectedAnnouncement] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    priority: 'normal',
    is_active: true,
    start_date: '',
    end_date: ''
  })

  useEffect(() => {
    loadAnnouncements()
  }, [isAdmin]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (selectedAnnouncement) {
      setFormData({
        title: selectedAnnouncement.title || '',
        content: selectedAnnouncement.content || '',
        priority: selectedAnnouncement.priority || 'normal',
        is_active: selectedAnnouncement.is_active ?? true,
        start_date: selectedAnnouncement.start_date ? selectedAnnouncement.start_date.substring(0, 16) : '',
        end_date: selectedAnnouncement.end_date ? selectedAnnouncement.end_date.substring(0, 16) : ''
      })
    } else {
      setFormData({
        title: '',
        content: '',
        priority: 'normal',
        is_active: true,
        start_date: '',
        end_date: ''
      })
    }
  }, [selectedAnnouncement, formOpen])

  const loadAnnouncements = async () => {
    try {
      setLoading(true)
      // non-admin users can only see active announcements
      const data = isAdmin
        ? await announcementService.getAllAnnouncements()
        : await announcementService.getActiveAnnouncements()
      setAnnouncements(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading announcements:', error)
      toast.error('Failed to load announcements')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedAnnouncement(null)
    setFormOpen(true)
  }

  const handleEdit = (announcement) => {
    setSelectedAnnouncement(announcement)
    setFormOpen(true)
  }

  const handleDelete = async (announcementId) => {
    if (!window.confirm('Are you sure you want to delete this announcement?')) {
      return
    }

    try {
      await announcementService.deleteAnnouncement(announcementId)
      toast.success('Announcement deleted successfully')
      loadAnnouncements()
    } catch (error) {
      console.error('Error deleting announcement:', error)
      toast.error('Failed to delete announcement')
    }
  }

  const handleFormChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.type === 'checkbox' ? event.target.checked : event.target.value
    }))
  }

  const handleFormSubmit = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      toast.error('Title and content are required')
      return
    }

    try {
      setSubmitting(true)
      const submitData = {
        title: formData.title,
        content: formData.content,
        priority: formData.priority,
        is_active: formData.is_active,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null
      }

      if (selectedAnnouncement) {
        await announcementService.updateAnnouncement(selectedAnnouncement.id, submitData)
        toast.success('Announcement updated successfully')
      } else {
        await announcementService.createAnnouncement(submitData)
        toast.success('Announcement created successfully')
      }
      
      setFormOpen(false)
      loadAnnouncements()
    } catch (error) {
      console.error('Error saving announcement:', error)
      toast.error('Failed to save announcement')
    } finally {
      setSubmitting(false)
    }
  }

  const formatDate = (dateString) => {
    return dateString ? format(new Date(dateString), 'MMM dd, yyyy HH:mm') : '-'
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" fontWeight="bold">
          {isAdmin ? 'Announcement Management' : 'Announcements'}
        </Typography>
        {isAdmin && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Create Announcement
          </Button>
        )}
      </Box>

      {/* Empty state */}
      {!loading && announcements.length === 0 && (
        <Alert severity="info">
          No announcements yet. Create your first announcement to get started!
        </Alert>
      )}

      {/* Loading state */}
      {loading && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
              </TableRow>
            </TableHead>
          </Table>
        </TableContainer>
      )}

      {/* Announcements table */}
      {!loading && announcements.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Title</strong></TableCell>
                <TableCell><strong>Priority</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Start Date</strong></TableCell>
                <TableCell><strong>End Date</strong></TableCell>
                <TableCell><strong>Created</strong></TableCell>
                <TableCell align="right"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {announcements.map((announcement) => (
                <TableRow key={announcement.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="500">
                      {announcement.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {announcement.content.substring(0, 60)}
                      {announcement.content.length > 60 && '...'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={announcement.priority}
                      size="small"
                      color={getPriorityColor(announcement.priority)}
                      sx={{ textTransform: 'uppercase' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={announcement.is_active ? 'Active' : 'Inactive'}
                      size="small"
                      color={announcement.is_active ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{formatDate(announcement.start_date)}</TableCell>
                  <TableCell>{formatDate(announcement.end_date)}</TableCell>
                  <TableCell>{formatDate(announcement.created_at)}</TableCell>
                  <TableCell align="right">
                    {isAdmin && (
                      <>
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleEdit(announcement)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(announcement.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={formOpen} onClose={() => setFormOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedAnnouncement ? 'Edit Announcement' : 'Create New Announcement'}
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Title"
                  value={formData.title}
                  onChange={handleFormChange('title')}
                  required
                  inputProps={{ maxLength: 200 }}
                  helperText={`${formData.title.length}/200 characters`}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Content"
                  value={formData.content}
                  onChange={handleFormChange('content')}
                  required
                  multiline
                  rows={4}
                  helperText="Announcement message to display"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={formData.priority}
                    onChange={handleFormChange('priority')}
                    label="Priority"
                  >
                    {PRIORITY_LEVELS.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_active}
                      onChange={handleFormChange('is_active')}
                      color="primary"
                    />
                  }
                  label="Active"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Start Date (Optional)"
                  type="datetime-local"
                  value={formData.start_date}
                  onChange={handleFormChange('start_date')}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="End Date (Optional)"
                  type="datetime-local"
                  value={formData.end_date}
                  onChange={handleFormChange('end_date')}
                  InputLabelProps={{ shrink: true }}
                  inputProps={{ min: formData.start_date }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setFormOpen(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleFormSubmit}
            variant="contained"
            disabled={!formData.title.trim() || !formData.content.trim() || submitting}
          >
            {submitting ? 'Saving...' : selectedAnnouncement ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default AnnouncementManagement
