import { Paper, Typography, Box, Button, Divider } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import LocalHospitalIcon from '@mui/icons-material/LocalHospital'
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment'
import SupportAgentIcon from '@mui/icons-material/SupportAgent'
import PlumbingIcon from '@mui/icons-material/Plumbing'
import ElectricalServicesIcon from '@mui/icons-material/ElectricalServices'
import PhoneIcon from '@mui/icons-material/Phone'
import ContactPhoneIcon from '@mui/icons-material/ContactPhone'
import ContactsIcon from '@mui/icons-material/Contacts'
import { ROUTES } from '../../utils/constants'

const ContactsSection = () => {
  const navigate = useNavigate()
  const emergencyContacts = [
    { label: 'Fire Emergency', phone: '101', icon: <LocalFireDepartmentIcon />, color: '#f44336' },
    { label: 'Ambulance', phone: '108', icon: <LocalHospitalIcon />, color: '#2196f3' },
    { label: 'Quick Support', phone: '1800-XXX-XXXX', icon: <SupportAgentIcon />, color: '#ff9800' },
  ]

  const helperContacts = [
    { label: 'Plumber', phone: '9876543210', icon: <PlumbingIcon />, color: '#2196f3' },
    { label: 'Electrician', phone: '9876543211', icon: <ElectricalServicesIcon />, color: '#ff9800' },
  ]

  const additionalContacts = [
    { label: 'Security Office', phone: '9876543212' },
    { label: 'Maintenance', phone: '9876543213' },
    { label: 'Management Office', phone: '9876543214' },
  ]

  const ContactButton = ({ contact, isEmergency = false }) => (
    <Button
      fullWidth
      variant={isEmergency ? "contained" : "outlined"}
      startIcon={contact.icon || <PhoneIcon />}
      sx={{
        justifyContent: 'flex-start',
        py: 0.4,
        px: 1,
        mb: 0.4,
        textTransform: 'none',
        bgcolor: isEmergency ? contact.color : 'transparent',
        borderColor: contact.color || 'primary.main',
        color: isEmergency ? 'white' : contact.color || 'primary.main',
        minHeight: 0,
        height: 'auto',
        '&:hover': {
          bgcolor: isEmergency ? contact.color : `${contact.color || '#1976d2'}20`,
          borderColor: contact.color || 'primary.main',
        },
        transition: 'all 0.2s',
      }}
      onClick={() => window.open(`tel:${contact.phone}`)}
    >
      <Box sx={{ flex: 1, textAlign: 'left' }}>
        <Typography variant="caption" fontWeight="bold" sx={{ fontSize: '0.7rem', display: 'block', lineHeight: 1.2 }}>
          {contact.label}
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.85, fontSize: '0.65rem', lineHeight: 1.2 }}>
          {contact.phone}
        </Typography>
      </Box>
    </Button>
  )

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
      {/* Emergency Contacts */}
      <Box sx={{ mb: 1 }}>
        <Typography variant="body2" fontWeight="bold" sx={{ color: '#d32f2f', mb: 0.5, fontSize: '0.85rem' }}>
          🚨 Emergency
        </Typography>
        {emergencyContacts.map((contact, index) => (
          <ContactButton key={index} contact={contact} isEmergency />
        ))}
      </Box>

      <Divider sx={{ my: 0.75 }} />

      {/* Helper Contacts */}
      <Box sx={{ mb: 1 }}>
        <Typography variant="body2" fontWeight="bold" sx={{ mb: 0.5, fontSize: '0.85rem' }}>
          🔧 Helpers
        </Typography>
        {helperContacts.map((contact, index) => (
          <ContactButton key={index} contact={contact} />
        ))}
      </Box>

      <Divider sx={{ my: 0.75 }} />

      {/* Additional References */}
      <Box sx={{ mb: 1 }}>
        <Typography variant="body2" fontWeight="bold" sx={{ mb: 0.5, fontSize: '0.85rem' }}>
          📞 References
        </Typography>
        {additionalContacts.map((contact, index) => (
          <Button
            key={index}
            fullWidth
            variant="text"
            startIcon={<ContactPhoneIcon sx={{ fontSize: 14 }} />}
            sx={{
              justifyContent: 'flex-start',
              py: 0.3,
              px: 1,
              mb: 0.25,
              textTransform: 'none',
              color: 'text.primary',
              minHeight: 0,
              height: 'auto',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
            onClick={() => window.open(`tel:${contact.phone}`)}
          >
            <Box sx={{ flex: 1, textAlign: 'left' }}>
              <Typography variant="caption" fontWeight="500" sx={{ fontSize: '0.7rem', lineHeight: 1.2 }}>
                {contact.label}: {contact.phone}
              </Typography>
            </Box>
          </Button>
        ))}
      </Box>

      <Divider sx={{ my: 0.75 }} />

      {/* Resident Directory Link */}
      <Box>
        <Button
          fullWidth
          variant="contained"
          color="primary"
          startIcon={<ContactsIcon fontSize="small" />}
          onClick={() => navigate(ROUTES.RESIDENTS)}
          size="small"
          sx={{
            fontSize: '0.75rem',
            fontWeight: 600,
            py: 0.5,
            textTransform: 'none',
          }}
        >
          Resident Directory
        </Button>
      </Box>
    </Paper>
  )
}

export default ContactsSection
