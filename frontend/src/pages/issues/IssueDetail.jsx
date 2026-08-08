import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  Container, 
  Typography, 
  Paper, 
  Box, 
  CircularProgress, 
  Alert, 
  Button,
  Chip,
  Grid,
  Divider,
  Card,
  CardContent,
  IconButton,
  Dialog,
  DialogContent
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import CalendarTodayIcon from '@mui/icons-material/CalendarToday'
import PersonIcon from '@mui/icons-material/Person'
import CloseIcon from '@mui/icons-material/Close'
import { toast } from 'react-toastify'
import issueService from '../../api/issueService'
import { useAuth } from '../../hooks/useAuth'
import CommentSection from '../../components/comments/CommentSection'
import ActivityTimeline from '../../components/activity/ActivityTimeline'

/**
 * Format date to readable string
 */
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

/**
 * IssueDetail page - View complete issue details
 */
const IssueDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [issue, setIssue] = useState(null)
  const [photos, setPhotos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedPhoto, setSelectedPhoto] = useState(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  useEffect(() => {
    loadIssue()
  }, [id])

  const loadIssue = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [issueData, photosData] = await Promise.all([
        issueService.getIssueById(id),
        issueService.getPhotos(id).catch(() => []) // Photos optional
      ])
      
      setIssue(issueData)
      setPhotos(photosData || [])
    } catch (err) {
      console.error('Error loading issue:', err)
      setError(err.response?.data?.detail || 'Failed to load issue')
      toast.error('Failed to load issue')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      await issueService.deleteIssue(id)
      toast.success('Issue deleted successfully')
      navigate('/issues')
    } catch (err) {
      console.error('Error deleting issue:', err)
      toast.error('Failed to delete issue')
    }
  }

  const statusColors = {
    open: 'error',
    in_progress: 'warning',
    resolved: 'success',
    closed: 'default',
  }

  const priorityColors = {
    low: 'default',
    medium: 'info',
    high: 'warning',
    critical: 'error',
  }

  const canEdit = user && issue && (user.id === issue.reported_by || user.role === 'admin')
  const canDelete = canEdit

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress sx={{ color: 'white' }} />
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {error}
        </Alert>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/issues')}
          sx={{ 
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.25)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            },
          }}
        >
          Back to Issues
        </Button>
      </Container>
    )
  }

  if (!issue) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
        <Alert 
          severity="warning" 
          sx={{ 
            mb: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          Issue not found
        </Alert>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/issues')}
          sx={{ 
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.25)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            },
          }}
        >
          Back to Issues
        </Button>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/issues')}
          sx={{ 
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.25)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            },
          }}
        >
          Back to Issues
        </Button>
        
        {canEdit && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => navigate(`/issues/${id}/edit`)}
              sx={{ 
                color: 'white',
                borderColor: 'rgba(255, 255, 255, 0.3)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                },
              }}
            >
              Edit
            </Button>
            {canDelete && (
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => setDeleteDialogOpen(true)}
                sx={{ 
                  color: 'white',
                  borderColor: 'rgba(255, 100, 100, 0.5)',
                  backgroundColor: 'rgba(255, 100, 100, 0.15)',
                  '&:hover': {
                    borderColor: 'rgba(255, 100, 100, 0.7)',
                    backgroundColor: 'rgba(255, 100, 100, 0.25)',
                  },
                }}
              >
                Delete
              </Button>
            )}
          </Box>
        )}
      </Box>

      {/* Issue Header */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          mb: 3,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="overline" color="text.secondary">
              {issue.id}
            </Typography>
            <Typography variant="h4" gutterBottom fontWeight="bold">
              {issue.title}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label={issue.status?.replace('_', ' ').toUpperCase()}
              color={statusColors[issue.status] || 'default'}
            />
            <Chip
              label={issue.priority?.toUpperCase()}
              color={priorityColors[issue.priority] || 'default'}
              variant="outlined"
            />
          </Box>
        </Box>

        <Typography variant="body1" color="text.secondary" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
          {issue.description}
        </Typography>

        <Divider sx={{ my: 3 }} />

        {/* Issue Metadata */}
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label={issue.category?.toUpperCase()} size="small" />
            </Box>
            <Typography variant="caption" color="text.secondary">
              Category
            </Typography>
          </Grid>

          {issue.location && (
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOnIcon fontSize="small" color="action" />
                <Typography variant="body2">{issue.location}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Location
              </Typography>
            </Grid>
          )}

          {issue.unit_number && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">{issue.unit_number}</Typography>
              <Typography variant="caption" color="text.secondary">
                Unit Number
              </Typography>
            </Grid>
          )}

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CalendarTodayIcon fontSize="small" color="action" />
              <Typography variant="body2">
                {issue.created_at && formatDate(issue.created_at)}
              </Typography>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Created
            </Typography>
          </Grid>

          {/* Reporter */}
          {issue.reporter && (
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon fontSize="small" color="action" />
                <Box>
                  <Typography variant="body2">{issue.reporter.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {issue.reporter.email}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Reporter
              </Typography>
            </Grid>
          )}

          {/* Assignee */}
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <PersonIcon fontSize="small" color={issue.assignee ? 'primary' : 'disabled'} />
              <Box>
                {issue.assignee ? (
                  <>
                    <Typography variant="body2">{issue.assignee.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {issue.assignee.email}
                    </Typography>
                  </>
                ) : (
                  <Typography variant="body2" color="text.secondary" fontStyle="italic">
                    Unassigned
                  </Typography>
                )}
              </Box>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Assignee
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Photos Section */}
      {photos.length > 0 && (
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            mb: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.5)',
          }}
        >
          <Typography variant="h6" gutterBottom>
            Photos ({photos.length})
          </Typography>
          <Grid container spacing={2}>
            {photos.map((photo, index) => (
              <Grid item xs={6} sm={4} md={3} key={photo.id || index}>
                <Card 
                  sx={{ cursor: 'pointer' }}
                  onClick={() => setSelectedPhoto(photo)}
                >
                  <Box
                    component="img"
                    src={photo.url || photo.file_url}
                    alt={`Issue photo ${index + 1}`}
                    sx={{
                      width: '100%',
                      height: 150,
                      objectFit: 'cover',
                    }}
                  />
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Comments Section */}
      <CommentSection issueId={id} />

      {/* Activity Timeline */}
      <ActivityTimeline issueId={id} />

      {/* Photo Lightbox */}
      <Dialog
        open={!!selectedPhoto}
        onClose={() => setSelectedPhoto(null)}
        maxWidth="lg"
        fullWidth
      >
        <IconButton
          sx={{ position: 'absolute', right: 8, top: 8, color: 'white', bgcolor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSelectedPhoto(null)}
        >
          <CloseIcon />
        </IconButton>
        <DialogContent sx={{ p: 0 }}>
          {selectedPhoto && (
            <Box
              component="img"
              src={selectedPhoto.url || selectedPhoto.file_url}
              alt="Full size"
              sx={{ width: '100%', display: 'block' }}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            Delete Issue?
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Are you sure you want to delete this issue? This action cannot be undone.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={handleDelete}
            >
              Delete
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  )
}

export default IssueDetail
