import { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Box,
  TextField,
  MenuItem,
  Button,
  Grid,
  Typography,
  InputAdornment,
} from '@mui/material'
import SaveIcon from '@mui/icons-material/Save'
import PersonIcon from '@mui/icons-material/Person'
import PropTypes from 'prop-types'
import { issueSchema, CATEGORY_OPTIONS, PRIORITY_OPTIONS } from '../../schemas/issueSchema'
import PhotoUpload from '../common/PhotoUpload'
import { useAuth } from '../../hooks/useAuth'
import userService from '../../api/userService'

/**
 * IssueForm Component
 * Reusable form for creating and editing issues
 */
const IssueForm = ({ 
  defaultValues, 
  onSubmit, 
  isSubmitting = false,
  submitButtonText = 'Create Issue',
  mode = 'create',
  reporterInfo = null,
}) => {
  const [photos, setPhotos] = useState([])
  const [users, setUsers] = useState([])
  const { user } = useAuth()

  const canAssign = user && ['admin', 'facility'].includes(user.role)

  useEffect(() => {
    if (canAssign) {
      userService.getUsers({ limit: 100 })
        .then(data => setUsers(Array.isArray(data) ? data : (data.users || [])))
        .catch(() => setUsers([]))
    }
  }, [canAssign])

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(issueSchema),
    defaultValues: defaultValues || {
      title: '',
      description: '',
      category: '',
      priority: 'medium',
      location: '',
      unit_number: '',
      assigned_to: '',
    },
  })

  const onFormSubmit = (data) => {
    // Pass both form data and photos to parent
    onSubmit({ formData: data, photos })
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onFormSubmit)} noValidate>
      <Grid container spacing={3}>
        {/* Title */}
        <Grid item xs={12}>
          <Controller
            name="title"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Issue Title"
                required
                fullWidth
                error={!!errors.title}
                helperText={errors.title?.message || 'Brief description of the issue (10-200 characters)'}
                placeholder="e.g., Water leakage in bathroom"
              />
            )}
          />
        </Grid>

        {/* Description */}
        <Grid item xs={12}>
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Description"
                required
                fullWidth
                multiline
                rows={4}
                error={!!errors.description}
                helperText={errors.description?.message || 'Detailed description of the issue (20-2000 characters)'}
                placeholder="Describe the issue in detail..."
              />
            )}
          />
        </Grid>

        {/* Category and Priority */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="category"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Category"
                required
                fullWidth
                select
                error={!!errors.category}
                helperText={errors.category?.message || 'Select the issue category'}
              >
                <MenuItem value="">
                  <em>Select a category</em>
                </MenuItem>
                {CATEGORY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="priority"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Priority"
                required
                fullWidth
                select
                error={!!errors.priority}
                helperText={errors.priority?.message || 'Set the priority level'}
              >
                {PRIORITY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Box>
                      <Typography variant="body1">{option.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {option.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            )}
          />
        </Grid>

        {/* Location and Unit Number */}
        <Grid item xs={12} sm={6}>
          <Controller
            name="location"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Location"
                fullWidth
                error={!!errors.location}
                helperText={errors.location?.message || 'e.g., Building A, 3rd Floor'}
                placeholder="Building, floor, area..."
              />
            )}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <Controller
            name="unit_number"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                label="Unit Number"
                fullWidth
                error={!!errors.unit_number}
                helperText={errors.unit_number?.message || 'e.g., A-301'}
                placeholder="Your unit/flat number"
              />
            )}
          />
        </Grid>

        {/* Reporter (read-only display) */}
        {(mode === 'edit' && reporterInfo) && (
          <Grid item xs={12} sm={6}>
            <TextField
              label="Reporter"
              fullWidth
              value={reporterInfo.name || reporterInfo.email || ''}
              InputProps={{
                readOnly: true,
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonIcon fontSize="small" color="action" />
                  </InputAdornment>
                ),
              }}
              helperText="Issue reported by"
              sx={{ '& .MuiInputBase-root': { backgroundColor: 'action.hover' } }}
            />
          </Grid>
        )}

        {/* Assignee (admin/facility only) */}
        {canAssign && (
          <Grid item xs={12} sm={mode === 'edit' && reporterInfo ? 6 : 12}>
            <Controller
              name="assigned_to"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Assignee"
                  fullWidth
                  select
                  error={!!errors.assigned_to}
                  helperText={errors.assigned_to?.message || 'Assign issue to a team member (optional)'}
                  value={field.value || ''}
                >
                  <MenuItem value="">
                    <em>Unassigned</em>
                  </MenuItem>
                  {users.map((u) => (
                    <MenuItem key={u.id} value={u.id}>
                      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="body2">{u.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {u.email} · {u.role}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>
        )}

        {/* Photo Upload */}
        <Grid item xs={12}>
          <PhotoUpload photos={photos} onPhotosChange={setPhotos} />
        </Grid>

        {/* Submit Button */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              startIcon={<SaveIcon />}
              disabled={isSubmitting}
              sx={{ minWidth: 200 }}
            >
              {isSubmitting ? 'Saving...' : submitButtonText}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

IssueForm.propTypes = {
  defaultValues: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool,
  submitButtonText: PropTypes.string,
  mode: PropTypes.oneOf(['create', 'edit']),
  reporterInfo: PropTypes.shape({
    name: PropTypes.string,
    email: PropTypes.string,
  }),
}

export default IssueForm
