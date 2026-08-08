import { useState } from 'react'
import { AppBar as MuiAppBar, Toolbar, IconButton, Typography, Box } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import UserMenu from './UserMenu'
import { APP_NAME } from '../../utils/constants'

/**
 * Top app bar component
 */
const AppBar = ({ onMenuClick }) => {
  return (
    <MuiAppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        bgcolor: 'white',
        color: 'text.primary',
        boxShadow: 1,
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <img
            src="/logo.png"
            alt={APP_NAME}
            style={{ height: 40, marginRight: 12 }}
            onError={(e) => {
              e.target.style.display = 'none'
            }}
          />
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ fontWeight: 600, color: 'primary.main' }}
          >
            {APP_NAME}
          </Typography>
        </Box>

        <UserMenu />
      </Toolbar>
    </MuiAppBar>
  )
}

export default AppBar
