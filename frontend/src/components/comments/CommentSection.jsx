import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Divider,
  Paper,
  Alert,
  CircularProgress
} from '@mui/material'
import CommentIcon from '@mui/icons-material/Comment'
import { toast } from 'react-toastify'
import {
  getComments,
  createComment,
  updateComment,
  deleteComment
} from '../../api/commentService'
import { useAuth } from '../../hooks/useAuth'
import CommentForm from './CommentForm'
import CommentList from './CommentList'

/**
 * CommentSection Component
 * Main container for comments functionality
 */
const CommentSection = ({ issueId }) => {
  const { user } = useAuth()
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch comments on mount
  useEffect(() => {
    fetchComments()
  }, [issueId])

  const fetchComments = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getComments(issueId)
      setComments(data.comments || [])
    } catch (err) {
      console.error('Error fetching comments:', err)
      setError('Failed to load comments')
    } finally {
      setLoading(false)
    }
  }

  const handleAddComment = async (content) => {
    try {
      const newComment = await createComment(issueId, content)
      setComments((prev) => [...prev, newComment])
      return newComment
    } catch (error) {
      throw error
    }
  }

  const handleEditComment = async (commentId, content) => {
    try {
      const updatedComment = await updateComment(commentId, content)
      setComments((prev) =>
        prev.map((comment) =>
          comment.id === commentId ? updatedComment : comment
        )
      )
      return updatedComment
    } catch (error) {
      throw error
    }
  }

  const handleDeleteComment = async (commentId) => {
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this comment?')) {
      return
    }

    try {
      await deleteComment(commentId)
      setComments((prev) => prev.filter((comment) => comment.id !== commentId))
      toast.success('Comment deleted')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete comment')
      throw error
    }
  }

  return (
    <Paper elevation={0} sx={{ p: 3, mt: 3, border: '1px solid', borderColor: 'grey.200' }}>
      {/* Section Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <CommentIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">
          Comments ({comments.length})
        </Typography>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Add Comment Form */}
      <Box sx={{ mb: 3 }}>
        <CommentForm onSubmit={handleAddComment} />
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Comments List */}
      <CommentList
        comments={comments}
        loading={loading}
        currentUser={user}
        onEdit={handleEditComment}
        onDelete={handleDeleteComment}
      />
    </Paper>
  )
}

export default CommentSection
