import { useState, useEffect, useCallback } from 'react'
import {
  Box, Container, Typography, Grid, Paper, CircularProgress, Alert,
  TextField, Button, MenuItem, Select, FormControl, InputLabel, Divider,
} from '@mui/material'
import BugReportIcon from '@mui/icons-material/BugReport'
import RefreshIcon from '@mui/icons-material/Refresh'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, LineChart, Line,
} from 'recharts'
import { format, subDays } from 'date-fns'
import reportService from '../../api/reportService'

const COLORS = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#0288d1', '#e91e63']

const CATEGORIES = ['electrical', 'plumbing', 'civil', 'carpentry', 'painting', 'housekeeping', 'security', 'other']
const PRIORITIES  = ['low', 'medium', 'high', 'critical']
const STATUSES    = ['open', 'in_progress', 'resolved', 'closed']

const dictToChartData = (obj) =>
  Object.entries(obj || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' '),
    value,
  })).filter(d => d.value > 0)

const IssueAnalytics = () => {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [fromDate, setFromDate] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [toDate,   setToDate]   = useState(format(new Date(), 'yyyy-MM-dd'))
  const [category, setCategory] = useState('')
  const [priority, setPriority] = useState('')
  const [status,   setStatus]   = useState('')

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params = {
        from_date: fromDate,
        to_date:   toDate,
        ...(category && { category }),
        ...(priority && { priority }),
        ...(status   && { status }),
      }
      const res = await reportService.getIssueAnalytics(params)
      setData(res)
    } catch {
      setError('Failed to load issue analytics.')
    } finally {
      setLoading(false)
    }
  }, [fromDate, toDate, category, priority, status])

  useEffect(() => { fetchData() }, [fetchData])

  const trendData = (data?.trend_data || []).map(d => ({ date: d.date, Issues: d.count }))

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
      <CircularProgress />
    </Box>
  )

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" alignItems="center" gap={1} mb={3}>
        <BugReportIcon color="error" />
        <Typography variant="h5" fontWeight={700}>Issue Analytics</Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          <TextField size="small" type="date" label="From" value={fromDate}
            onChange={e => setFromDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <TextField size="small" type="date" label="To" value={toDate}
            onChange={e => setToDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <FormControl size="small" sx={{ minWidth: 130 }}>
            <InputLabel>Category</InputLabel>
            <Select value={category} label="Category" onChange={e => setCategory(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              {CATEGORIES.map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Priority</InputLabel>
            <Select value={priority} label="Priority" onChange={e => setPriority(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              {PRIORITIES.map(p => <MenuItem key={p} value={p}>{p}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select value={status} label="Status" onChange={e => setStatus(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              {STATUSES.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<RefreshIcon />} onClick={fetchData} size="small">
            Apply
          </Button>
        </Box>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {data && (
        <>
          {/* Key metrics */}
          <Grid container spacing={2} mb={3}>
            {[
              ['Total Issues',     data.total_issues,                        '#1976d2'],
              ['Resolution Rate',  `${(data.resolution_rate || 0).toFixed(1)}%`, '#388e3c'],
            ].map(([label, value, color]) => (
              <Grid item xs={6} sm={3} key={label}>
                <Paper sx={{ p: 2.5, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">{label}</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color }}>{value}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>

          <Grid container spacing={3}>
            {/* By Category */}
            {dictToChartData(data.issues_by_category).length > 0 && (
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>By Category</Typography>
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={dictToChartData(data.issues_by_category)} layout="vertical"
                      margin={{ left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" allowDecimals={false} />
                      <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
                      <Tooltip />
                      <Bar dataKey="value" name="Issues" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}

            {/* By Priority */}
            {dictToChartData(data.issues_by_priority).length > 0 && (
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>By Priority</Typography>
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie data={dictToChartData(data.issues_by_priority)} dataKey="value"
                        nameKey="name" cx="50%" cy="50%" outerRadius={85}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                        {dictToChartData(data.issues_by_priority).map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}

            {/* By Status */}
            {dictToChartData(data.issues_by_status).length > 0 && (
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>By Status</Typography>
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie data={dictToChartData(data.issues_by_status)} dataKey="value"
                        nameKey="name" cx="50%" cy="50%" outerRadius={85}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                        {dictToChartData(data.issues_by_status).map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}

            {/* Trend line */}
            {trendData.length > 0 && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>Daily Trend</Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Line type="monotone" dataKey="Issues" stroke="#1976d2" dot={false} strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            )}

            {/* Avg resolution time by category */}
            {Object.keys(data.avg_resolution_time_by_category || {}).length > 0 && (
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>
                    Avg Resolution Time by Category (hours)
                  </Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart
                      data={Object.entries(data.avg_resolution_time_by_category).map(([k, v]) => ({
                        name: k, value: +v.toFixed(1),
                      }))}
                      margin={{ left: 10 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" name="Hours" fill="#f57c00" />
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

export default IssueAnalytics
