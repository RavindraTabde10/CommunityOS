import { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material'
import { CheckCircle, Cancel, Refresh } from '@mui/icons-material'
import userService from '../../api/userService'
import { useToast } from '../../hooks/useToast'
import { formatDate } from '../../utils/formatters'

/**
 * Pending Users page for admin approval
 */
const PendingUsers = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [processingUserId, setProcessingUserId] = useState(null)
  const toast = useToast()

  const fetchPendingUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await userService.getUsers({ is_active: false, limit: 100 })
      console.log('API Response:', response)
      
      // Extract users array from response
      const usersArray = response?.users || response || []
      console.log('Users array:', usersArray)
      console.log('Users count:', usersArray.length)
      
      setUsers(usersArray)
    } catch (err) {
      console.error('Error fetching pending users:', err)
      console.error('Error response:', err.response)
      setError(err.response?.data?.detail || 'Failed to load pending users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPendingUsers()
  }, [])

  useEffect(() => {
    console.log('Users state updated:', users)
    console.log('Users state length:', users.length)
  }, [users])

  const handleApprove = async (userId) => {
    try {
      setProcessingUserId(userId)
      await userService.updateUserStatus(userId, true)
      toast.success('User approved successfully')
      // Remove from list or refresh
      setUsers(users.filter(user => user.id !== userId))
    } catch (err) {
      console.error('Error approving user:', err)
      toast.error(err.response?.data?.detail || 'Failed to approve user')
    } finally {
      setProcessingUserId(null)
    }
  }

  const handleReject = async (userId) => {
    // For now, just keep them as inactive
    // In future, we might want to delete or mark as rejected
    toast.info('User rejection not implemented yet')
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress sx={{ color: 'white' }} />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" fontWeight={600} sx={{ color: 'white' }}>
            Pending User Approvals
          </Typography>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchPendingUsers} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
            }}
          >
            {error}
          </Alert>
        )}

        {users.length === 0 && !loading ? (
          <Card 
            sx={{ 
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            }}
          >
            <CardContent>
              <Alert severity="info">
                No pending user approvals. All registrations have been processed.
              </Alert>
            </CardContent>
          </Card>
        ) : (
          <Card 
            sx={{ 
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
            }}
          >
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Name</strong></TableCell>
                    <TableCell><strong>Email</strong></TableCell>
                    <TableCell><strong>Role</strong></TableCell>
                    <TableCell><strong>Unit</strong></TableCell>
                    <TableCell><strong>Phone</strong></TableCell>
                    <TableCell><strong>Registered</strong></TableCell>
                    <TableCell align="center"><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Chip 
                          label={user.role.toUpperCase()} 
                          size="small" 
                          color="default"
                        />
                      </TableCell>
                      <TableCell>{user.unit_number || '-'}</TableCell>
                      <TableCell>{user.phone || '-'}</TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(user.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box display="flex" gap={1} justifyContent="center">
                          <Button
                            variant="contained"
                            color="success"
                            size="small"
                            startIcon={<CheckCircle />}
                            onClick={() => handleApprove(user.id)}
                            disabled={processingUserId === user.id}
                          >
                            Approve
                          </Button>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            startIcon={<Cancel />}
                            onClick={() => handleReject(user.id)}
                            disabled={processingUserId === user.id}
                          >
                            Reject
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Card>
        )}
      </Container>
  )
}

export default PendingUsers
