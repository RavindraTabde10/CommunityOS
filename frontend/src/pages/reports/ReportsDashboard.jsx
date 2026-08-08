import { useState, useEffect, useCallback } from 'react'
import {
  Box, Container, Typography, Grid, Paper, CircularProgress, Alert,
  TextField, Button, Chip, Divider, Stack,
} from '@mui/material'
import AssessmentIcon from '@mui/icons-material/Assessment'
import RefreshIcon from '@mui/icons-material/Refresh'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, LineChart, Line,
} from 'recharts'
import { format, subDays } from 'date-fns'
import reportService from '../../api/reportService'

const COLORS = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#0288d1']

const StatCard = ({ label, value, color = '#1976d2', sub }) => (
  <Paper sx={{ p: 2.5, height: '100%' }}>
    <Typography variant="body2" color="text.secondary">{label}</Typography>
    <Typography variant="h4" fontWeight={700} sx={{ color, mt: 0.5 }}>
      {value ?? '—'}
    </Typography>
    {sub && <Typography variant="caption" color="text.secondary">{sub}</Typography>}
  </Paper>
)

const ReportsDashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [fromDate, setFromDate] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [toDate,   setToDate]   = useState(format(new Date(), 'yyyy-MM-dd'))

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await reportService.getDashboardStats({ from_date: fromDate, to_date: toDate })
      setStats(res)
    } catch {
      setError('Failed to load dashboard statistics.')
    } finally {
      setLoading(false)
    }
  }, [fromDate, toDate])

  useEffect(() => { fetchStats() }, [fetchStats])

  const issueStatusData = stats ? [
    { name: 'Open',        value: stats.open_issues        },
    { name: 'In Progress', value: stats.in_progress_issues },
    { name: 'Resolved',    value: stats.resolved_issues    },
    { name: 'Closed',      value: stats.closed_issues      },
  ].filter(d => d.value > 0) : []

  const bookingData = stats ? [
    { name: 'Pending',   value: stats.pending_bookings   },
    { name: 'Confirmed', value: stats.confirmed_bookings },
    { name: 'Total',     value: stats.total_bookings     },
  ] : []

  const roleData = stats ? Object.entries(stats.users_by_role || {}).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1), value: v,
  })) : []

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
      <CircularProgress />
    </Box>
  )

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3} flexWrap="wrap" gap={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <AssessmentIcon color="primary" />
          <Typography variant="h5" fontWeight={700}>Reports Dashboard</Typography>
        </Box>
        <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
          <TextField size="small" type="date" label="From" value={fromDate}
            onChange={e => setFromDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <TextField size="small" type="date" label="To" value={toDate}
            onChange={e => setToDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchStats} size="small">
            Refresh
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {stats && (
        <>
          {/* Issue stats */}
          <Typography variant="subtitle1" fontWeight={600} mb={1.5}>Issues</Typography>
          <Grid container spacing={2} mb={3}>
            {[
              ['Total Issues',     stats.total_issues,       '#1976d2'],
              ['Open',             stats.open_issues,        '#f57c00'],
              ['In Progress',      stats.in_progress_issues, '#0288d1'],
              ['Resolved',         stats.resolved_issues,    '#388e3c'],
              ['Avg Resolution',   stats.avg_resolution_time_hours
                ? `${stats.avg_resolution_time_hours.toFixed(1)} hrs` : 'N/A', '#7b1fa2'],
            ].map(([label, value, color]) => (
              <Grid item xs={6} sm={4} md={2.4} key={label}>
                <StatCard label={label} value={value} color={color} />
              </Grid>
            ))}
          </Grid>

          {/* User & asset stats */}
          <Typography variant="subtitle1" fontWeight={600} mb={1.5}>Users & Assets</Typography>
          <Grid container spacing={2} mb={3}>
            {[
              ['Total Users',      stats.total_users,         '#1976d2'],
              ['Active Contractors', stats.active_contractors, '#388e3c'],
              ['Total Assets',     stats.total_assets,        '#f57c00'],
              ['Active Assets',    stats.active_assets,       '#0288d1'],
              ['Total Bookings',   stats.total_bookings,      '#7b1fa2'],
              ['Revenue',          `₹${(stats.total_booking_revenue || 0).toFixed(0)}`, '#d32f2f'],
            ].map(([label, value, color]) => (
              <Grid item xs={6} sm={4} md={2} key={label}>
                <StatCard label={label} value={value} color={color} />
              </Grid>
            ))}
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Charts */}
          <Grid container spacing={3}>
            {/* Issue status pie */}
            {issueStatusData.length > 0 && (
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>Issues by Status</Typography>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={issueStatusData} dataKey="value" nameKey="name"
                        cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) =>
                          `${name} ${(percent * 100).toFixed(0)}%`}>
                        {issueStatusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}

            {/* Users by role bar */}
            {roleData.length > 0 && (
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>Users by Role</Typography>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={roleData} margin={{ bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" name="Users" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}

            {/* Bookings bar */}
            {stats.total_bookings > 0 && (
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>Booking Overview</Typography>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={bookingData} margin={{ bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="value" name="Bookings" fill="#388e3c" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}
          </Grid>
        </>
      )}
    </Container>
  )
}

export default ReportsDashboard
