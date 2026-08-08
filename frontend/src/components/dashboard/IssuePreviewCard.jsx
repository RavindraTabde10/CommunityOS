import { Card, CardContent, Typography, Box, Chip, IconButton } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import PropTypes from 'prop-types'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'

/**
 * Format date to readable string
 */
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

/**
 * IssuePreviewCard Component
 * Displays a compact preview of an issue
 */
const IssuePreviewCard = ({ issue }) => {
  const navigate = useNavigate()

  const statusColors = {
    open: 'error',
    in_progress: 'warning',
    resolved: 'success',
    closed: 'default',
  }

  const priorityColors = {
    low: 'default',
    medium: 'info',
    high: 'warning',
    critical: 'error',
  }

  const handleClick = () => {
    navigate(`/issues/${issue.id}`)
  }

  return (
    <Card
      sx={{
        cursor: 'pointer',
        background: 'rgba(255, 255, 255, 0.98)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.12)',
        },
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" fontWeight="bold" color="primary" sx={{ fontSize: '0.75rem' }}>
              {issue.id}
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.25 }} noWrap>
              {issue.title}
            </Typography>
          </Box>
          <IconButton size="small" color="primary" sx={{ p: 0.5 }}>
            <ArrowForwardIcon fontSize="small" />
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          <Chip
            label={issue.status?.replace('_', ' ').toUpperCase()}
            color={statusColors[issue.status] || 'default'}
            size="small"
            sx={{ height: 20, fontSize: '0.65rem' }}
          />
          <Chip
            label={issue.priority?.toUpperCase()}
            color={priorityColors[issue.priority] || 'default'}
            size="small"
            variant="outlined"
            sx={{ height: 20, fontSize: '0.65rem' }}
          />
          <Chip
            label={issue.category?.toUpperCase()}
            size="small"
            variant="outlined"
            sx={{ height: 20, fontSize: '0.65rem' }}
          />
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
            {issue.location && `📍 ${issue.location}`}
            {issue.unit_number && ` • Unit ${issue.unit_number}`}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
            {issue.created_at && formatDate(issue.created_at)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

IssuePreviewCard.propTypes = {
  issue: PropTypes.shape({
    id: PropTypes.string.isRequired,
    issue_number: PropTypes.string,
    title: PropTypes.string.isRequired,
    description: PropTypes.string,
    status: PropTypes.string.isRequired,
    priority: PropTypes.string.isRequired,
    category: PropTypes.string.isRequired,
    location: PropTypes.string,
    unit_number: PropTypes.string,
    created_at: PropTypes.string,
  }).isRequired,
}

export default IssuePreviewCard
