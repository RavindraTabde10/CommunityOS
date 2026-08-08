import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material'
import TimelineIcon from '@mui/icons-material/Timeline'
import { toast } from 'react-toastify'
import { getActivityLog } from '../../api/activityService'
import ActivityItem from './ActivityItem'

/**
 * ActivityTimeline Component
 * Displays chronological activity log for an issue
 */
const ActivityTimeline = ({ issueId }) => {
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchActivities()
  }, [issueId])

  const fetchActivities = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getActivityLog(issueId)
      setActivities(data.activities || [])
    } catch (err) {
      console.error('Error fetching activity log:', err)
      setError('Failed to load activity log')
    } finally {
      setLoading(false)
    }
  }

  // Loading state
  if (loading) {
    return (
      <Paper elevation={0} sx={{ p: 3, mt: 3, border: '1px solid', borderColor: 'grey.200' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Activity Timeline</Typography>
        </Box>
        <Divider sx={{ mb: 3 }} />
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Paper>
    )
  }

  // Error state
  if (error) {
    return (
      <Paper elevation={0} sx={{ p: 3, mt: 3, border: '1px solid', borderColor: 'grey.200' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Activity Timeline</Typography>
        </Box>
        <Divider sx={{ mb: 3 }} />
        <Alert severity="error">{error}</Alert>
      </Paper>
    )
  }

  // Empty state
  if (!activities || activities.length === 0) {
    return (
      <Paper elevation={0} sx={{ p: 3, mt: 3, border: '1px solid', borderColor: 'grey.200' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Activity Timeline</Typography>
        </Box>
        <Divider sx={{ mb: 3 }} />
        <Box
          sx={{
            textAlign: 'center',
            py: 4,
            color: 'text.secondary'
          }}
        >
          <TimelineIcon sx={{ fontSize: 48, mb: 1, opacity: 0.3 }} />
          <Typography variant="body2">No activity yet</Typography>
        </Box>
      </Paper>
    )
  }

  // Render timeline
  return (
    <Paper elevation={0} sx={{ p: 3, mt: 3, border: '1px solid', borderColor: 'grey.200' }}>
      {/* Section Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">
          Activity Timeline ({activities.length})
        </Typography>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Activity Items */}
      <Box>
        {activities.map((activity, index) => (
          <Box key={activity.id || index}>
            <ActivityItem activity={activity} />
          </Box>
        ))}
      </Box>
    </Paper>
  )
}

export default ActivityTimeline
