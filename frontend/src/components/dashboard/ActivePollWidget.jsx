import { useState, useEffect, useCallback } from 'react'
import { Box, Paper, Typography, Chip, LinearProgress, Skeleton, Button, CircularProgress } from '@mui/material'
import PollIcon from '@mui/icons-material/Poll'
import HowToVoteIcon from '@mui/icons-material/HowToVote'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { toast } from 'react-toastify'
import { pollsAPI } from '../../api/polls'

const ActivePollWidget = () => {
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)
  const [poll, setPoll] = useState(null)
  const [loading, setLoading] = useState(true)
  const [votingIndex, setVotingIndex] = useState(null)

  const fetchActivePoll = useCallback(async () => {
    try {
      const response = await pollsAPI.getAll({ is_active: true, limit: 1 })
      const polls = response.data?.polls || []
      setPoll(polls[0] || null)
    } catch {
      // silently skip — dashboard should never crash due to poll fetch failure
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchActivePoll()
  }, [fetchActivePoll])

  const getUserVoteIndex = () => {
    if (!poll || !user?.id) return -1
    return (poll.votes || []).find((v) => String(v.user_id) === String(user.id))?.option_index ?? -1
  }

  const handleVote = async (optionIndex) => {
    if (!poll || votingIndex !== null) return
    try {
      setVotingIndex(optionIndex)
      const response = await pollsAPI.vote(poll.id, { option_index: optionIndex })
      setPoll(response.data)
      toast.success('Vote recorded!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to cast vote')
    } finally {
      setVotingIndex(null)
    }
  }

  if (loading) {
    return (
      <Paper
        elevation={3}
        sx={{
          p: 1.5,
          background: 'rgba(255,255,255,0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.5)',
        }}
      >
        <Skeleton variant="text" width="50%" height={24} />
        <Skeleton variant="text" width="80%" height={20} sx={{ mt: 0.5 }} />
        <Skeleton variant="rectangular" height={36} sx={{ borderRadius: 1, mt: 1 }} />
        <Skeleton variant="rectangular" height={36} sx={{ borderRadius: 1, mt: 0.75 }} />
      </Paper>
    )
  }

  if (!poll) return null

  const totalVotes = poll.total_votes ?? 0
  const userVoteIndex = getUserVoteIndex()
  const hasVoted = userVoteIndex !== -1

  return (
    <Paper
      elevation={3}
      sx={{
        p: 1.5,
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.5)',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <PollIcon fontSize="small" color="primary" />
          <Typography variant="body1" fontWeight="bold">
            Active Poll
          </Typography>
          {hasVoted && (
            <Chip
              icon={<CheckCircleIcon sx={{ fontSize: '0.8rem !important' }} />}
              label="Voted"
              size="small"
              color="success"
              sx={{ height: 18, fontSize: '0.65rem' }}
            />
          )}
        </Box>
        <Chip
          label="View All Polls"
          clickable
          onClick={() => navigate('/polls')}
          color="primary"
          variant="outlined"
          size="small"
          sx={{ height: 20, fontSize: '0.7rem' }}
        />
      </Box>

      {/* Question */}
      <Typography variant="body2" fontWeight={600} sx={{ mb: 1, lineHeight: 1.4 }}>
        {poll.question}
      </Typography>

      {/* Options */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
        {(poll.options || []).map((option, index) => {
          const optionVotes = poll.option_vote_counts?.[index] ?? 0
          const pct = totalVotes > 0 ? Math.round((optionVotes / totalVotes) * 100) : 0
          const isUserChoice = userVoteIndex === index
          const isVotingThis = votingIndex === index

          return (
            <Box
              key={index}
              onClick={() => handleVote(index)}
              sx={{
                position: 'relative',
                border: '1px solid',
                borderColor: isUserChoice ? 'primary.main' : 'divider',
                borderRadius: 1,
                overflow: 'hidden',
                cursor: poll.is_active ? 'pointer' : 'default',
                bgcolor: isUserChoice ? 'primary.50' : 'background.paper',
                transition: 'border-color 0.15s, box-shadow 0.15s',
                '&:hover': poll.is_active
                  ? { borderColor: 'primary.main', boxShadow: '0 0 0 2px rgba(25,118,210,0.15)' }
                  : {},
              }}
            >
              {/* Vote % progress bar */}
              <LinearProgress
                variant="determinate"
                value={hasVoted ? pct : 0}
                sx={{
                  position: 'absolute',
                  top: 0, left: 0, right: 0, bottom: 0,
                  height: '100%',
                  borderRadius: 0,
                  bgcolor: 'transparent',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: isUserChoice ? 'primary.light' : 'grey.200',
                    opacity: 0.4,
                    transition: 'transform 0.4s ease',
                  },
                }}
              />

              {/* Content row */}
              <Box
                sx={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  px: 1,
                  py: 0.6,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {isVotingThis ? (
                    <CircularProgress size={12} />
                  ) : isUserChoice ? (
                    <CheckCircleIcon sx={{ fontSize: '0.85rem', color: 'primary.main' }} />
                  ) : (
                    <HowToVoteIcon sx={{ fontSize: '0.85rem', color: 'text.disabled' }} />
                  )}
                  <Typography
                    variant="body2"
                    sx={{
                      fontSize: '0.78rem',
                      fontWeight: isUserChoice ? 600 : 400,
                      color: isUserChoice ? 'primary.dark' : 'text.primary',
                    }}
                  >
                    {option}
                  </Typography>
                </Box>
                {hasVoted && (
                  <Typography variant="body2" sx={{ fontSize: '0.72rem', color: 'text.secondary', ml: 1, whiteSpace: 'nowrap' }}>
                    {pct}% ({optionVotes})
                  </Typography>
                )}
              </Box>
            </Box>
          )
        })}
      </Box>

      {/* Footer */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.75 }}>
        <Typography variant="caption" color="text.secondary">
          {totalVotes} {totalVotes === 1 ? 'vote' : 'votes'} total
        </Typography>
        {!hasVoted && (
          <Typography variant="caption" color="primary.main" fontWeight={500}>
            Click an option to vote
          </Typography>
        )}
      </Box>
    </Paper>
  )
}

export default ActivePollWidget
