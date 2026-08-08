import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  CheckCircle as ActivateIcon,
  Block as DeactivateIcon,
  PersonAdd as PersonAddIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import userService from '../../api/userService'
import { USER_ROLES } from '../../constants/roles'
import { formatDate } from '../../utils/formatters'

/**
 * Users management page (Admin only)
 */
const Users = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Pagination
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  
  // Edit dialog
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [editRole, setEditRole] = useState('')
  const [editStatus, setEditStatus] = useState(true)
  const [editName, setEditName] = useState('')
  const [editPhone, setEditPhone] = useState('')
  const [editUnitNumber, setEditUnitNumber] = useState('')
  const [editResidencyType, setEditResidencyType] = useState('')
  const [editFieldErrors, setEditFieldErrors] = useState({})
  
  // Delete dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [userToDelete, setUserToDelete] = useState(null)

  // Create tenant dialog
  const EMPTY_NEW_USER = { name: '', email: '', password: '', phone: '', unit_number: '', residency_type: 'tenant', role: USER_ROLES.RESIDENT }
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newUser, setNewUser] = useState(EMPTY_NEW_USER)
  const [createErrors, setCreateErrors] = useState({})

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await userService.getUsers({ limit: 100 })
      
      // Extract users array from response
      const usersArray = response?.users || response || []
      console.log('Fetched users:', usersArray)
      
      setUsers(usersArray)
    } catch (err) {
      console.error('Error fetching users:', err)
      
      // Handle error message - ensure it's a string
      let errorMessage = 'Failed to load users'
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map(e => e.msg || e).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      }
      
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // Filter users based on search and filters
  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.unit_number?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter
    const matchesStatus = statusFilter === 'all' || 
                          (statusFilter === 'active' && user.is_active) ||
                          (statusFilter === 'inactive' && !user.is_active)
    
    return matchesSearch && matchesRole && matchesStatus
  })

  // Paginated users
  const paginatedUsers = filteredUsers.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleEditClick = (user) => {
    setSelectedUser(user)
    setEditRole(user.role)
    setEditStatus(user.is_active)
    setEditName(user.name || '')
    setEditPhone(user.phone || '')
    setEditUnitNumber(user.unit_number || '')
    setEditResidencyType(user.residency_type || '')
    setEditFieldErrors({})
    setEditDialogOpen(true)
  }

  const handleEditSave = async () => {
    if (!selectedUser) return

    // Validate tenant mandatory fields before calling API
    if (editResidencyType === 'tenant') {
      const errs = {}
      if (!editName.trim()) errs.name = 'Tenant name is required'
      if (!editPhone.trim()) errs.phone = 'Tenant phone number is required'
      if (Object.keys(errs).length > 0) {
        setEditFieldErrors(errs)
        return
      }
    }
    // Validate unit number format
    if (editUnitNumber && !/^[A-Za-z]\d-\d{4}$/.test(editUnitNumber)) {
      setEditFieldErrors(p => ({ ...p, unit_number: 'Enter a valid unit number (e.g. B6-1001 or B7-0101)' }))
      return
    }
    setEditFieldErrors({})

    try {
      // Update contact info and residency type via PUT /users/{id}
      const contactChanged =
        editName !== (selectedUser.name || '') ||
        editPhone !== (selectedUser.phone || '') ||
        editUnitNumber !== (selectedUser.unit_number || '') ||
        editResidencyType !== (selectedUser.residency_type || '')

      if (contactChanged) {
        await userService.updateUser(selectedUser.id, {
          name: editName || undefined,
          phone: editPhone || undefined,
          unit_number: editUnitNumber || undefined,
          residency_type: editResidencyType || undefined,
        })
      }

      // Update role if changed
      if (editRole !== selectedUser.role) {
        await userService.updateUserRole(selectedUser.id, editRole)
      }
      
      // Update status if changed
      if (editStatus !== selectedUser.is_active) {
        await userService.updateUserStatus(selectedUser.id, editStatus)
      }

      toast.success('User updated successfully')
      setEditDialogOpen(false)
      fetchUsers()
    } catch (err) {
      console.error('Error updating user:', err)
      const errorMsg = typeof err.response?.data?.detail === 'string' 
        ? err.response.data.detail 
        : 'Failed to update user'
      toast.error(errorMsg)
    }
  }

  const handleDeleteClick = (user) => {
    setUserToDelete(user)
    setDeleteDialogOpen(true)
  }

  const handleCreateOpen = () => { setNewUser(EMPTY_NEW_USER); setCreateErrors({}); setCreateDialogOpen(true) }

  const handleCreateSave = async () => {
    const errs = {}
    if (!newUser.name.trim()) errs.name = 'Name is required'
    if (!newUser.email.trim()) errs.email = 'Email is required'
    if (!newUser.password || newUser.password.length < 8) errs.password = 'Password must be at least 8 characters'
    if (!newUser.phone.trim()) errs.phone = 'Phone is required'
    if (!newUser.unit_number.trim()) errs.unit_number = 'Unit number is required'
    else if (!/^[A-Za-z]\d-\d{4}$/.test(newUser.unit_number)) errs.unit_number = 'Format: B6-1001'
    if (Object.keys(errs).length > 0) { setCreateErrors(errs); return }
    setCreateErrors({})
    try {
      await userService.createUser(newUser)
      const label = newUser.residency_type === 'tenant' ? 'Tenant' : 'Resident'
      toast.success(`${label} registered successfully${
        newUser.residency_type === 'tenant' ? ' — previous tenant deactivated if any' : ''
      }`)
      setCreateDialogOpen(false)
      fetchUsers()
    } catch (err) {
      const msg = typeof err.response?.data?.detail === 'string' ? err.response.data.detail : 'Failed to create user'
      toast.error(msg)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return

    try {
      await userService.deleteUser(userToDelete.id)
      toast.success('User deleted successfully')
      setDeleteDialogOpen(false)
      setUserToDelete(null)
      fetchUsers()
    } catch (err) {
      console.error('Error deleting user:', err)
      const errorMsg = typeof err.response?.data?.detail === 'string' 
        ? err.response.data.detail 
        : 'Failed to delete user'
      toast.error(errorMsg)
    }
  }

  const handleToggleStatus = async (user) => {
    const newStatus = !user.is_active
    const action = newStatus ? 'activated' : 'deactivated'
    
    try {
      await userService.updateUserStatus(user.id, newStatus)
      toast.success(`User ${action} successfully`)
      fetchUsers()
    } catch (err) {
      console.error(`Error ${action} user:`, err)
      const errorMsg = typeof err.response?.data?.detail === 'string' 
        ? err.response.data.detail 
        : `Failed to ${action.slice(0, -1)} user`
      toast.error(errorMsg)
    }
  }

  const getRoleColor = (role) => {
    const colors = {
      admin: 'error',
      resident: 'primary',
      contractor: 'warning',
      facility_manager: 'info',
      builder: 'secondary',
    }
    return colors[role] || 'default'
  }

  return (
    <Box sx={{ position: 'relative', zIndex: 1 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" sx={{ color: 'white' }}>Users Management</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={<PersonAddIcon />}
            onClick={handleCreateOpen}
            sx={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.4)',
              color: 'white',
              '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' },
            }}
          >
            Register New Tenant
          </Button>
          <IconButton 
            onClick={fetchUsers} 
            color="primary" 
            disabled={loading}
            sx={{ 
              color: 'white',
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.25)',
              },
            }}
          >
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 2,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper 
        sx={{ 
          p: 2, 
          mb: 2,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
        }}
      >
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            placeholder="Search by name, email, or unit..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ flexGrow: 1 }}
          />
          
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={roleFilter}
              label="Role"
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <MenuItem value="all">All Roles</MenuItem>
              <MenuItem value={USER_ROLES.RESIDENT}>Resident</MenuItem>
              <MenuItem value={USER_ROLES.ADMIN}>Admin</MenuItem>
              <MenuItem value={USER_ROLES.CONTRACTOR}>Contractor</MenuItem>
              <MenuItem value={USER_ROLES.FACILITY_MANAGER}>Facility Manager</MenuItem>
              <MenuItem value={USER_ROLES.BUILDER}>Builder</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
        </Stack>
      </Paper>

      {/* Users Table */}
      <Paper 
        sx={{ 
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : filteredUsers.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No users found
            </Typography>
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>Occupancy</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Joined</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paginatedUsers.map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Chip 
                          label={user.role} 
                          size="small" 
                          color={getRoleColor(user.role)}
                        />
                      </TableCell>
                      <TableCell>{user.unit_number || '-'}</TableCell>
                      <TableCell>
                        {user.residency_type ? (
                          <Chip
                            label={user.residency_type === 'owner' ? 'Owner' : 'Tenant'}
                            size="small"
                            color={user.residency_type === 'owner' ? 'primary' : 'secondary'}
                            variant="outlined"
                          />
                        ) : '-'}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={user.is_active ? 'Active' : 'Inactive'} 
                          size="small" 
                          color={user.is_active ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>{formatDate(user.created_at)}</TableCell>
                      <TableCell align="right">
                        {user.is_active ? (
                          <IconButton 
                            size="small" 
                            onClick={() => handleToggleStatus(user)}
                            color="warning"
                            title="Deactivate user"
                          >
                            <DeactivateIcon fontSize="small" />
                          </IconButton>
                        ) : (
                          <IconButton 
                            size="small" 
                            onClick={() => handleToggleStatus(user)}
                            color="success"
                            title="Activate user"
                          >
                            <ActivateIcon fontSize="small" />
                          </IconButton>
                        )}
                        <IconButton 
                          size="small" 
                          onClick={() => handleEditClick(user)}
                          color="primary"
                          title="Edit user"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteClick(user)}
                          color="error"
                          title="Delete user"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={filteredUsers.length}
              page={page}
              onPageChange={handleChangePage}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </>
        )}
      </Paper>

      {/* Edit User Dialog */}
      <Dialog open={editDialogOpen} onClose={() => { setEditDialogOpen(false); setEditFieldErrors({}) }} maxWidth="sm" fullWidth>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              User: {selectedUser?.name} ({selectedUser?.email})
            </Typography>

            {editResidencyType === 'tenant' && (
              <Alert severity="info" sx={{ mt: 1, mb: 1 }}>
                Name, email and phone are <strong>required</strong> for tenants so visitor approval requests are routed correctly.
              </Alert>
            )}

            <TextField
              label={editResidencyType === 'tenant' ? 'Tenant Full Name *' : 'Full Name'}
              fullWidth
              sx={{ mt: 2 }}
              value={editName}
              onChange={(e) => { setEditName(e.target.value); setEditFieldErrors(p => ({ ...p, name: undefined })) }}
              error={!!editFieldErrors.name}
              helperText={editFieldErrors.name}
            />

            {/* Email shown read-only so admin can verify it's correct */}
            <TextField
              label="Email Address"
              fullWidth
              sx={{ mt: 2 }}
              value={selectedUser?.email || ''}
              disabled
              helperText={editResidencyType === 'tenant' ? 'Visitor requests will be sent to this email' : ''}
            />

            <TextField
              label={editResidencyType === 'tenant' ? 'Tenant Phone Number *' : 'Phone'}
              fullWidth
              sx={{ mt: 2 }}
              value={editPhone}
              onChange={(e) => { setEditPhone(e.target.value); setEditFieldErrors(p => ({ ...p, phone: undefined })) }}
              error={!!editFieldErrors.phone}
              helperText={editFieldErrors.phone}
            />

            <TextField
              label="Unit Number"
              fullWidth
              sx={{ mt: 2 }}
              value={editUnitNumber}
              onChange={(e) => { setEditUnitNumber(e.target.value); setEditFieldErrors(p => ({ ...p, unit_number: undefined })) }}
              placeholder="B6-1001"
              error={!!editFieldErrors.unit_number}
              helperText={editFieldErrors.unit_number || 'Format: B6-1001 or B7-0101'}
            />

            {/* Residency type only relevant for residents */}
            {(editRole === USER_ROLES.RESIDENT || selectedUser?.role === USER_ROLES.RESIDENT) && (
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Occupancy Type</InputLabel>
                <Select
                  value={editResidencyType}
                  label="Occupancy Type"
                  onChange={(e) => { setEditResidencyType(e.target.value); setEditFieldErrors({}) }}
                >
                  <MenuItem value="">Not specified</MenuItem>
                  <MenuItem value="owner">Owner</MenuItem>
                  <MenuItem value="tenant">Tenant / Renter</MenuItem>
                </Select>
              </FormControl>
            )}
            
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Role</InputLabel>
              <Select
                value={editRole}
                label="Role"
                onChange={(e) => setEditRole(e.target.value)}
              >
                <MenuItem value={USER_ROLES.RESIDENT}>Resident</MenuItem>
                <MenuItem value={USER_ROLES.ADMIN}>Admin</MenuItem>
                <MenuItem value={USER_ROLES.CONTRACTOR}>Contractor</MenuItem>
                <MenuItem value={USER_ROLES.FACILITY_MANAGER}>Facility Manager</MenuItem>
                <MenuItem value={USER_ROLES.BUILDER}>Builder</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={editStatus}
                label="Status"
                onChange={(e) => setEditStatus(e.target.value)}
              >
                <MenuItem value={true}>Active</MenuItem>
                <MenuItem value={false}>Inactive</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setEditDialogOpen(false); setEditFieldErrors({}) }}>Cancel</Button>
          <Button onClick={handleEditSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete user <strong>{userToDelete?.name}</strong>?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Register New Tenant / User Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Register New Tenant</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mt: 1, mb: 2 }}>
            If this unit already has an active tenant, they will be automatically deactivated.
          </Alert>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Full Name *"
              value={newUser.name}
              onChange={e => setNewUser(p => ({ ...p, name: e.target.value }))}
              error={!!createErrors.name} helperText={createErrors.name}
              fullWidth
            />
            <TextField
              label="Email Address *"
              type="email"
              value={newUser.email}
              onChange={e => setNewUser(p => ({ ...p, email: e.target.value }))}
              error={!!createErrors.email} helperText={createErrors.email}
              fullWidth
            />
            <TextField
              label="Password *"
              type="password"
              value={newUser.password}
              onChange={e => setNewUser(p => ({ ...p, password: e.target.value }))}
              error={!!createErrors.password} helperText={createErrors.password || 'Min 8 characters'}
              fullWidth
            />
            <TextField
              label="Phone Number *"
              value={newUser.phone}
              onChange={e => setNewUser(p => ({ ...p, phone: e.target.value }))}
              error={!!createErrors.phone} helperText={createErrors.phone}
              fullWidth
            />
            <TextField
              label="Unit Number *"
              placeholder="B6-1001"
              value={newUser.unit_number}
              onChange={e => setNewUser(p => ({ ...p, unit_number: e.target.value }))}
              error={!!createErrors.unit_number} helperText={createErrors.unit_number || 'Format: B6-1001'}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Occupancy Type</InputLabel>
              <Select
                value={newUser.residency_type}
                label="Occupancy Type"
                onChange={e => setNewUser(p => ({ ...p, residency_type: e.target.value }))}
              >
                <MenuItem value="tenant">Tenant / Renter</MenuItem>
                <MenuItem value="owner">Owner</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateSave} variant="contained" startIcon={<PersonAddIcon />}>
            Register
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Users
