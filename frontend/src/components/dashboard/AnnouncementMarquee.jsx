/**
 * AnnouncementMarquee Component
 * Displays active announcements as scrolling/moving text on the dashboard
 */

import { useState, useEffect } from 'react'
import { Box, Typography, Paper, Chip } from '@mui/material'
import { keyframes } from '@mui/system'
import CampaignIcon from '@mui/icons-material/Campaign'
import announcementService from '../../api/announcementService'
import { getPriorityColor } from '../../constants/announcements'

// Seamless continuous scrolling animation
const scrollText = keyframes`
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
`

/**
 * Marquee component showing active announcements
 */
const AnnouncementMarquee = () => {
  const [announcements, setAnnouncements] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadActiveAnnouncements()
    // Refresh every 5 minutes
    const interval = setInterval(loadActiveAnnouncements, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const loadActiveAnnouncements = async () => {
    try {
      const data = await announcementService.getActiveAnnouncements()
      setAnnouncements(data)
    } catch (error) {
      console.error('Error loading announcements:', error)
    } finally {
      setLoading(false)
    }
  }

  // Don't render if no announcements
  if (loading || announcements.length === 0) {
    return null
  }

  return (
    <Paper
      elevation={3}
      sx={{
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%)',
        border: '2px solid rgba(255, 215, 0, 0.3)',
        borderRadius: 2,
        position: 'relative',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'linear-gradient(90deg, #ffd700, #ffed4e, #ffd700)',
          animation: 'shimmer 2s infinite',
        },
        '@keyframes shimmer': {
          '0%, 100%': { opacity: 0.8 },
          '50%': { opacity: 1 },
        }
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 1.5,
          py: 1,
          gap: 1.5
        }}
      >
        {/* Icon */}
        <CampaignIcon 
          sx={{ 
            color: '#ffd700', 
            fontSize: 28, 
            flexShrink: 0,
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))',
            animation: 'pulse 2s infinite'
          }} 
        />
        
        {/* Scrolling container */}
        <Box
          sx={{
            flex: 1,
            overflow: 'hidden',
            position: 'relative',
            minHeight: '32px',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              animation: `${scrollText} ${announcements.length * 15}s linear infinite`,
              whiteSpace: 'nowrap'
            }}
          >
            {/* Render twice for seamless looping */}
            {[0, 1].map((copy) =>
              announcements.map((announcement, index) => (
                <Box key={`${copy}-${announcement.id}`} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Chip
                    label={announcement.priority.toUpperCase()}
                    size="small"
                    color={getPriorityColor(announcement.priority)}
                    sx={{ 
                      fontWeight: 700,
                      fontSize: '0.65rem',
                      px: 0.5,
                      height: 20,
                      textTransform: 'uppercase',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                    }}
                  />
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      fontSize: '0.9rem',
                      color: '#ffffff',
                      textShadow: '1px 1px 3px rgba(0, 0, 0, 0.4)',
                      letterSpacing: '0.3px'
                    }}
                  >
                    {announcement.title}: {announcement.content}
                  </Typography>
                  <Typography 
                    sx={{ 
                      mx: 3, 
                      color: '#ffd700',
                      fontSize: '1.5rem',
                      fontWeight: 'bold'
                    }}
                  >
                    ★
                  </Typography>
                </Box>
              ))
            )}
          </Box>
        </Box>
      </Box>
    </Paper>
  )
}

export default AnnouncementMarquee
