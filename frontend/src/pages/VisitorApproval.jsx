import { useState, useEffect, useCallback } from 'react'
import {
  Container, Typography, Box, Paper, Chip, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, CircularProgress,
  IconButton, Tooltip, Divider, Alert, Badge, Button, Tabs, Tab,
} from '@mui/material'
import {
  CheckCircle as ApproveIcon,
  Cancel as DenyIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import { format } from 'date-fns'
import visitorService from '../api/visitorService'

const STATUS_CONFIG = {
  pending:     { label: 'Pending',      color: 'warning' },
  approved:    { label: 'Approved',     color: 'success' },
  denied:      { label: 'Denied',       color: 'error' },
  checked_out: { label: 'Checked Out',  color: 'default' },
}

const VisitorApproval = () => {
  const [allVisitors, setAllVisitors] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState(0)
  const [processing, setProcessing] = useState(null)

  const fetchVisitors = useCallback(async () => {
    try {
      setLoading(true)
      const res = await visitorService.getMyVisitors()
      setAllVisitors(res.data || [])
    } catch {
      toast.error('Failed to load visitor requests')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchVisitors() }, [fetchVisitors])

  const pending = allVisitors.filter((v) => v.status === 'pending')
  const history = allVisitors.filter((v) => v.status !== 'pending')

  const handleAction = async (id, status) => {
    try {
      setProcessing(id)
      await visitorService.updateStatus(id, status)
      toast.success(status === 'approved' ? 'Visitor approved' : 'Visitor denied')
      fetchVisitors()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Action failed')
    } finally {
      setProcessing(null)
    }
  }

  const fmtTime = (dt) => dt ? format(new Date(dt), 'dd MMM yyyy, HH:mm') : '—'

  const renderTable = (rows, showActions = false) => (
    rows.length === 0 ? (
      <Alert severity="info" sx={{ mt: 1 }}>No records found.</Alert>
    ) : (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell><strong>Visitor</strong></TableCell>
              <TableCell><strong>Phone</strong></TableCell>
              <TableCell><strong>Purpose</strong></TableCell>
              <TableCell><strong>Vehicle</strong></TableCell>
              <TableCell><strong>Check In</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              {showActions && <TableCell align="center"><strong>Action</strong></TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((v) => (
              <TableRow key={v.id} hover>
                <TableCell>{v.visitor_name}</TableCell>
                <TableCell>{v.visitor_phone || '—'}</TableCell>
                <TableCell>{v.purpose || '—'}</TableCell>
                <TableCell>{v.vehicle_number || '—'}</TableCell>
                <TableCell>{fmtTime(v.check_in_time)}</TableCell>
                <TableCell>
                  <Chip
                    label={STATUS_CONFIG[v.status]?.label || v.status}
                    color={STATUS_CONFIG[v.status]?.color || 'default'}
                    size="small"
                  />
                </TableCell>
                {showActions && (
                  <TableCell align="center">
                    {processing === v.id ? (
                      <CircularProgress size={20} />
                    ) : (
                      <>
                        <Tooltip title="Approve">
                          <IconButton size="small" color="success" onClick={() => handleAction(v.id, 'approved')}>
                            <ApproveIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Deny">
                          <IconButton size="small" color="error" onClick={() => handleAction(v.id, 'denied')}>
                            <DenyIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  )

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
          <Box>
            <Typography variant="h5" fontWeight={700}>Visitor Approvals</Typography>
            <Typography variant="body2" color="text.secondary">
              Approve or deny visitors who wish to enter your unit
            </Typography>
          </Box>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchVisitors}><RefreshIcon /></IconButton>
          </Tooltip>
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
          <Tab
            label={
              <Badge badgeContent={pending.length} color="error" max={99}>
                <Box sx={{ pr: pending.length > 0 ? 2 : 0 }}>Pending Approvals</Box>
              </Badge>
            }
          />
          <Tab label="Visit History" />
        </Tabs>

        {loading ? (
          <Box sx={{ textAlign: 'center', py: 4 }}><CircularProgress /></Box>
        ) : (
          <>
            {tab === 0 && renderTable(pending, true)}
            {tab === 1 && renderTable(history, false)}
          </>
        )}
      </Paper>
    </Container>
  )
}

export default VisitorApproval
