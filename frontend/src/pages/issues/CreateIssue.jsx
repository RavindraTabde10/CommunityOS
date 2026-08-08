import { useState } from 'react'
import { Container, Typography, Paper, Box, Button, Alert } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { toast } from 'react-toastify'
import IssueForm from '../../components/forms/IssueForm'
import issueService from '../../api/issueService'

/**
 * CreateIssue page - Create a new issue
 */
const CreateIssue = () => {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async ({ formData, photos }) => {
    try {
      setIsSubmitting(true)
      setError(null)

      // Normalize assigned_to: empty string → omit field for non-admins
      const payload = {
        ...formData,
        assigned_to: formData.assigned_to || undefined,
      }

      // Step 1: Create the issue
      const newIssue = await issueService.createIssue(payload)
      
      // Step 2: Upload photos if any
      if (photos.length > 0) {
        try {
          const photoFiles = photos.map(photo => photo.file)
          await issueService.uploadPhotos(newIssue.id, photoFiles)
        } catch (photoError) {
          console.error('Error uploading photos:', photoError)
          // Issue created but photos failed - show warning
          toast.warning('Issue created but some photos failed to upload')
        }
      }

      // Success
      toast.success('Issue created successfully!')
      
      // Redirect to the new issue detail page
      navigate(`/issues/${newIssue.id}`)
      
    } catch (err) {
      console.error('Error creating issue:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to create issue'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      {/* Back Button */}
      <Button 
        startIcon={<ArrowBackIcon />} 
        onClick={() => navigate('/issues')}
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
        Back to Issues
      </Button>

      {/* Page Title */}
      <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ color: 'white' }}>
        Create New Issue
      </Typography>
      <Typography variant="body1" paragraph sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
        Fill in the details below to report a new issue. Include photos if possible to help us understand the problem better.
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
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          submitButtonText="Create Issue"
          mode="create"
        />
      </Paper>
    </Container>
  )
}

export default CreateIssue
