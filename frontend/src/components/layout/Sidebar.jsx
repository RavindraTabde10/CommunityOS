import { useNavigate, useLocation } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  Box,
  Badge,
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import BugReportIcon from '@mui/icons-material/BugReport'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import PeopleIcon from '@mui/icons-material/People'
import HowToRegIcon from '@mui/icons-material/HowToReg'
import AssessmentIcon from '@mui/icons-material/Assessment'
import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import CampaignIcon from '@mui/icons-material/Campaign'
import GroupsIcon from '@mui/icons-material/Groups'
import ContactsIcon from '@mui/icons-material/Contacts'
import EventIcon from '@mui/icons-material/Event'
import PollIcon from '@mui/icons-material/Poll'
import FeedbackIcon from '@mui/icons-material/Feedback'
import SecurityIcon from '@mui/icons-material/Security'
import PersonPinCircleIcon from '@mui/icons-material/PersonPinCircle'
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom'
import BookOnlineIcon from '@mui/icons-material/BookOnline'
import QrCodeScannerIcon from '@mui/icons-material/QrCodeScanner'
import BarChartIcon from '@mui/icons-material/BarChart'
import FileDownloadIcon from '@mui/icons-material/FileDownload'
import StorefrontIcon from '@mui/icons-material/Storefront'
import EngineeringIcon from '@mui/icons-material/Engineering'
import LocalShippingIcon from '@mui/icons-material/LocalShipping'
import { useAuth } from '../../hooks/useAuth'
import { ROUTES } from '../../utils/constants'
import { USER_ROLES } from '../../constants/roles'
import { useState, useEffect } from 'react'
import visitorService from '../../api/visitorService'

const drawerWidth = 240

/**
 * Sidebar navigation component
 */
const Sidebar = ({ mobileOpen, onMobileClose }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const [pendingCount, setPendingCount] = useState(0)

  useEffect(() => {
    if (user?.role === USER_ROLES.RESIDENT) {
      visitorService.getPendingForMe()
        .then((res) => setPendingCount((res.data || []).length))
        .catch(() => {})
    }
  }, [user])

  // Navigation items based on role
  const getNavItems = () => {
    const baseItems = [
      { text: 'Dashboard', icon: <DashboardIcon />, path: ROUTES.DASHBOARD },
      { text: 'All Issues', icon: <BugReportIcon />, path: ROUTES.ISSUES },
      { text: 'Create Issue', icon: <AddCircleOutlineIcon />, path: ROUTES.ISSUES_CREATE },
      { text: 'Facilities', icon: <MeetingRoomIcon />, path: ROUTES.ASSETS },
      { text: 'My Bookings', icon: <BookOnlineIcon />, path: ROUTES.BOOKINGS },
      { text: 'Scan QR', icon: <QrCodeScannerIcon />, path: ROUTES.SCAN_QR },
      { text: 'Water Tanker', icon: <LocalShippingIcon />, path: ROUTES.WATER_TANKER },
      { text: 'Residents', icon: <ContactsIcon />, path: ROUTES.RESIDENTS },
      { text: 'Announcements', icon: <CampaignIcon />, path: '/admin/announcements' },
      { text: 'Events', icon: <EventIcon />, path: '/events' },
      { text: 'Polls', icon: <PollIcon />, path: ROUTES.POLLS },
      { text: 'Feedback', icon: <FeedbackIcon />, path: ROUTES.FEEDBACK },
      {
        text: 'Visitor Approvals',
        icon: <Badge badgeContent={pendingCount} color="error"><PersonPinCircleIcon /></Badge>,
        path: ROUTES.VISITOR_APPROVAL,
      },
    ]

    const adminItems = [
      { text: 'Dashboard', icon: <DashboardIcon />, path: ROUTES.DASHBOARD },
      { text: 'All Issues', icon: <BugReportIcon />, path: ROUTES.ISSUES },
      { text: 'Create Issue', icon: <AddCircleOutlineIcon />, path: ROUTES.ISSUES_CREATE },
      { text: 'Facilities', icon: <MeetingRoomIcon />, path: ROUTES.ASSETS },
      { text: 'My Bookings', icon: <BookOnlineIcon />, path: ROUTES.BOOKINGS },
      { text: 'Scan QR', icon: <QrCodeScannerIcon />, path: ROUTES.SCAN_QR },
      { text: 'Manage Assets', icon: <MeetingRoomIcon />, path: ROUTES.ADMIN.ASSETS },
      { text: 'Water Tanker', icon: <LocalShippingIcon />, path: ROUTES.WATER_TANKER },
      { text: 'Residents', icon: <ContactsIcon />, path: ROUTES.RESIDENTS },
      { text: 'Announcements', icon: <CampaignIcon />, path: '/admin/announcements' },
      { text: 'Events', icon: <EventIcon />, path: '/events' },
      { text: 'Polls', icon: <PollIcon />, path: ROUTES.POLLS },
      { text: 'Feedback', icon: <FeedbackIcon />, path: ROUTES.FEEDBACK },
      { text: 'Security – Visitors', icon: <SecurityIcon />, path: ROUTES.SECURITY },
      { text: 'Committee', icon: <GroupsIcon />, path: ROUTES.ADMIN.COMMITTEE },
      { text: 'Pending Approvals', icon: <HowToRegIcon />, path: ROUTES.ADMIN.PENDING_USERS },
      { text: 'Users', icon: <PeopleIcon />, path: ROUTES.ADMIN.USERS },
      { text: 'Reports', icon: <AssessmentIcon />, path: ROUTES.REPORTS.DASHBOARD },
      { text: 'Issue Analytics', icon: <BarChartIcon />, path: ROUTES.REPORTS.ISSUES },
      { text: 'Asset Reports', icon: <StorefrontIcon />, path: ROUTES.REPORTS.ASSETS },
      { text: 'Contractor Reports', icon: <EngineeringIcon />, path: ROUTES.REPORTS.CONTRACTORS },
      { text: 'Export Data', icon: <FileDownloadIcon />, path: ROUTES.REPORTS.EXPORT },
    ]

    const contractorItems = [
      { text: 'Dashboard', icon: <DashboardIcon />, path: ROUTES.DASHBOARD },
      { text: 'Assigned Issues', icon: <BugReportIcon />, path: ROUTES.ISSUES },
    ]

    const securityItems = [
      { text: 'Dashboard',    icon: <DashboardIcon />,      path: ROUTES.DASHBOARD },
      { text: 'Visitor Log',  icon: <SecurityIcon />,       path: ROUTES.SECURITY },
      { text: 'Water Tanker', icon: <LocalShippingIcon />,  path: ROUTES.WATER_TANKER },
    ]

    if (user?.role === USER_ROLES.ADMIN) {
      return adminItems
    } else if (user?.role === USER_ROLES.CONTRACTOR) {
      return contractorItems
    } else if (user?.role === USER_ROLES.SECURITY) {
      return securityItems
    } else {
      return baseItems
    }
  }

  const navItems = getNavItems()

  const handleNavigation = (path) => {
    navigate(path)
    if (mobileOpen) {
      onMobileClose()
    }
  }

  const drawerContent = (
    <Box>
      <Toolbar />
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton
            selected={location.pathname === ROUTES.PROFILE}
            onClick={() => handleNavigation(ROUTES.PROFILE)}
          >
            <ListItemIcon>
              <AccountCircleIcon />
            </ListItemIcon>
            <ListItemText primary="Profile" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      aria-label="navigation"
    >
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
        open
      >
        {drawerContent}
      </Drawer>
    </Box>
  )
}

export default Sidebar
