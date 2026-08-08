import { useState } from 'react'
import {
  Box, Container, Typography, Paper, Button, MenuItem, Select,
  FormControl, InputLabel, TextField, ToggleButtonGroup, ToggleButton,
  Alert, CircularProgress, Divider, Chip, Stack,
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import FileDownloadIcon from '@mui/icons-material/FileDownload'
import reportService from '../../api/reportService'
import { format, subDays } from 'date-fns'
import { toast } from 'react-toastify'

const REPORT_TYPES = [
  { value: 'dashboard',   label: 'Dashboard Overview',        desc: 'Summary stats: issues, users, assets, bookings' },
  { value: 'issues',      label: 'Issue Analytics',           desc: 'Issue distribution, trends, resolution times' },
  { value: 'contractors', label: 'Contractor Performance',    desc: 'Ratings, jobs completed, response times' },
  { value: 'assets',      label: 'Asset Usage',               desc: 'Bookings, revenue, utilization rates' },
]

const ExportReports = () => {
  const [reportType, setReportType]  = useState('issues')
  const [exportFmt,  setExportFmt]   = useState('csv')
  const [fromDate,   setFromDate]    = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [toDate,     setToDate]      = useState(format(new Date(), 'yyyy-MM-dd'))
  const [loading,    setLoading]     = useState(false)
  const [lastExport, setLastExport]  = useState(null)

  const handleExport = async () => {
    try {
      setLoading(true)
      const payload = {
        report_type: reportType,
        format: exportFmt,
        filters: { from_date: fromDate, to_date: toDate },
      }
      const res = await reportService.exportReport(payload)

      if (exportFmt === 'csv') {
        // res is a Blob
        const url = URL.createObjectURL(res)
        const a = document.createElement('a')
        a.href = url
        a.download = `${reportType}_report_${format(new Date(), 'yyyyMMdd')}.csv`
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      } else {
        // res is JSON — trigger download as .json file
        const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${reportType}_report_${format(new Date(), 'yyyyMMdd')}.json`
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      }

      setLastExport({ type: reportType, format: exportFmt, time: new Date() })
      toast.success('Report downloaded successfully!')
    } catch (err) {
      if (err?.response?.status === 403) {
        toast.error('Admin access required to export reports.')
      } else {
        toast.error('Export failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const selected = REPORT_TYPES.find(r => r.value === reportType)

  return (
    <Container maxWidth="sm" sx={{ py: 3 }}>
      <Box display="flex" alignItems="center" gap={1} mb={3}>
        <FileDownloadIcon color="primary" />
        <Typography variant="h5" fontWeight={700}>Export Reports</Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Stack spacing={3}>
          {/* Report type */}
          <FormControl fullWidth size="small">
            <InputLabel>Report Type</InputLabel>
            <Select value={reportType} label="Report Type" onChange={e => setReportType(e.target.value)}>
              {REPORT_TYPES.map(r => (
                <MenuItem key={r.value} value={r.value}>{r.label}</MenuItem>
              ))}
            </Select>
          </FormControl>

          {selected && (
            <Alert severity="info" icon={false} sx={{ py: 0.5 }}>
              <Typography variant="body2">{selected.desc}</Typography>
            </Alert>
          )}

          {/* Date range */}
          <Box display="flex" gap={2}>
            <TextField size="small" type="date" label="From" fullWidth value={fromDate}
              onChange={e => setFromDate(e.target.value)} InputLabelProps={{ shrink: true }} />
            <TextField size="small" type="date" label="To" fullWidth value={toDate}
              onChange={e => setToDate(e.target.value)} InputLabelProps={{ shrink: true }} />
          </Box>

          {/* Format toggle */}
          <Box>
            <Typography variant="body2" color="text.secondary" mb={1}>Format</Typography>
            <ToggleButtonGroup
              value={exportFmt}
              exclusive
              onChange={(_, v) => v && setExportFmt(v)}
              size="small"
            >
              <ToggleButton value="csv">
                CSV (Excel)
              </ToggleButton>
              <ToggleButton value="json">
                JSON (API)
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          <Divider />

          <Button
            variant="contained"
            size="large"
            fullWidth
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <DownloadIcon />}
            onClick={handleExport}
            disabled={loading}
          >
            {loading ? 'Generating...' : `Download ${exportFmt.toUpperCase()}`}
          </Button>

          {lastExport && (
            <Alert severity="success" icon={<DownloadIcon fontSize="small" />}>
              Last export: <strong>{lastExport.type}</strong> as{' '}
              <strong>{lastExport.format.toUpperCase()}</strong> at{' '}
              {format(lastExport.time, 'HH:mm:ss')}
            </Alert>
          )}
        </Stack>
      </Paper>
    </Container>
  )
}

export default ExportReports
