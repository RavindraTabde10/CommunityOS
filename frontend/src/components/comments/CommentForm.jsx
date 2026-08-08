import { useState } from 'react'
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress
} from '@mui/material'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { commentSchema } from '../../schemas/commentSchema'
import { toast } from 'react-toastify'

/**
 * CommentForm Component
 * Form for adding or editing comments
 */
const CommentForm = ({
  onSubmit,
  onCancel,
  initialValue = '',
  isEdit = false
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(commentSchema),
    defaultValues: {
      content: initialValue
    }
  })

  const content = watch('content', initialValue)
  const characterCount = content?.length || 0
  const maxCharacters = 2000

  const handleFormSubmit = async (data) => {
    try {
      setIsSubmitting(true)
      await onSubmit(data.content)
      
      if (!isEdit) {
        reset() // Clear form after adding new comment
      }
      
      toast.success(isEdit ? 'Comment updated!' : 'Comment added!')
    } catch (error) {
      toast.error(
        error.response?.data?.detail || 
        (isEdit ? 'Failed to update comment' : 'Failed to add comment')
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    if (isEdit) {
      onCancel?.()
    } else {
      reset()
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <TextField
        {...register('content')}
        multiline
        rows={isEdit ? 3 : 4}
        fullWidth
        placeholder={isEdit ? 'Edit your comment...' : 'Add a comment...'}
        error={!!errors.content}
        helperText={errors.content?.message}
        disabled={isSubmitting}
        sx={{
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'white'
          }
        }}
      />

      {/* Character Count */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
        <Typography
          variant="caption"
          color={characterCount > maxCharacters ? 'error' : 'text.secondary'}
        >
          {characterCount} / {maxCharacters}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {(isEdit || content) && (
            <Button
              variant="outlined"
              size="small"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}

          <Button
            type="submit"
            variant="contained"
            size="small"
            disabled={isSubmitting || !content?.trim() || characterCount > maxCharacters}
            startIcon={isSubmitting && <CircularProgress size={16} />}
          >
            {isSubmitting ? 'Saving...' : (isEdit ? 'Save' : 'Comment')}
          </Button>
        </Box>
      </Box>
    </Box>
  )
}

export default CommentForm
