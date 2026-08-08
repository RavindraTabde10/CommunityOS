import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Avatar,
  IconButton,
  Tooltip,
  Chip
} from '@mui/material'
import PersonIcon from '@mui/icons-material/Person'
import { formatDistanceToNow } from 'date-fns'
import CommentActions from './CommentActions'
import CommentForm from './CommentForm'

/**
 * CommentItem Component
 * Displays a single comment with edit/delete options
 */
const CommentItem = ({ comment, currentUser, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  // Check if current user can edit/delete this comment
  const isOwner = currentUser?.id === comment.user_id
  const isAdmin = currentUser?.role === 'admin'
  const canEdit = isOwner
  const canDelete = isOwner || isAdmin

  // Format timestamp
  const timestamp = comment.created_at
    ? formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })
    : 'just now'

  // Check if comment was edited
  const isEdited = comment.updated_at && comment.updated_at !== comment.created_at

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
  }

  const handleSaveEdit = async (content) => {
    try {
      await onEdit(comment.id, content)
      setIsEditing(false)
    } catch (error) {
      // Error handled in parent
      throw error
    }
  }

  const handleDelete = async () => {
    try {
      setIsDeleting(true)
      await onDelete(comment.id)
    } catch (error) {
      setIsDeleting(false)
      // Error handled in parent
    }
  }

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        mb: 2,
        backgroundColor: 'grey.50',
        border: '1px solid',
        borderColor: 'grey.200',
        '&:hover': {
          borderColor: 'grey.300'
        }
      }}
    >
      {/* Comment Header */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
        <Avatar sx={{ width: 32, height: 32, mr: 1.5, bgcolor: 'primary.main' }}>
          <PersonIcon fontSize="small" />
        </Avatar>

        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {comment.user_name || 'User'}
            </Typography>

            <Typography variant="caption" color="text.secondary">
              {timestamp}
            </Typography>

            {isEdited && (
              <Chip
                label="Edited"
                size="small"
                sx={{
                  height: 18,
                  fontSize: '0.7rem',
                  backgroundColor: 'grey.300',
                  color: 'text.secondary'
                }}
              />
            )}
          </Box>
        </Box>

        {/* Edit/Delete Actions */}
        {!isEditing && (canEdit || canDelete) && (
          <CommentActions
            onEdit={canEdit ? handleEdit : null}
            onDelete={canDelete ? handleDelete : null}
            isDeleting={isDeleting}
          />
        )}
      </Box>

      {/* Comment Content or Edit Form */}
      {isEditing ? (
        <Box sx={{ mt: 1 }}>
          <CommentForm
            initialValue={comment.content}
            onSubmit={handleSaveEdit}
            onCancel={handleCancelEdit}
            isEdit
          />
        </Box>
      ) : (
        <Typography
          variant="body2"
          sx={{
            ml: 5,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}
        >
          {comment.content}
        </Typography>
      )}
    </Paper>
  )
}

export default CommentItem
