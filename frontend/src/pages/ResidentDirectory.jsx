import { useState, useEffect, useMemo } from 'react'
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Box,
  TextField,
  InputAdornment,
  Avatar,
  IconButton,
  Chip,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'
import HomeIcon from '@mui/icons-material/Home'
import PersonIcon from '@mui/icons-material/Person'
import KeyIcon from '@mui/icons-material/Key'
import FilterListIcon from '@mui/icons-material/FilterList'
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material'
import apiClient from '../api/client'
import { toast } from 'react-toastify'

/**
 * Resident Directory Page
 * Displays contact information for all residents in the society
 */
const ResidentDirectory = () => {
  const [residents, setResidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [residencyFilter, setResidencyFilter] = useState('all')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    loadResidents()
  }, [page, rowsPerPage])

  const loadResidents = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiClient.get('/users', {
        params: {
          skip: page * rowsPerPage,
          limit: rowsPerPage,
          role: 'resident',
          is_active: true
        }
      })
      
      setResidents(response.data.users || [])
      setTotalCount(response.data.total || 0)
    } catch (err) {
      console.error('Error loading residents:', err)
      setError(err.response?.data?.detail || 'Failed to load residents')
      toast.error('Failed to load residents directory')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const filteredResidents = residents.filter(resident => {
    const matchesSearch =
      resident.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      resident.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      resident.unit_number?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesResidency =
      residencyFilter === 'all' || resident.residency_type === residencyFilter
    return matchesSearch && matchesResidency
  })

  // Unit-level summary: per unit, tenant takes priority over owner
  const unitSummary = useMemo(() => {
    const map = residents.reduce((m, r) => {
      if (!r.unit_number) return m
      const existing = m.get(r.unit_number)
      if (!existing || r.residency_type === 'tenant') m.set(r.unit_number, r)
      return m
    }, new Map())
    const units = [...map.values()]
    return {
      totalUnits: map.size,
      withPhone: units.filter(r => r.phone).length,
      tenantUnits: units.filter(r => r.residency_type === 'tenant').length,
      ownerUnits: units.filter(r => r.residency_type === 'owner').length,
    }
  }, [residents])

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          📖 Resident Directory
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Contact information for all residents in the society
        </Typography>
      </Box>

      {/* Search & Filter Bar */}
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            sx={{ flex: 1, minWidth: 240 }}
            placeholder="Search by name, email, or unit number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <FormControl sx={{ minWidth: 180 }}>
            <InputLabel id="residency-filter-label">
              <FilterListIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
              Occupancy Type
            </InputLabel>
            <Select
              labelId="residency-filter-label"
              value={residencyFilter}
              label="Occupancy Type"
              onChange={(e) => setResidencyFilter(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="owner">Owner</MenuItem>
              <MenuItem value="tenant">Tenant</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Summary Card */}
      {!loading && (
        <Paper elevation={2} sx={{ p: 2, mb: 3, bgcolor: 'primary.light', color: 'white' }}>
          <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap', alignItems: 'center' }}>
            <Box>
              <Typography variant="h5" fontWeight="bold">{unitSummary.totalUnits}</Typography>
              <Typography variant="caption">Total Units</Typography>
            </Box>
            <Box>
              <Typography variant="h5" fontWeight="bold">{unitSummary.ownerUnits}</Typography>
              <Typography variant="caption">Owner-Occupied</Typography>
            </Box>
            <Box>
              <Typography variant="h5" fontWeight="bold">{unitSummary.tenantUnits}</Typography>
              <Typography variant="caption">Rented (Tenant)</Typography>
            </Box>
            <Box>
              <Typography variant="h5" fontWeight="bold">{unitSummary.withPhone}</Typography>
              <Typography variant="caption">Units With Phone</Typography>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Directory Table */}
      <Paper elevation={3}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Resident</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Unit Number</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Email</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Phone</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Occupancy</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 8 }}>
                    <CircularProgress />
                    <Typography variant="body2" sx={{ mt: 2 }}>
                      Loading residents...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : filteredResidents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 8 }}>
                    <Typography variant="body1" color="text.secondary">
                      {searchTerm ? 'No residents found matching your search' : 'No residents found'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredResidents.map((resident) => {
                  const isOwner = resident.residency_type === 'owner'
                  const isTenant = resident.residency_type === 'tenant'
                  return (
                  <TableRow
                    key={resident.id}
                    sx={{
                      '&:hover': { bgcolor: 'action.hover' },
                      '&:nth-of-type(even)': { bgcolor: 'action.hover' }
                    }}
                  >
                    {/* Resident Info */}
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {resident.name?.charAt(0).toUpperCase() || 'R'}
                        </Avatar>
                        <Box>
                          <Typography variant="body1" fontWeight="bold">
                            {resident.name}
                          </Typography>
                          {resident.is_active ? (
                            <Chip label="Active" size="small" color="success" sx={{ height: 20 }} />
                          ) : (
                            <Chip label="Inactive" size="small" color="default" sx={{ height: 20 }} />
                          )}
                        </Box>
                      </Box>
                    </TableCell>

                    {/* Unit Number */}
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <HomeIcon fontSize="small" color="action" />
                        <Typography variant="body2">
                          {resident.unit_number || 'N/A'}
                        </Typography>
                      </Box>
                    </TableCell>

                    {/* Email */}
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 250 }}>
                        {resident.email || 'N/A'}
                      </Typography>
                    </TableCell>

                    {/* Phone */}
                    <TableCell>
                      <Typography variant="body2">
                        {resident.phone || 'N/A'}
                      </Typography>
                    </TableCell>

                    {/* Occupancy Type */}
                    <TableCell>
                      {isOwner && (
                        <Chip
                          icon={<KeyIcon />}
                          label="Owner"
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      {isTenant && (
                        <Chip
                          icon={<PersonIcon />}
                          label="Tenant"
                          size="small"
                          color="secondary"
                          variant="outlined"
                        />
                      )}
                      {!isOwner && !isTenant && (
                        <Typography variant="body2" color="text.disabled">N/A</Typography>
                      )}
                    </TableCell>

                    {/* Actions */}
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                        {resident.email && (
                          <Tooltip title={`Email ${resident.name}`}>
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => window.open(`mailto:${resident.email}`)}
                            >
                              <EmailIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {resident.phone && (
                          <Tooltip title={`Call ${resident.name}`}>
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => window.open(`tel:${resident.phone}`)}
                            >
                              <PhoneIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        {!loading && filteredResidents.length > 0 && (
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        )}
      </Paper>
    </Container>
  )
}

export default ResidentDirectory
