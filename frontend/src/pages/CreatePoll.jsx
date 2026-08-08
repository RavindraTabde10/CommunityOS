/**
 * Create Poll Page
 * Admin-only page for creating community polls
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Grid,
  Alert,
  IconButton,
} from '@mui/material'
import { ArrowBack as ArrowBackIcon, Save as SaveIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { toast } from 'react-toastify'
import { USER_ROLES } from '../constants/roles'
import { pollsAPI } from '../api/polls'

const MIN_OPTIONS = 2
const MAX_OPTIONS = 6

const CreatePoll = () => {
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)

  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})
  const [formData, setFormData] = useState({
    question: '',
    description: '',
    is_active: true,
    active_till: '',
    options: ['', '']
  })

  useEffect(() => {
    if (user && user.role !== USER_ROLES.ADMIN) {
      toast.error('Access denied. Admin privileges required.')
      navigate('/polls')
    }
  }, [user, navigate])

  const handleChange = (event) => {
    const { name, value, checked } = event.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'is_active' ? checked : value
    }))

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const handleOptionChange = (index, value) => {
    setFormData((prev) => ({
      ...prev,
      options: prev.options.map((option, optionIndex) =>
        optionIndex === index ? value : option
      )
    }))
  }

  const addOption = () => {
    if (formData.options.length >= MAX_OPTIONS) {
      toast.info(`A maximum of ${MAX_OPTIONS} options is allowed`)
      return
    }

    setFormData((prev) => ({
      ...prev,
      options: [...prev.options, '']
    }))
  }

  const removeOption = (index) => {
    if (formData.options.length <= MIN_OPTIONS) {
      toast.info(`At least ${MIN_OPTIONS} options are required`)
      return
    }

    setFormData((prev) => ({
      ...prev,
      options: prev.options.filter((_, optionIndex) => optionIndex !== index)
    }))
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.question.trim()) {
      newErrors.question = 'Poll question is required'
    }

    const cleanedOptions = formData.options.map((option) => option.trim())
    const emptyOptions = cleanedOptions.filter((option) => !option)

    if (emptyOptions.length > 0) {
      newErrors.options = 'All option fields must be filled'
    }

    const uniqueOptionsCount = new Set(cleanedOptions.map((option) => option.toLowerCase())).size
    if (uniqueOptionsCount !== cleanedOptions.length) {
      newErrors.options = 'Options must be unique'
    }

    if (cleanedOptions.length < MIN_OPTIONS) {
      newErrors.options = `At least ${MIN_OPTIONS} options are required`
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!validateForm()) {
      toast.error('Please fix the errors in the form')
      return
    }

    try {
      setLoading(true)

      await pollsAPI.create({
        question: formData.question.trim(),
        description: formData.description.trim() || null,
        options: formData.options.map((option) => option.trim()),
        is_active: formData.is_active,
        active_till: formData.active_till || null,
      })

      toast.success('Poll created successfully')
      navigate('/polls')
    } catch (error) {
      console.error('Error creating poll:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create poll'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/polls')}>
          Back
        </Button>
        <Typography variant="h4" fontWeight="bold">
          Create Poll
        </Typography>
      </Box>

      <Paper sx={{ p: 3, maxWidth: 900 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                name="question"
                label="Poll Question"
                value={formData.question}
                onChange={handleChange}
                error={Boolean(errors.question)}
                helperText={errors.question}
                placeholder="e.g., Should we host a cultural fest in October?"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                name="description"
                label="Description (Optional)"
                value={formData.description}
                onChange={handleChange}
                placeholder="Provide additional context for residents..."
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Poll Options
              </Typography>

              {formData.options.map((option, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1.5 }}>
                  <TextField
                    fullWidth
                    required
                    label={`Option ${index + 1}`}
                    value={option}
                    onChange={(e) => handleOptionChange(index, e.target.value)}
                    placeholder={`Enter option ${index + 1}`}
                  />
                  <IconButton
                    color="error"
                    onClick={() => removeOption(index)}
                    sx={{ alignSelf: 'center' }}
                    aria-label={`remove option ${index + 1}`}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}

              {errors.options && (
                <Typography variant="body2" color="error" sx={{ mt: 0.5 }}>
                  {errors.options}
                </Typography>
              )}

              <Button variant="outlined" onClick={addOption} sx={{ mt: 1 }}>
                Add Option
              </Button>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                    color="primary"
                  />
                }
                label="Active (poll will be visible to residents)"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="datetime-local"
                name="active_till"
                label="Active Till (Optional)"
                value={formData.active_till}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
                helperText="Leave blank for no expiry"
              />
            </Grid>

            <Grid item xs={12}>
              <Alert severity="info">
                Polls are now saved to the backend and shared across authenticated users.
              </Alert>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => navigate('/polls')} disabled={loading}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" startIcon={<SaveIcon />} disabled={loading}>
                  {loading ? 'Creating...' : 'Create Poll'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  )
}

export default CreatePoll
