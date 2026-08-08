import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material'
import { ArrowBack as ArrowBackIcon, Save as SaveIcon, Delete as DeleteIcon } from '@mui/icons-material'
import { toast } from 'react-toastify'
import { USER_ROLES } from '../constants/roles'
import { pollsAPI } from '../api/polls'

const MIN_OPTIONS = 2
const MAX_OPTIONS = 6

const EditPoll = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)

  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [fetchError, setFetchError] = useState(null)
  const [errors, setErrors] = useState({})
  const [formData, setFormData] = useState({
    question: '',
    description: '',
    is_active: true,
    active_till: '',
    options: ['', ''],
  })

  useEffect(() => {
    if (user && user.role !== USER_ROLES.ADMIN) {
      toast.error('Access denied. Admin privileges required.')
      navigate('/polls')
      return
    }
    loadPoll()
  }, [user])

  const loadPoll = async () => {
    try {
      setFetching(true)
      const response = await pollsAPI.getById(id)
      const poll = response.data
      setFormData({
        question: poll.question || '',
        description: poll.description || '',
        is_active: poll.is_active,
        active_till: poll.active_till ? poll.active_till.slice(0, 16) : '',
        options: poll.options?.length >= MIN_OPTIONS ? poll.options : ['', ''],
      })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to load poll'
      setFetchError(msg)
      toast.error(msg)
    } finally {
      setFetching(false)
    }
  }

  const handleChange = (event) => {
    const { name, value, checked } = event.target
    setFormData((prev) => ({ ...prev, [name]: name === 'is_active' ? checked : value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }))
  }

  const handleOptionChange = (index, value) => {
    setFormData((prev) => ({
      ...prev,
      options: prev.options.map((o, i) => (i === index ? value : o)),
    }))
  }

  const addOption = () => {
    if (formData.options.length >= MAX_OPTIONS) {
      toast.info(`Maximum ${MAX_OPTIONS} options allowed`)
      return
    }
    setFormData((prev) => ({ ...prev, options: [...prev.options, ''] }))
  }

  const removeOption = (index) => {
    if (formData.options.length <= MIN_OPTIONS) {
      toast.info(`At least ${MIN_OPTIONS} options required`)
      return
    }
    setFormData((prev) => ({ ...prev, options: prev.options.filter((_, i) => i !== index) }))
  }

  const validateForm = () => {
    const newErrors = {}
    if (!formData.question.trim()) newErrors.question = 'Poll question is required'

    const cleaned = formData.options.map((o) => o.trim())
    if (cleaned.some((o) => !o)) newErrors.options = 'All option fields must be filled'
    else if (new Set(cleaned.map((o) => o.toLowerCase())).size !== cleaned.length)
      newErrors.options = 'Options must be unique'
    else if (cleaned.length < MIN_OPTIONS)
      newErrors.options = `At least ${MIN_OPTIONS} options required`

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
      await pollsAPI.update(id, {
        question: formData.question.trim(),
        description: formData.description.trim() || null,
        options: formData.options.map((o) => o.trim()),
        is_active: formData.is_active,
        active_till: formData.active_till || null,
      })
      toast.success('Poll updated successfully')
      navigate('/polls')
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message || 'Failed to update poll')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (fetchError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{fetchError}</Alert>
        <Button sx={{ mt: 2 }} onClick={() => navigate('/polls')}>Back to Polls</Button>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/polls')}>
          Back
        </Button>
        <Typography variant="h4" fontWeight="bold">
          Edit Poll
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
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => navigate('/polls')} disabled={loading}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" startIcon={<SaveIcon />} disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  )
}

export default EditPoll
