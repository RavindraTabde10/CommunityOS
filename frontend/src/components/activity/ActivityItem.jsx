import { Box, Typography, Paper, Chip } from '@mui/material'
import { formatDistanceToNow } from 'date-fns'
import ActivityIcon from './ActivityIcon'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'

/**
 * ActivityItem Component
 * Displays a single activity entry in the timeline
 */
const ActivityItem = ({ activity }) => {
  const timestamp = activity.created_at
    ? formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })
    : 'just now'

  // Show field changes if available
  const hasFieldChange = activity.field_name && (activity.old_value || activity.new_value)

  return (
    <Box sx={{ display: 'flex', gap: 2, position: 'relative', pb: 3 }}>
      {/* Icon */}
      <Box
        sx={{
          width: 40,
          height: 40,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'background.paper',
          border: '2px solid',
          borderColor: 'grey.300',
          flexShrink: 0,
          zIndex: 1
        }}
      >
        <ActivityIcon activityType={activity.action} />
      </Box>

      {/* Vertical line connecting to next item */}
      <Box
        sx={{
          position: 'absolute',
          left: 19,
          top: 40,
          bottom: -12,
          width: 2,
          backgroundColor: 'grey.200'
        }}
      />

      {/* Content */}
      <Box sx={{ flex: 1, pt: 0.5 }}>
        <Paper
          elevation={0}
          sx={{
            p: 2,
            backgroundColor: 'grey.50',
            border: '1px solid',
            borderColor: 'grey.200'
          }}
        >
          {/* Description */}
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            {activity.description}
          </Typography>

          {/* Field Changes */}
          {hasFieldChange && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mt: 1,
                flexWrap: 'wrap'
              }}
            >
              <Typography variant="caption" color="text.secondary">
                {activity.field_name}:
              </Typography>

              {activity.old_value && (
                <Chip
                  label={activity.old_value}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.7rem',
                    backgroundColor: 'grey.300',
                    textDecoration: 'line-through'
                  }}
                />
              )}

              {activity.old_value && activity.new_value && (
                <ArrowForwardIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
              )}

              {activity.new_value && (
                <Chip
                  label={activity.new_value}
                  size="small"
                  color="primary"
                  sx={{
                    height: 20,
                    fontSize: '0.7rem'
                  }}
                />
              )}
            </Box>
          )}

          {/* Timestamp */}
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            {timestamp}
          </Typography>
        </Paper>
      </Box>
    </Box>
  )
}

export default ActivityItem
