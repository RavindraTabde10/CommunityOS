/**
 * Polls Page
 * Lists all created polls with admin controls
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  LinearProgress,
} from '@mui/material'
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import { USER_ROLES } from '../constants/roles'
import { ROUTES } from '../utils/constants'
import { pollsAPI } from '../api/polls'

const Polls = () => {
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)
  const isAdmin = user?.role === USER_ROLES.ADMIN

  const [polls, setPolls] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPoll, setSelectedPoll] = useState(null)
  const [pollDetailsLoading, setPollDetailsLoading] = useState(false)
  const [voteLoadingIndex, setVoteLoadingIndex] = useState(null)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, pollId: null, question: '' })
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchPolls()
  }, [])

  const fetchPolls = async () => {
    try {
      setLoading(true)
      const response = await pollsAPI.getAll()
      setPolls(response.data.polls || [])
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const handleOpenPoll = async (pollId) => {
    try {
      setPollDetailsLoading(true)
      const response = await pollsAPI.getById(pollId)
      setSelectedPoll(response.data)
    } finally {
      setPollDetailsLoading(false)
    }
  }

  const handleVote = async (optionIndex) => {
    if (!selectedPoll || !user?.id) {
      return
    }

    try {
      setVoteLoadingIndex(optionIndex)
      const response = await pollsAPI.vote(selectedPoll.id, {
        option_index: optionIndex
      })

      const updatedPoll = response.data
      setSelectedPoll(updatedPoll)
      setPolls((prev) =>
        prev.map((poll) => (String(poll.id) === String(updatedPoll.id) ? updatedPoll : poll))
      )
    } catch (error) {
      console.error('Error submitting vote:', error)
    } finally {
      setVoteLoadingIndex(null)
    }
  }

  const getCurrentUserVoteIndex = (poll) => {
    if (!poll || !user?.id) {
      return -1
    }

    return (poll.votes || []).find((vote) => String(vote.user_id) === String(user.id))?.option_index ?? -1
  }

  const handleDeleteClick = (poll) => {
    setDeleteDialog({ open: false, pollId: null, question: '' })
    setDeleteDialog({ open: true, pollId: poll.id, question: poll.question })
  }

  const handleDeleteConfirm = async () => {
    try {
      setDeleting(true)
      await pollsAPI.delete(deleteDialog.pollId)
      setPolls((prev) => prev.filter((p) => p.id !== deleteDialog.pollId))
      toast.success('Poll deleted successfully')
      setDeleteDialog({ open: false, pollId: null, question: '' })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete poll')
    } finally {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Polls
        </Typography>
        {isAdmin && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/polls/create')}
          >
            Create Poll
          </Button>
        )}
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: 'grey.100' }}>
              <TableCell><strong>Question</strong></TableCell>
              <TableCell><strong>Options</strong></TableCell>
              <TableCell><strong>Votes</strong></TableCell>
              <TableCell><strong>Created On</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell align="right"><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {polls.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No polls created yet
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              polls.map((poll) => (
                <TableRow key={poll.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {poll.question}
                    </Typography>
                  </TableCell>
                  <TableCell>{poll.options?.length || 0}</TableCell>
                  <TableCell>{poll.total_votes ?? poll.votes?.length ?? 0}</TableCell>
                  <TableCell>{formatDateTime(poll.created_at)}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={poll.is_active ? 'Active' : 'Inactive'}
                      color={poll.is_active ? 'success' : 'default'}
                    />
                    {poll.active_till && (
                      <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                        Expires: {formatDateTime(poll.active_till)}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenPoll(poll.id)}
                      title="View Poll"
                    >
                      <ViewIcon fontSize="small" />
                    </IconButton>
                    {isAdmin && (
                      <IconButton
                        size="small"
                        onClick={() => navigate(ROUTES.POLLS_EDIT(poll.id))}
                        title="Edit Poll"
                        sx={{ ml: 0.5 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    )}
                    {isAdmin && (
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(poll)}
                        title="Delete Poll"
                        sx={{ ml: 0.5 }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={Boolean(selectedPoll)} onClose={() => setSelectedPoll(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Poll Details</DialogTitle>
        <DialogContent dividers>
          {pollDetailsLoading ? (
            <Box sx={{ py: 3 }}>
              <LinearProgress />
            </Box>
          ) : (
            <>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                {selectedPoll?.question}
              </Typography>

              {selectedPoll?.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedPoll.description}
                </Typography>
              )}

              <Typography variant="body2" sx={{ mb: 2 }}>
                Total Votes: <strong>{selectedPoll?.total_votes ?? selectedPoll?.votes?.length ?? 0}</strong>
              </Typography>

              <Typography variant="body2" fontWeight="bold" sx={{ mb: 1 }}>
                Options
              </Typography>

              {(selectedPoll?.options || []).map((option, index) => {
                const optionVotes = selectedPoll?.option_vote_counts?.[index] ?? 0
                const totalVotes = selectedPoll?.total_votes ?? 0
                const percentage = totalVotes > 0 ? (optionVotes / totalVotes) * 100 : 0
                const userVoteIndex = getCurrentUserVoteIndex(selectedPoll)
                const isCurrentUserChoice = userVoteIndex === index

                return (
                  <Box key={`${option}-${index}`} sx={{ mb: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1.5, p: 1.5 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 2, mb: 1 }}>
                      <Typography variant="body2" fontWeight={isCurrentUserChoice ? 'bold' : 'regular'}>
                        {index + 1}. {option}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {optionVotes} vote(s) • {percentage.toFixed(0)}%
                      </Typography>
                    </Box>

                    <LinearProgress variant="determinate" value={percentage} sx={{ height: 8, borderRadius: 8, mb: 1 }} />

                    <Button
                      variant={isCurrentUserChoice ? 'contained' : 'outlined'}
                      size="small"
                      disabled={!selectedPoll?.is_active || voteLoadingIndex !== null || !user?.id}
                      onClick={() => handleVote(index)}
                    >
                      {isCurrentUserChoice ? 'Your Vote' : 'Vote'}
                    </Button>
                  </Box>
                )
              })}

              {!selectedPoll?.is_active && (
                <Typography variant="caption" color="text.secondary">
                  Voting is disabled because this poll is inactive.
                </Typography>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedPoll(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => !deleting && setDeleteDialog({ open: false, pollId: null, question: '' })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Delete Poll</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete:<br />
            <strong>&ldquo;{deleteDialog.question}&rdquo;</strong><br /><br />
            This action cannot be undone. All votes will be permanently deleted.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialog({ open: false, pollId: null, question: '' })}
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button color="error" variant="contained" onClick={handleDeleteConfirm} disabled={deleting}>
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Polls
