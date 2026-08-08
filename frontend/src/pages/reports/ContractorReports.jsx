import { useState, useEffect, useCallback } from 'react'
import {
  Box, Container, Typography, Grid, Paper, CircularProgress, Alert,
  TextField, Button, MenuItem, Select, FormControl, InputLabel,
  Chip, Divider, Stack, Rating,
} from '@mui/material'
import EngineeringIcon from '@mui/icons-material/Engineering'
import RefreshIcon from '@mui/icons-material/Refresh'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { format, subDays } from 'date-fns'
import reportService from '../../api/reportService'

const ContractorReports = () => {
  const [reports, setReports]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [error,   setError]     = useState(null)
  const [fromDate, setFromDate] = useState(format(subDays(new Date(), 90), 'yyyy-MM-dd'))
  const [toDate,   setToDate]   = useState(format(new Date(), 'yyyy-MM-dd'))

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await reportService.getContractorPerformance({ from_date: fromDate, to_date: toDate })
      setReports(Array.isArray(res) ? res : [])
    } catch (err) {
      if (err?.response?.status === 403) {
        setError('Admin access required to view contractor reports.')
      } else {
        setError('Failed to load contractor performance reports.')
      }
    } finally {
      setLoading(false)
    }
  }, [fromDate, toDate])

  useEffect(() => { fetchData() }, [fetchData])

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
      <CircularProgress />
    </Box>
  )

  const ratingData = reports.map(r => ({
    name: r.contractor_name || r.contractor_email,
    Rating: +(r.avg_rating || 0).toFixed(2),
    Jobs: r.total_jobs_completed || 0,
  }))

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" alignItems="center" gap={1} mb={3}>
        <EngineeringIcon color="action" />
        <Typography variant="h5" fontWeight={700}>Contractor Performance</Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          <TextField size="small" type="date" label="From" value={fromDate}
            onChange={e => setFromDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <TextField size="small" type="date" label="To" value={toDate}
            onChange={e => setToDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <Button variant="contained" startIcon={<RefreshIcon />} onClick={fetchData} size="small">
            Apply
          </Button>
        </Box>
      </Paper>

      {error && <Alert severity={error.includes('Admin') ? 'warning' : 'error'} sx={{ mb: 2 }}>{error}</Alert>}

      {reports.length === 0 && !error ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">No contractor data available for the selected period.</Typography>
        </Paper>
      ) : (
        <>
          {/* Contractor cards */}
          <Grid container spacing={2} mb={3}>
            {reports.map(r => (
              <Grid item xs={12} sm={6} md={4} key={r.contractor_id}>
                <Paper sx={{ p: 2.5 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                    <Box>
                      <Typography fontWeight={700}>{r.contractor_name || '—'}</Typography>
                      <Typography variant="caption" color="text.secondary">{r.contractor_email}</Typography>
                    </Box>
                    <Box display="flex" gap={0.5} flexDirection="column" alignItems="flex-end">
                      <Chip
                        label={r.is_verified ? 'Verified' : 'Unverified'}
                        color={r.is_verified ? 'success' : 'default'}
                        size="small"
                      />
                      <Chip
                        label={r.is_available ? 'Available' : 'Unavailable'}
                        color={r.is_available ? 'info' : 'default'}
                        size="small"
                      />
                    </Box>
                  </Box>

                  <Divider sx={{ my: 1 }} />

                  <Stack spacing={0.5}>
                    {[
                      ['Jobs Completed',   r.total_jobs_completed || 0],
                      ['Completion Rate',  `${(r.completion_rate || 0).toFixed(1)}%`],
                      ['Total Ratings',    r.total_ratings || 0],
                      ['Avg Response',     r.avg_response_time_hours
                        ? `${r.avg_response_time_hours.toFixed(1)} hrs` : 'N/A'],
                    ].map(([label, val]) => (
                      <Box key={label} display="flex" justifyContent="space-between">
                        <Typography variant="caption" color="text.secondary">{label}</Typography>
                        <Typography variant="caption" fontWeight={600}>{val}</Typography>
                      </Box>
                    ))}
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="caption" color="text.secondary">Avg Rating</Typography>
                      <Rating value={r.avg_rating || 0} precision={0.5} readOnly size="small" />
                    </Box>
                  </Stack>

                  {/* Recent ratings */}
                  {r.recent_ratings?.length > 0 && (
                    <Box mt={1.5}>
                      <Typography variant="caption" color="text.secondary" fontWeight={600}>
                        Recent Ratings
                      </Typography>
                      {r.recent_ratings.slice(0, 2).map((rt, i) => (
                        <Box key={i} mt={0.5} p={1} bgcolor="grey.50" borderRadius={1}>
                          <Rating value={rt.rating || 0} readOnly size="small" />
                          {rt.review && (
                            <Typography variant="caption" display="block" color="text.secondary"
                              sx={{ mt: 0.3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              "{rt.review}"
                            </Typography>
                          )}
                        </Box>
                      ))}
                    </Box>
                  )}
                </Paper>
              </Grid>
            ))}
          </Grid>

          {/* Comparison charts */}
          {ratingData.length > 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>Average Rating</Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={ratingData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis domain={[0, 5]} />
                      <Tooltip />
                      <Bar dataKey="Rating" fill="#f57c00" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} mb={2}>Jobs Completed</Typography>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={ratingData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="Jobs" fill="#388e3c" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          )}
        </>
      )}
    </Container>
  )
}

export default ContractorReports
