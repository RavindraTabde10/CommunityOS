/**
 * Committee Member Card Component
 * Displays committee member information with contact options
 */
import { Card, CardContent, Typography, Box, Avatar, Chip, IconButton, Tooltip } from '@mui/material'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'
import { getRoleLabel, getRoleIcon } from '../../constants/committee'

const CommitteeMemberCard = ({ member, compact = false }) => {
  const roleIcon = getRoleIcon(member.role)
  const roleLabel = getRoleLabel(member.role)

  // Compact view for sidebar
  if (compact) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 0.75,
          py: 0.4,
          px: 0.5,
          borderRadius: 1,
          '&:hover': { 
            bgcolor: 'action.hover',
            '& .email-btn': { opacity: 1 }
          }
        }}
      >
        <Avatar 
          sx={{ width: 24, height: 24, bgcolor: 'primary.main', fontSize: '0.7rem', fontWeight: 'bold', flexShrink: 0 }}
        >
          {member.user_name?.charAt(0).toUpperCase() || '?'}
        </Avatar>

        <Box sx={{ minWidth: 0 }}>
          <Typography noWrap sx={{ fontSize: '0.75rem', fontWeight: 600, lineHeight: 1.2 }}>
            {member.user_name}
          </Typography>
          <Typography noWrap sx={{ fontSize: '0.65rem', color: 'text.secondary', lineHeight: 1.2 }}>
            {roleIcon} {roleLabel}
          </Typography>
        </Box>

        {member.contact_email && (
          <Tooltip title={member.contact_email}>
            <IconButton 
              className="email-btn"
              size="small" color="primary" 
              sx={{ p: 0.25, ml: 'auto', opacity: 0, transition: 'opacity 0.15s' }}
              onClick={() => window.location.href = `mailto:${member.contact_email}`}
            >
              <EmailIcon sx={{ fontSize: 12 }} />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    )
  }

  // Full view for main display
  return (
    <Card 
      elevation={2}
      sx={{ 
        height: '100%',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6
        }
      }}
    >
      <CardContent sx={{ textAlign: 'center', p: 3 }}>
        {/* Avatar */}
        <Box sx={{ mb: 2 }}>
          <Avatar 
            sx={{ 
              width: 80, 
              height: 80, 
              margin: '0 auto',
              bgcolor: 'primary.main',
              fontSize: '2rem',
              fontWeight: 'bold'
            }}
          >
            {member.user_name?.charAt(0).toUpperCase() || '?'}
          </Avatar>
        </Box>

        {/* Name */}
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          {member.user_name}
        </Typography>

        {/* Role with Icon */}
        <Chip 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span>{roleIcon}</span>
              <span>{roleLabel}</span>
            </Box>
          }
          color="primary"
          variant="outlined"
          sx={{ mb: 2, fontWeight: 600 }}
        />

        {/* Position Name (if different from role) */}
        {member.position_name && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontStyle: 'italic' }}>
            {member.position_name}
          </Typography>
        )}

        {/* Responsibilities */}
        {member.responsibilities && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontSize: '0.85rem' }}>
            {member.responsibilities}
          </Typography>
        )}

        {/* Contact Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
          {member.contact_email && (
            <Tooltip title={member.contact_email}>
              <IconButton 
                size="small" 
                color="primary"
                onClick={() => window.location.href = `mailto:${member.contact_email}`}
              >
                <EmailIcon />
              </IconButton>
            </Tooltip>
          )}
          {member.contact_phone && (
            <Tooltip title={member.contact_phone}>
              <IconButton 
                size="small" 
                color="primary"
                onClick={() => window.location.href = `tel:${member.contact_phone}`}
              >
                <PhoneIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </CardContent>
    </Card>
  )
}

export default CommitteeMemberCard
