import { Box, IconButton, Tooltip, CircularProgress } from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'

/**
 * CommentActions Component
 * Edit and delete buttons for comments
 */
const CommentActions = ({ onEdit, onDelete, isDeleting }) => {
  return (
    <Box sx={{ display: 'flex', gap: 0.5 }}>
      {onEdit && (
        <Tooltip title="Edit comment">
          <IconButton
            size="small"
            onClick={onEdit}
            sx={{
              '&:hover': {
                color: 'primary.main'
              }
            }}
          >
            <EditIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}

      {onDelete && (
        <Tooltip title="Delete comment">
          <IconButton
            size="small"
            onClick={onDelete}
            disabled={isDeleting}
            sx={{
              '&:hover': {
                color: 'error.main'
              }
            }}
          >
            {isDeleting ? (
              <CircularProgress size={16} />
            ) : (
              <DeleteIcon fontSize="small" />
            )}
          </IconButton>
        </Tooltip>
      )}
    </Box>
  )
}

export default CommentActions
