import { Box, Typography, Skeleton } from '@mui/material'
import CommentIcon from '@mui/icons-material/Comment'
import CommentItem from './CommentItem'

/**
 * CommentList Component
 * Displays a list of comments
 */
const CommentList = ({ comments, loading, currentUser, onEdit, onDelete }) => {
  // Loading state
  if (loading) {
    return (
      <Box>
        {[1, 2, 3].map((i) => (
          <Box key={i} sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Skeleton variant="circular" width={32} height={32} sx={{ mr: 1.5 }} />
              <Skeleton variant="text" width={150} />
            </Box>
            <Skeleton variant="rectangular" height={60} sx={{ ml: 5 }} />
          </Box>
        ))}
      </Box>
    )
  }

  // Empty state
  if (!comments || comments.length === 0) {
    return (
      <Box
        sx={{
          textAlign: 'center',
          py: 4,
          color: 'text.secondary'
        }}
      >
        <CommentIcon sx={{ fontSize: 48, mb: 1, opacity: 0.3 }} />
        <Typography variant="body2">No comments yet</Typography>
        <Typography variant="caption">Be the first to comment!</Typography>
      </Box>
    )
  }

  // Render comments
  return (
    <Box>
      {comments.map((comment) => (
        <CommentItem
          key={comment.id}
          comment={comment}
          currentUser={currentUser}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </Box>
  )
}

export default CommentList
