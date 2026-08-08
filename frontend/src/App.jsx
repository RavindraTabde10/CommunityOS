import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

// Layouts
import MainLayout from './components/layout/MainLayout'

// Route guards
import ProtectedRoute from './components/common/ProtectedRoute'
import PublicRoute from './components/common/PublicRoute'

// Auth pages
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import ForgotPassword from './pages/auth/ForgotPassword'
import ResetPassword from './pages/auth/ResetPassword'

// Main pages
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import EditProfile from './pages/EditProfile'
import ChangePassword from './pages/ChangePassword'
import ResidentDirectory from './pages/ResidentDirectory'

// Issue pages
import { IssueList, CreateIssue, IssueDetail, EditIssue } from './pages/issues'

// Event pages
import Events from './pages/Events'
import CreateEvent from './pages/CreateEvent'
import EditEvent from './pages/EditEvent'
import Polls from './pages/Polls'
import CreatePoll from './pages/CreatePoll'
import EditPoll from './pages/EditPoll'
import Feedback from './pages/Feedback'

// Asset & booking pages
import { AssetList, AssetDetail, QRScanner } from './pages/assets'
import { MyBookings } from './pages/bookings'
import WaterTanker from './pages/WaterTanker'

// Reports pages
import {
  ReportsDashboard, IssueAnalytics, AssetReports, ContractorReports, ExportReports,
} from './pages/reports'

// Admin pages
import PendingUsers from './pages/admin/PendingUsers'
import Users from './pages/admin/Users'
import AnnouncementManagement from './pages/AnnouncementManagement'
import CommitteeManagement from './pages/admin/CommitteeManagement'
import AssetManagement from './pages/admin/AssetManagement'
import SecurityPage from './pages/SecurityPage'
import VisitorApproval from './pages/VisitorApproval'

// Redux
import { getCurrentUser } from './store/authSlice'
import authService from './api/authService'
import { ROUTES } from './utils/constants'

function App() {
  const dispatch = useDispatch()

  // Check if user is authenticated on mount
  useEffect(() => {
    if (authService.isAuthenticated()) {
      dispatch(getCurrentUser())
    }
  }, [dispatch])

  return (
    <>
      <Routes>
        {/* Public routes - redirect to dashboard if authenticated */}
        <Route
          path={ROUTES.LOGIN}
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path={ROUTES.REGISTER}
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path={ROUTES.FORGOT_PASSWORD}
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />
        <Route
          path={ROUTES.RESET_PASSWORD}
          element={
            <PublicRoute>
              <ResetPassword />
            </PublicRoute>
          }
        />

        {/* Protected routes - require authentication */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
          
          {/* Issue routes */}
          <Route path={ROUTES.ISSUES} element={<IssueList />} />
          <Route path={ROUTES.ISSUES_CREATE} element={<CreateIssue />} />
          <Route path="/issues/:id" element={<IssueDetail />} />
          <Route path="/issues/:id/edit" element={<EditIssue />} />
          
          {/* Profile routes */}
          <Route path={ROUTES.PROFILE} element={<Profile />} />
          <Route path="/profile/edit" element={<EditProfile />} />
          <Route path="/profile/change-password" element={<ChangePassword />} />
          
          {/* Resident Directory */}
          <Route path={ROUTES.RESIDENTS} element={<ResidentDirectory />} />
          
          {/* Event routes */}
          <Route path="/events" element={<Events />} />
          <Route path="/events/create" element={<CreateEvent />} />
          <Route path="/events/:id/edit" element={<EditEvent />} />

          {/* Poll routes */}
          <Route path={ROUTES.POLLS} element={<Polls />} />
          <Route path={ROUTES.POLLS_CREATE} element={<CreatePoll />} />
          <Route path="/polls/:id/edit" element={<EditPoll />} />
          <Route path={ROUTES.FEEDBACK} element={<Feedback />} />
          
          {/* Admin routes */}
          <Route path={ROUTES.ADMIN.USERS} element={<Users />} />
          <Route path={ROUTES.ADMIN.PENDING_USERS} element={<PendingUsers />} />
          <Route path={ROUTES.ADMIN.REPORTS} element={<Dashboard />} />
          <Route path="/admin/announcements" element={<AnnouncementManagement />} />
          <Route path={ROUTES.ADMIN.COMMITTEE} element={<CommitteeManagement />} />

          {/* Asset & booking routes */}
          <Route path={ROUTES.ASSETS} element={<AssetList />} />
          <Route path="/assets/:id" element={<AssetDetail />} />
          <Route path={ROUTES.SCAN_QR} element={<QRScanner />} />
          <Route path={ROUTES.BOOKINGS} element={<MyBookings />} />
          <Route path={ROUTES.WATER_TANKER} element={<WaterTanker />} />

          {/* Admin asset management */}
          <Route path={ROUTES.ADMIN.ASSETS} element={<AssetManagement />} />

          {/* Reports routes */}
          <Route path={ROUTES.REPORTS.DASHBOARD}    element={<ReportsDashboard />} />
          <Route path={ROUTES.REPORTS.ISSUES}       element={<IssueAnalytics />} />
          <Route path={ROUTES.REPORTS.ASSETS}       element={<AssetReports />} />
          <Route path={ROUTES.REPORTS.CONTRACTORS}  element={<ContractorReports />} />
          <Route path={ROUTES.REPORTS.EXPORT}       element={<ExportReports />} />

          {/* Security routes */}
          <Route path={ROUTES.SECURITY} element={<SecurityPage />} />
          <Route path={ROUTES.VISITOR_APPROVAL} element={<VisitorApproval />} />
        </Route>

        {/* Default redirect */}
        <Route path={ROUTES.HOME} element={<Navigate to={ROUTES.DASHBOARD} replace />} />
        
        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      </Routes>

      {/* Toast notifications */}
      <ToastContainer />
    </>
  )
}

export default App
