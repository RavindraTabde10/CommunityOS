import { Box, Container, Paper, Typography } from '@mui/material'
import { APP_NAME, APP_VERSION } from '../../utils/constants'
import loginBackground from '../../images/RG_connect_login_page.jpg'

/**
 * Auth layout for login/register pages with enhanced UI
 */
const AuthLayout = ({ children }) => {
  const currentYear = new Date().getFullYear()

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundImage: `url(${loginBackground})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        py: 4,
        px: { xs: 2, md: 1 },
        position: 'relative',
        animation: 'fadeIn 0.6s ease-in',
        '@keyframes fadeIn': {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(to bottom, rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.4) 100%)',
          pointerEvents: 'none',
        },
      }}
    >
      <Container 
        maxWidth="sm" 
        sx={{ 
          position: 'relative', 
          zIndex: 1,
          ml: { xs: 0, md: '50%' },
          mr: { xs: 0, md: '5%' },
        }}
      >
        <Paper
          elevation={24}
          sx={{
            p: 4,
            borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.92)',
            backdropFilter: 'blur(20px)',
            border: '2px solid rgba(255, 255, 255, 0.6)',
            boxShadow: `
              0 8px 32px rgba(0, 0, 0, 0.15),
              0 2px 8px rgba(0, 0, 0, 0.1),
              inset 0 1px 1px rgba(255, 255, 255, 0.8)
            `,
            position: 'relative',
            animation: 'floatIn 0.8s ease-out, float 3s ease-in-out infinite',
            '@keyframes floatIn': {
              from: { 
                opacity: 0,
                transform: 'translateY(30px) scale(0.95)',
              },
              to: { 
                opacity: 1,
                transform: 'translateY(0) scale(1)',
              },
            },
            '@keyframes float': {
              '0%, 100%': { transform: 'translateY(0px)' },
              '50%': { transform: 'translateY(-8px)' },
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: -2,
              left: -2,
              right: -2,
              bottom: -2,
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3))',
              borderRadius: 4,
              zIndex: -1,
              opacity: 0,
              transition: 'opacity 0.3s ease',
            },
            '&:hover::before': {
              opacity: 1,
            },
          }}
        >
          {children}
        </Paper>

        {/* Footer Information */}
        <Box
          sx={{
            mt: 3,
            textAlign: 'center',
            animation: 'fadeIn 1s ease-in 0.3s both',
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: 'white',
              textShadow: '1px 1px 3px rgba(0, 0, 0, 0.5)',
              mb: 0.5,
              fontSize: '0.875rem',
            }}
          >
            © {currentYear} {APP_NAME} • Version {APP_VERSION}
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              textShadow: '1px 1px 3px rgba(0, 0, 0, 0.5)',
              fontSize: '0.75rem',
            }}
          >
            Powered by CommunityOS.ai
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}

export default AuthLayout
