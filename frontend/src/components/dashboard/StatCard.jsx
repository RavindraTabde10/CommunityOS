import { Paper, Box, Typography, Skeleton } from '@mui/material'
import PropTypes from 'prop-types'

/**
 * StatCard Component
 * Displays a statistic with icon, label, and value
 */
const StatCard = ({ icon: Icon, label, value, color = 'primary', isLoading = false }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        p: 1.5,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.7rem' }}>
            {label}
          </Typography>
          {isLoading ? (
            <Skeleton variant="text" width={40} height={28} />
          ) : (
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
              {value}
            </Typography>
          )}
        </Box>
        {Icon && (
          <Box
            sx={{
              backgroundColor: `${color}.light`,
              borderRadius: 1.5,
              p: 0.75,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ fontSize: 24, color: `${color}.main` }} />
          </Box>
        )}
      </Box>
    </Paper>
  )
}

StatCard.propTypes = {
  icon: PropTypes.elementType,
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  color: PropTypes.oneOf(['primary', 'secondary', 'success', 'error', 'warning', 'info']),
  isLoading: PropTypes.bool,
}

export default StatCard
