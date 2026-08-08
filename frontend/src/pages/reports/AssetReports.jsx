import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Box, Container, Typography, Grid, Paper, CircularProgress, Alert,
  TextField, Button, MenuItem, Select, FormControl, InputLabel, Stack,
  ToggleButtonGroup, ToggleButton, Chip,
} from '@mui/material'
import StorefrontIcon from '@mui/icons-material/Storefront'
import RefreshIcon from '@mui/icons-material/Refresh'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { format, subDays, startOfWeek } from 'date-fns'
import reportService from '../../api/reportService'
import assetService from '../../api/assetService'
import { ASSET_TYPES, ASSET_TYPE_OPTIONS } from '../../constants/assets'

// one distinct colour per facility line
const LINE_COLORS = ['#1976d2', '#e53935', '#388e3c', '#f57c00', '#7b1fa2', '#0288d1', '#5d4037']

const AssetReports = () => {
  const [reports,    setReports]    = useState([])
  const [assets,     setAssets]     = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [fromDate,   setFromDate]   = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [toDate,     setToDate]     = useState(format(new Date(), 'yyyy-MM-dd'))
  const [assetId,    setAssetId]    = useState('')
  const [assetType,  setAssetType]  = useState('')
  const [granularity, setGranularity] = useState('day')
  // set of asset_ids whose lines are visible; null = all visible
  const [visibleIds, setVisibleIds] = useState(null)

  useEffect(() => {
    assetService.getAssets({ is_active: true, limit: 100 })
      .then(r => setAssets(r.data || []))
      .catch(() => {})
  }, [])

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params = {
        from_date: fromDate,
        to_date:   toDate,
        ...(assetId   && { asset_id:   assetId }),
        ...(assetType && { asset_type: assetType }),
      }
      const res = await reportService.getAssetUsage(params)
      const data = Array.isArray(res) ? res : []
      setReports(data)
      setVisibleIds(new Set(data.map(r => r.asset_id)))
    } catch {
      setError('Failed to load asset usage reports.')
    } finally {
      setLoading(false)
    }
  }, [fromDate, toDate, assetId, assetType])

  useEffect(() => { fetchData() }, [fetchData])

  const visibleReports = useMemo(
    () => reports.filter(r => !visibleIds || visibleIds.has(r.asset_id)),
    [reports, visibleIds],
  )

  // Build a unified dataset: one row per label, one key per facility
  const chartData = useMemo(() => {
    if (!visibleReports.length) return []

    if (granularity === 'hour') {
      return Array.from({ length: 24 }, (_, h) => {
        const point = { label: `${String(h).padStart(2, '0')}:00` }
        visibleReports.forEach(r => {
          const slot = (r.popular_time_slots || []).find(s => s.hour === h)
          point[r.asset_name] = slot?.booking_count ?? 0
        })
        return point
      })
    }

    // Collect all unique period keys across every facility
    const labelSet = new Set()
    const getKey = (dateStr) => {
      const dt = new Date(dateStr)
      if (granularity === 'day')   return dateStr
      if (granularity === 'week')  return format(startOfWeek(dt, { weekStartsOn: 1 }), 'yyyy-MM-dd')
      return format(dt, 'yyyy-MM')
    }
    visibleReports.forEach(r =>
      (r.booking_trend || []).forEach(d => labelSet.add(getKey(d.date)))
    )
    const labels = Array.from(labelSet).sort()

    return labels.map(label => {
      const point = { label }
      visibleReports.forEach(r => {
        let total = 0
        ;(r.booking_trend || []).forEach(d => {
          if (getKey(d.date) === label) total += (d.count ?? 0)
        })
        point[r.asset_name] = total
      })
      return point
    })
  }, [visibleReports, granularity])

  // Format X-axis tick label for display
  const fmtLabel = (v) => {
    if (granularity === 'hour' || granularity === 'month') return v
    if (granularity === 'week') {
      try { return format(new Date(v), 'dd MMM') } catch { return v }
    }
    try { return format(new Date(v), 'dd MMM') } catch { return v }
  }

  const toggleFacility = (id) => {
    setVisibleIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) { next.delete(id) } else { next.add(id) }
      return next
    })
  }

  const utilizationData = reports.map(r => ({
    name: r.asset_name,
    Rate: +(r.utilization_rate || 0).toFixed(1),
  }))

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
      <CircularProgress />
    </Box>
  )

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Box display="flex" alignItems="center" gap={1} mb={3}>
        <StorefrontIcon color="warning" />
        <Typography variant="h5" fontWeight={700}>Asset Usage Reports</Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          <TextField size="small" type="date" label="From" value={fromDate}
            onChange={e => setFromDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <TextField size="small" type="date" label="To" value={toDate}
            onChange={e => setToDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Asset</InputLabel>
            <Select value={assetId} label="Asset" onChange={e => setAssetId(e.target.value)}>
              <MenuItem value="">All Assets</MenuItem>
              {assets.map(a => <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Type</InputLabel>
            <Select value={assetType} label="Type" onChange={e => setAssetType(e.target.value)}>
              <MenuItem value="">All Types</MenuItem>
              {ASSET_TYPE_OPTIONS.map(o => (
                <MenuItem key={o.value} value={o.value}>
                  {ASSET_TYPES[o.value]?.icon} {o.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<RefreshIcon />} onClick={fetchData} size="small">
            Apply
          </Button>
        </Box>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {reports.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">No asset usage data for the selected filters.</Typography>
        </Paper>
      ) : (
        <>
          {/* ── Booking Trend Chart ──────────────────────────────────── */}
          <Paper sx={{ p: 2.5, mb: 3 }}>
            {/* Header row: title + granularity toggle */}
            <Box display="flex" alignItems="flex-start" justifyContent="space-between"
              flexWrap="wrap" gap={1} mb={2}>
              <Box>
                <Typography variant="subtitle1" fontWeight={700}>Bookings Over Time</Typography>
                <Typography variant="caption" color="text.secondary">
                  {granularity === 'hour' ? 'Total bookings by hour of day' : 'Total bookings per facility'}
                </Typography>
              </Box>
              <ToggleButtonGroup value={granularity} exclusive
                onChange={(_, v) => v && setGranularity(v)} size="small">
                {[['hour','Hour'],['day','Day'],['week','Week'],['month','Month']].map(([v, l]) => (
                  <ToggleButton key={v} value={v} sx={{ px: 1.5, fontSize: 12 }}>{l}</ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>

            {/* Facility filter chips */}
            <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
              {reports.map((r, i) => {
                const color = LINE_COLORS[i % LINE_COLORS.length]
                const active = !visibleIds || visibleIds.has(r.asset_id)
                return (
                  <Chip
                    key={r.asset_id}
                    label={r.asset_name}
                    onClick={() => toggleFacility(r.asset_id)}
                    size="small"
                    sx={{
                      borderLeft: `4px solid ${color}`,
                      bgcolor: active ? color + '18' : 'transparent',
                      color: active ? color : 'text.disabled',
                      fontWeight: active ? 600 : 400,
                      border: `1px solid ${active ? color : '#ccc'}`,
                      borderLeftWidth: 4,
                      cursor: 'pointer',
                      transition: 'all .15s',
                    }}
                  />
                )
              })}
            </Box>

            {chartData.length === 0 ? (
              <Box py={4} textAlign="center">
                <Typography variant="body2" color="text.secondary">
                  No booking activity for the selected facilities in this period.
                </Typography>
              </Box>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData} margin={{ right: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis
                    dataKey="label"
                    tick={{ fontSize: 11 }}
                    tickFormatter={fmtLabel}
                  />
                  <YAxis allowDecimals={false} />
                  <Tooltip
                    labelFormatter={v => {
                      if (granularity === 'day' || granularity === 'week') {
                        try { return format(new Date(v), 'dd MMM yyyy') } catch { return v }
                      }
                      if (granularity === 'month') {
                        try { return format(new Date(v + '-01'), 'MMM yyyy') } catch { return v }
                      }
                      return v
                    }}
                  />
                  <Legend />
                  {visibleReports.map((r, i) => (
                    <Line
                      key={r.asset_id}
                      type="monotone"
                      dataKey={r.asset_name}
                      stroke={LINE_COLORS[i % LINE_COLORS.length]}
                      strokeWidth={2.5}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                      connectNulls
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>

          {/* ── Summary cards ────────────────────────────────────────────── */}
          <Grid container spacing={2} mb={3}>
            {reports.map(r => {
              const typeInfo = ASSET_TYPES[r.asset_type] || ASSET_TYPES.other
              return (
                <Grid item xs={12} sm={6} md={4} key={r.asset_id}>
                  <Paper sx={{ p: 2.5, borderLeft: `4px solid ${typeInfo.color}` }}>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <Typography fontSize={22}>{typeInfo.icon}</Typography>
                      <Typography fontWeight={700} fontSize={14}>{r.asset_name}</Typography>
                    </Box>
                    <Stack spacing={0.5}>
                      {[
                        ['Total Bookings',  r.total_bookings],
                        ['Completed',       r.completed_bookings],
                        ['Cancelled',       r.cancelled_bookings],
                        ['Revenue',         `₹${(r.total_revenue || 0).toFixed(0)}`],
                        ['Utilization',     `${(r.utilization_rate || 0).toFixed(1)}%`],
                        ['Avg Duration',    `${Math.round(r.avg_booking_duration_minutes || 0)} min`],
                      ].map(([label, val]) => (
                        <Box key={label} display="flex" justifyContent="space-between">
                          <Typography variant="caption" color="text.secondary">{label}</Typography>
                          <Typography variant="caption" fontWeight={600}>{val}</Typography>
                        </Box>
                      ))}
                    </Stack>
                  </Paper>
                </Grid>
              )
            })}
          </Grid>

          {/* ── Utilization comparison ───────────────────────────────────── */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" fontWeight={600} mb={2}>Utilization Rate (%) by Facility</Typography>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={utilizationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={v => [`${v}%`, 'Utilization']} />
                <Bar dataKey="Rate" fill="#1976d2" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </>
      )}
    </Container>
  )
}

export default AssetReports
