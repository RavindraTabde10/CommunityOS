import { useState, useEffect } from 'react'
import { Box, Container, Typography, Grid, Paper, Alert, Chip, Skeleton, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, MenuItem, FormControl, InputLabel, IconButton, Tooltip, Divider } from '@mui/material'
import { useAuth } from '../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import { USER_ROLES } from '../constants/roles'
import { ROUTES } from '../utils/constants'
import { toast } from 'react-toastify'
import issueService from '../api/issueService'
import reportService from '../api/reportService'
import committeeService from '../api/committeeService'
import visitorService from '../api/visitorService'
import guidelineService from '../api/guidelineService'
import { IssuePreviewCard, QuickActions, AnnouncementMarquee, CommitteeMemberCard, CommunityStats, ContactsSection, ActivePollWidget } from '../components/dashboard'
import UpcomingEvents from '../components/dashboard/UpcomingEvents'
import PersonAddAlt1Icon from '@mui/icons-material/PersonAddAlt1'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom'
import ExitToAppIcon from '@mui/icons-material/ExitToApp'
import GppGoodIcon from '@mui/icons-material/GppGood'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import BlockIcon from '@mui/icons-material/Block'
import BadgeIcon from '@mui/icons-material/Badge'
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar'
import ReportProblemIcon from '@mui/icons-material/ReportProblem'
import EditIcon from '@mui/icons-material/Edit'
import AddIcon from '@mui/icons-material/Add'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'

/**
 * Dashboard page - Society management hub with community information
 */
const Dashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const isSecurity = user?.role === USER_ROLES.SECURITY
  const isAdmin = user?.role === USER_ROLES.ADMIN
  const [communityStats, setCommunityStats] = useState(null)
  const [committeeMembers, setCommitteeMembers] = useState([])
  const [recentIssues, setRecentIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [visitorStats, setVisitorStats] = useState({ pending: 0, insideNow: 0, leftToday: 0 })
  const [statsLoading, setStatsLoading] = useState(false)
  const [guidelines, setGuidelines] = useState([])
  const [guidelinesLoading, setGuidelinesLoading] = useState(true)
  const [editOpen, setEditOpen] = useState(false)
  const [editList, setEditList] = useState([])
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [])

  useEffect(() => {
    if (isSecurity) loadSecurityStats()
  }, [isSecurity])

  useEffect(() => {
    loadGuidelines()
  }, [])

  const loadGuidelines = async () => {
    try {
      setGuidelinesLoading(true)
      const res = await guidelineService.getActive()
      setGuidelines(res.data || [])
    } catch (err) {
      console.error('Failed to load guidelines:', err)
    } finally {
      setGuidelinesLoading(false)
    }
  }

  const loadSecurityStats = async () => {
    try {
      setStatsLoading(true)
      const res = await visitorService.getAll()
      const list = res.data || []
      const todayStr = new Date().toDateString()
      const pending = list.filter(v => v.status === 'pending').length
      const insideNow = list.filter(v => v.status === 'approved').length
      const leftToday = list.filter(v => {
        if (v.status !== 'checked_out' || !v.check_out_time) return false
        const t = v.check_out_time.endsWith('Z') ? v.check_out_time : v.check_out_time + 'Z'
        return new Date(t).toDateString() === todayStr
      }).length
      setVisitorStats({ pending, insideNow, leftToday })
    } catch (err) {
      console.error('Failed to load visitor stats:', err)
    } finally {
      setStatsLoading(false)
    }
  }

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch community stats, committee members, and recent issues separately for better error handling
      let statsData = null
      let membersData = []
      let issuesData = []
      
      try {
        statsData = await reportService.getDashboardStats()
        console.log('✅ Dashboard stats loaded:', statsData)
      } catch (err) {
        console.error('❌ Error loading dashboard stats:', err)
        throw new Error(`Dashboard stats: ${err.response?.data?.detail || err.message}`)
      }
      
      try {
        membersData = await committeeService.getActiveMembers()
        console.log('✅ Committee members loaded:', membersData)
      } catch (err) {
        console.error('❌ Error loading committee members:', err)
        throw new Error(`Committee members: ${err.response?.data?.detail || err.message}`)
      }
      
      try {
        issuesData = await issueService.getRecentIssues(4)
        console.log('✅ Recent issues loaded:', issuesData)
      } catch (err) {
        console.error('❌ Error loading recent issues:', err)
        throw new Error(`Recent issues: ${err.response?.data?.detail || err.message}`)
      }
      
      setCommunityStats(statsData)
      setCommitteeMembers(membersData)
      setRecentIssues(issuesData)
    } catch (err) {
      console.error('Error loading dashboard data:', err)
      setError(err.message || 'Failed to load dashboard data')
      toast.error(err.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const ICON_CFG = {
    block:   { icon: <BlockIcon sx={{ color: '#c62828', fontSize: 20 }} />, severity: '#ffebee', label: 'No Entry' },
    check:   { icon: <CheckCircleOutlineIcon sx={{ color: '#2e7d32', fontSize: 20 }} />, severity: '#e8f5e9', label: 'Required' },
    badge:   { icon: <BadgeIcon sx={{ color: '#1565c0', fontSize: 20 }} />, severity: '#e3f2fd', label: 'ID Check' },
    car:     { icon: <DirectionsCarIcon sx={{ color: '#e65100', fontSize: 20 }} />, severity: '#fff3e0', label: 'Vehicle' },
    warning: { icon: <ReportProblemIcon sx={{ color: '#f57f17', fontSize: 20 }} />, severity: '#fffde7', label: 'Alert' },
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 1, mb: 1, position: 'relative', zIndex: 1 }}>
      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 1 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={1.5}>
        {/* LEFT SIDE - Main Dashboard Content */}
        <Grid item xs={12} lg={8}>
          {/* Welcome Header */}
          <Box 
            sx={{ 
              mb: 1, 
              p: 1.5, 
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              borderRadius: 2,
              border: '1px solid rgba(255, 255, 255, 0.3)',
            }}
          >
            <Typography variant="h6" fontWeight="bold" sx={{ color: 'white', mb: 0 }}>
              Welcome to Riverdale Grove Connect!
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.95)', mt: 0.5 }}>
              {user?.name || 'User'}
              {' • '}
              <Chip label={user?.role || 'N/A'} size="small" sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white', fontWeight: 600, height: 18, fontSize: '0.7rem' }} />
              {user?.unit_number && (
                <>
                  {' • '}
                  <Chip label={`Unit ${user.unit_number}`} size="small" sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white', fontWeight: 600, height: 18, fontSize: '0.7rem' }} />
                </>
              )}
            </Typography>
          </Box>

          {/* Announcement Marquee */}
          <Box sx={{ mb: 1 }}>
            <AnnouncementMarquee />
          </Box>

          {/* Security Dashboard */}
          {isSecurity && (
            <Box sx={{ mb: 1.5 }}>
              {/* Log Visitor CTA */}
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<PersonAddAlt1Icon sx={{ fontSize: 28 }} />}
                onClick={() => navigate(ROUTES.SECURITY)}
                sx={{
                  py: 2,
                  mb: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  borderRadius: 3,
                  background: 'white',
                  color: '#1565c0',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.35)',
                  letterSpacing: 0.5,
                  '&:hover': { background: '#e3f2fd' },
                }}
              >
                Log Visitor &nbsp;•&nbsp; विज़िटर दर्ज करें
              </Button>

              {/* Visitor Stat Cards */}
              <Grid container spacing={1.5}>
                {[
                  {
                    icon: <HourglassEmptyIcon sx={{ fontSize: 38 }} />,
                    value: visitorStats.pending,
                    label: 'Pending Approvals',
                    sub: 'मंजूरी बाकी',
                    bg: 'linear-gradient(135deg, #e65100 0%, #fb8c00 100%)',
                    shadow: 'rgba(230,81,0,0.4)',
                  },
                  {
                    icon: <MeetingRoomIcon sx={{ fontSize: 38 }} />,
                    value: visitorStats.insideNow,
                    label: 'Inside Now',
                    sub: 'अभी अंदर',
                    bg: 'linear-gradient(135deg, #1b5e20 0%, #388e3c 100%)',
                    shadow: 'rgba(27,94,32,0.4)',
                  },
                  {
                    icon: <ExitToAppIcon sx={{ fontSize: 38 }} />,
                    value: visitorStats.leftToday,
                    label: 'Left Today',
                    sub: 'आज गए',
                    bg: 'linear-gradient(135deg, #01579b 0%, #0288d1 100%)',
                    shadow: 'rgba(1,87,155,0.4)',
                  },
                ].map((stat) => (
                  <Grid item xs={4} key={stat.label}>
                    <Paper
                      elevation={4}
                      sx={{
                        p: 1.5,
                        borderRadius: 3,
                        background: stat.bg,
                        boxShadow: `0 4px 14px ${stat.shadow}`,
                        color: 'white',
                        textAlign: 'center',
                        minHeight: 110,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 0.5,
                      }}
                    >
                      {statsLoading ? (
                        <Skeleton variant="circular" width={38} height={38} sx={{ bgcolor: 'rgba(255,255,255,0.3)' }} />
                      ) : (
                        stat.icon
                      )}
                      <Typography variant="h4" fontWeight={800} lineHeight={1}>
                        {statsLoading ? '–' : (stat.value > 99 ? '99+' : stat.value)}
                      </Typography>
                      <Typography variant="caption" fontWeight={600} sx={{ lineHeight: 1.2 }}>
                        {stat.label}
                      </Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.65rem', opacity: 0.9 }}>
                        {stat.sub}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Community Statistics */}
          {!isSecurity && (
            <Box sx={{ mb: 1 }}>
              <CommunityStats stats={communityStats} loading={loading} />
            </Box>
          )}

          {/* Active Poll Widget */}
          {!isSecurity && (
            <Box sx={{ mb: 1 }}>
              <ActivePollWidget />
            </Box>
          )}

          {/* Recent Activity - Issues */}
          {!isSecurity && <Paper 
            elevation={3} 
            sx={{ 
              p: 1.5,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body1" fontWeight="bold">
                🔔 Recent Activity
              </Typography>
              <Chip 
                label="View All" 
                clickable 
                onClick={() => navigate('/issues')}
                color="primary"
                variant="outlined"
                size="small"
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
            </Box>

            {loading ? (
              <Grid container spacing={1}>
                {[1].map((n) => (
                  <Grid item xs={12} key={n}>
                    <Skeleton variant="rectangular" height={100} sx={{ borderRadius: 1 }} />
                  </Grid>
                ))}
              </Grid>
            ) : recentIssues.length > 0 ? (
              <Grid container spacing={1}>
                {recentIssues.slice(0, 1).map((issue) => (
                  <Grid item xs={12} key={issue.id}>
                    <IssuePreviewCard issue={issue} />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="body1" color="text.secondary">
                  No recent issues. Everything is running smoothly!
                </Typography>
              </Box>
            )}
          </Paper>}

          {/* Upcoming Events Section */}
          <Box sx={{ mt: 1.5 }}>
            <UpcomingEvents />
          </Box>
        </Grid>

        {/* RIGHT SIDE - Committee & Contacts */}
        <Grid item xs={12} lg={4}>
          {/* Committee Members Section - Top Right */}
          {!isSecurity && <Paper 
            elevation={3} 
            sx={{ 
              p: 1.5, 
              mb: 1,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            }}
          >
            <Typography variant="body1" fontWeight="bold" sx={{ mb: 0.75 }}>
              🏛️ Committee Members
            </Typography>

            {loading ? (
              <Box>
                {[1].map((n) => (
                  <Skeleton key={n} variant="rectangular" height={50} sx={{ borderRadius: 2, mb: 0.5 }} />
                ))}
              </Box>
            ) : committeeMembers.length > 0 ? (
              <Box>
                {committeeMembers.slice(0, 4).map((member, idx) => (
                  <Box key={member.id} sx={{ borderBottom: idx < Math.min(committeeMembers.length, 4) - 1 ? '1px solid' : 'none', borderColor: 'divider' }}>
                    <CommitteeMemberCard member={member} compact />
                  </Box>
                ))}
                {committeeMembers.length > 4 && (
                  <Chip 
                    label={`+${committeeMembers.length - 4} more`}
                    size="small"
                    color="primary"
                    variant="outlined"
                    onClick={() => navigate(ROUTES.ADMIN.COMMITTEE)}
                    sx={{ mt: 0.5, height: 18, fontSize: '0.65rem', cursor: 'pointer' }}
                  />
                )}
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  No committee members assigned yet.
                </Typography>
              </Box>
            )}
          </Paper>}

          {/* Quick Actions - Middle Right */}
          {!isSecurity && (
            <Box sx={{ mb: 1 }}>
              <QuickActions onEditGuidelines={() => { setEditList(guidelines.map(g => ({ ...g }))); setEditOpen(true) }} />
            </Box>
          )}

          {/* Contacts Section - Bottom Right */}
          {isSecurity && (
            <Paper
              elevation={3}
              sx={{
                mb: 1.5,
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.5)',
                background: 'rgba(255,255,255,0.97)',
              }}
            >
              <Box
                sx={{
                  px: 1.5, py: 1,
                  background: 'linear-gradient(135deg, #b71c1c 0%, #e53935 100%)',
                  display: 'flex', alignItems: 'center', gap: 1,
                }}
              >
                <GppGoodIcon sx={{ color: 'white', fontSize: 20 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" fontWeight={700} color="white">
                    Security Guidelines
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.85)', fontSize: '0.65rem' }}>
                    सुरक्षा नियम — पालन अनिवार्य है
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ p: 1.5 }}>
                {guidelinesLoading ? (
                  [1, 2, 3].map(n => <Skeleton key={n} variant="rectangular" height={48} sx={{ borderRadius: 1.5, mb: 0.75 }} />)
                ) : guidelines.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 1 }}>
                    No guidelines configured.
                  </Typography>
                ) : (
                  guidelines.map((rule, i) => {
                    const cfg = ICON_CFG[rule.icon_type] || ICON_CFG.check
                    return (
                      <Box
                        key={rule.id ?? i}
                        sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, p: 1, mb: 0.75, borderRadius: 1.5, bgcolor: rule.severity }}
                      >
                        <Box sx={{ mt: 0.25, flexShrink: 0 }}>{cfg.icon}</Box>
                        <Box>
                          <Typography variant="body2" fontWeight={600} sx={{ lineHeight: 1.3 }}>
                            {rule.text}
                          </Typography>
                          {rule.text_hi && (
                            <Typography variant="caption" color="text.secondary">{rule.text_hi}</Typography>
                          )}
                        </Box>
                      </Box>
                    )
                  })
                )}
              </Box>
            </Paper>
          )}
          <ContactsSection />
        </Grid>
      </Grid>

      {/* Admin Edit Guidelines Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          Edit Security Guidelines
          <Typography variant="caption" display="block" color="text.secondary">
            Changes are visible to all security staff immediately.
          </Typography>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 2 }}>
          {editList.map((g, i) => (
            <Paper key={i} variant="outlined" sx={{ p: 1.5, mb: 1.5, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <FormControl size="small" sx={{ minWidth: 130 }}>
                  <InputLabel>Icon</InputLabel>
                  <Select
                    label="Icon"
                    value={g.icon_type || 'check'}
                    onChange={e => {
                      const updated = [...editList]
                      updated[i] = { ...updated[i], icon_type: e.target.value, severity: ICON_CFG[e.target.value]?.severity || '#e8f5e9' }
                      setEditList(updated)
                    }}
                  >
                    {Object.entries(ICON_CFG).map(([key, cfg]) => (
                      <MenuItem key={key} value={key}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          {cfg.icon} {cfg.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Box sx={{ flex: 1 }} />
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => setEditList(editList.filter((_, idx) => idx !== i))}
                >
                  <DeleteOutlineIcon fontSize="small" />
                </IconButton>
              </Box>
              <TextField
                fullWidth size="small" label="English" value={g.text || ''}
                onChange={e => { const u = [...editList]; u[i] = { ...u[i], text: e.target.value }; setEditList(u) }}
                sx={{ mb: 1 }}
              />
              <TextField
                fullWidth size="small" label="हिंदी (optional)" value={g.text_hi || ''}
                onChange={e => { const u = [...editList]; u[i] = { ...u[i], text_hi: e.target.value }; setEditList(u) }}
              />
            </Paper>
          ))}
          <Button
            startIcon={<AddIcon />}
            variant="outlined"
            size="small"
            onClick={() => setEditList([...editList, { text: '', text_hi: '', icon_type: 'check', severity: '#e8f5e9', is_active: true }])}
          >
            Add Rule
          </Button>
        </DialogContent>
        <DialogActions sx={{ px: 2, py: 1.5 }}>
          <Button onClick={() => setEditOpen(false)} disabled={saving}>Cancel</Button>
          <Button
            variant="contained"
            disabled={saving || editList.some(g => !g.text.trim())}
            onClick={async () => {
              setSaving(true)
              try {
                await guidelineService.bulkUpdate(editList)
                await loadGuidelines()
                setEditOpen(false)
                toast.success('Guidelines updated')
              } catch (err) {
                toast.error('Failed to save guidelines')
              } finally {
                setSaving(false)
              }
            }}
          >
            {saving ? 'Saving…' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Dashboard
