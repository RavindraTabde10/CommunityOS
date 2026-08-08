import { useState, useEffect } from 'react'
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  CircularProgress,
  Alert,
  Paper,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import { toast } from 'react-toastify'
import issueService from '../../api/issueService'
import IssuePreviewCard from '../../components/dashboard/IssuePreviewCard'

/**
 * IssueList page - Display all issues with filters
 */
const IssueList = () => {
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [reporterFilter, setReporterFilter] = useState('all')
  const [assigneeFilter, setAssigneeFilter] = useState('all')

  useEffect(() => {
    loadIssues()
  }, [statusFilter, categoryFilter])

  const loadIssues = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = {}
      if (statusFilter !== 'all') params.status = statusFilter
      if (categoryFilter !== 'all') params.category = categoryFilter

      const data = await issueService.getIssues(params)
      setIssues(data)
    } catch (err) {
      console.error('Error loading issues:', err)
      setError(err.response?.data?.detail || 'Failed to load issues')
      toast.error('Failed to load issues')
    } finally {
      setLoading(false)
    }
  }

  // Derive unique reporters and assignees from loaded issues
  const reporters = [...new Map(
    issues.filter(i => i.reporter).map(i => [i.reporter.id, i.reporter])
  ).values()]

  const assignees = [...new Map(
    issues.filter(i => i.assignee).map(i => [i.assignee.id, i.assignee])
  ).values()]

  const filteredIssues = issues.filter(issue => {
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      const matches =
        issue.title?.toLowerCase().includes(search) ||
        issue.description?.toLowerCase().includes(search) ||
        issue.id?.toLowerCase().includes(search) ||
        issue.reporter?.name?.toLowerCase().includes(search) ||
        issue.assignee?.name?.toLowerCase().includes(search)
      if (!matches) return false
    }
    if (reporterFilter !== 'all' && issue.reporter?.id !== reporterFilter) return false
    if (assigneeFilter !== 'all') {
      if (assigneeFilter === 'unassigned') {
        if (issue.assignee) return false
      } else if (issue.assignee?.id !== assigneeFilter) {
        return false
      }
    }
    return true
  })

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold" sx={{ color: 'white' }}>
        All Issues
      </Typography>

      {/* Filters */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 3, 
          mb: 3,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
        }}
      >
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search issues..."
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
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="resolved">Resolved</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={categoryFilter}
                label="Category"
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <MenuItem value="all">All Categories</MenuItem>
                <MenuItem value="electrical">Electrical</MenuItem>
                <MenuItem value="plumbing">Plumbing</MenuItem>
                <MenuItem value="painting">Painting</MenuItem>
                <MenuItem value="carpentry">Carpentry</MenuItem>
                <MenuItem value="flooring">Flooring</MenuItem>
                <MenuItem value="civil">Civil</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Reporter</InputLabel>
              <Select
                value={reporterFilter}
                label="Reporter"
                onChange={(e) => setReporterFilter(e.target.value)}
              >
                <MenuItem value="all">All Reporters</MenuItem>
                {reporters.map((r) => (
                  <MenuItem key={r.id} value={r.id}>{r.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Assignee</InputLabel>
              <Select
                value={assigneeFilter}
                label="Assignee"
                onChange={(e) => setAssigneeFilter(e.target.value)}
              >
                <MenuItem value="all">All Assignees</MenuItem>
                <MenuItem value="unassigned">Unassigned</MenuItem>
                {assignees.map((a) => (
                  <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Issue List */}
      {!loading && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Found {filteredIssues.length} issue(s)
          </Typography>
          
          {filteredIssues.length > 0 ? (
            <Grid container spacing={2}>
              {filteredIssues.map((issue) => (
                <Grid item xs={12} md={6} key={issue.id}>
                  <IssuePreviewCard issue={issue} />
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper 
              elevation={3} 
              sx={{ 
                p: 8, 
                textAlign: 'center',
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.5)',
              }}
            >
              <Typography variant="h6" color="text.secondary">
                No issues found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {searchTerm || statusFilter !== 'all' || categoryFilter !== 'all' || reporterFilter !== 'all' || assigneeFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Create your first issue to get started'}
              </Typography>
            </Paper>
          )}
        </>
      )}
    </Container>
  )
}

export default IssueList
