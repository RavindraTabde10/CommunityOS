import { useState, useEffect } from 'react'
import { Container, Typography, Paper, Box, Button, Alert, CircularProgress } from '@mui/material'
import { useParams, useNavigate } from 'react-router-dom'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { toast } from 'react-toastify'
import IssueForm from '../../components/forms/IssueForm'
import issueService from '../../api/issueService'
import { useAuth } from '../../hooks/useAuth'

/**
 * EditIssue page - Edit an existing issue
 */
const EditIssue = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [issue, setIssue] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadIssue()
  }, [id])

  const loadIssue = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await issueService.getIssueById(id)
      
      // Check permissions
      if (user && data.reported_by !== user.id && user.role !== 'admin') {
        setError('You do not have permission to edit this issue')
        return
      }
      
      setIssue(data)
    } catch (err) {
      console.error('Error loading issue:', err)
      setError(err.response?.data?.detail || 'Failed to load issue')
      toast.error('Failed to load issue')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async ({ formData, photos }) => {
    try {
      setIsSubmitting(true)
      setError(null)

      // Normalize assigned_to: empty string → null
      const payload = {
        ...formData,
        assigned_to: formData.assigned_to || null,
      }

      // Step 1: Update the issue
      await issueService.updateIssue(id, payload)
      
      // Step 2: Upload new photos if any
      if (photos.length > 0) {
        try {
          const photoFiles = photos.map(photo => photo.file)
          await issueService.uploadPhotos(id, photoFiles)
        } catch (photoError) {
          console.error('Error uploading photos:', photoError)
          toast.warning('Issue updated but some photos failed to upload')
        }
      }

      // Success
      toast.success('Issue updated successfully!')
      
      // Redirect to the issue detail page
      navigate(`/issues/${id}`)
      
    } catch (err) {
      console.error('Error updating issue:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to update issue'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (error || !issue) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {error || 'Issue not found'}
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
    <Container maxWidth="md" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      {/* Back Button */}
      <Button 
        startIcon={<ArrowBackIcon />} 
        onClick={() => navigate(`/issues/${id}`)}
        sx={{ 
          mb: 2,
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
        Back to Issue
      </Button>

      {/* Page Title */}
      <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ color: 'white' }}>
        Edit Issue
      </Typography>
      <Typography variant="body1" paragraph sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
        Update the issue details below. Note: Status and assignment can only be changed by administrators.
      </Typography>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {/* Issue Form */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          mt: 3,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
        }}
      >
        <IssueForm 
          defaultValues={{
            title: issue.title,
            description: issue.description,
            category: issue.category,
            priority: issue.priority,
            location: issue.location || '',
            unit_number: issue.unit_number || '',
            assigned_to: issue.assignee?.id || issue.assigned_to || '',
          }}
          reporterInfo={issue.reporter || null}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          submitButtonText="Update Issue"
          mode="edit"
        />
      </Paper>

      {/* Info Box */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Note:</strong> Existing photos will remain. You can add new photos, but removing existing photos 
          will be available in a future update.
        </Typography>
      </Alert>
    </Container>
  )
}

export default EditIssue
