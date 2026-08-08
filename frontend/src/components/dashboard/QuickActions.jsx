import { Paper, Box, Typography, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import AddIcon from '@mui/icons-material/Add'
import ListIcon from '@mui/icons-material/List'
import PollIcon from '@mui/icons-material/Poll'
import GppGoodIcon from '@mui/icons-material/GppGood'
import { ROUTES } from '../../utils/constants'
import { useAuth } from '../../hooks/useAuth'
import { USER_ROLES } from '../../constants/roles'

/**
 * QuickActions Component
 * Displays quick action buttons for common tasks
 */
const QuickActions = ({ onEditGuidelines }) => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === USER_ROLES.ADMIN

  const actions = [
    {
      label: 'Create Issue',
      icon: <AddIcon />,
      color: 'primary',
      path: ROUTES.ISSUES_CREATE,
    },
    {
      label: 'View All Issues',
      icon: <ListIcon />,
      color: 'secondary',
      path: ROUTES.ISSUES,
    },
    {
      label: 'Create Poll',
      icon: <PollIcon />,
      color: 'primary',
      path: ROUTES.POLLS_CREATE,
    },
    {
      label: 'View All Polls',
      icon: <ListIcon />,
      color: 'secondary',
      path: ROUTES.POLLS,
    },
  ]

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 1.5,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
      }}
    >
      <Typography variant="body1" fontWeight="bold" sx={{ mb: 0.75 }}>
        Quick Actions
      </Typography>
      <Box sx={{ display: 'flex', gap: 0.5, flexDirection: 'column' }}>
        {actions.map((action) => (
          <Button
            key={action.label}
            variant="contained"
            color={action.color}
            startIcon={action.icon}
            onClick={() => navigate(action.path)}
            fullWidth
            size="small"
            sx={{ py: 0.5, fontSize: '0.8rem' }}
          >
            {action.label}
          </Button>
        ))}
      {/* Admin-only: Security Guidelines */}
        {isAdmin && onEditGuidelines && (
          <Button
            variant="contained"
            startIcon={<GppGoodIcon />}
            onClick={onEditGuidelines}
            fullWidth
            size="small"
            sx={{ py: 0.5, fontSize: '0.8rem', bgcolor: '#b71c1c', '&:hover': { bgcolor: '#7f0000' } }}
          >
            Security Guidelines
          </Button>
        )}
      </Box>
    </Paper>
  )
}

export default QuickActions
