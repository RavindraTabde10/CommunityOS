import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box, Container, Typography, Grid, Card, CardContent, CardActions,
  Button, Chip, CircularProgress, Alert, TextField, InputAdornment,
  Select, MenuItem, FormControl, InputLabel, Divider, Tooltip,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import PeopleIcon from '@mui/icons-material/People'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import EventSeatIcon from '@mui/icons-material/EventSeat'
import assetService from '../../api/assetService'
import { ASSET_TYPES, ASSET_TYPE_OPTIONS } from '../../constants/assets'

const AssetList = () => {
  const navigate = useNavigate()
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [availableOnly, setAvailableOnly] = useState(false)

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await assetService.getAssets({ is_active: true, limit: 100 })
      setAssets(res.data || [])
    } catch {
      setError('Failed to load assets. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const filtered = useMemo(() => {
    return assets.filter((a) => {
      if (typeFilter !== 'all' && a.asset_type !== typeFilter) return false
      if (availableOnly && !a.is_bookable) return false
      if (search && !a.name.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [assets, typeFilter, availableOnly, search])

  const fmtTime = (t) => {
    if (!t) return null
    const [h, m] = t.split(':')
    const date = new Date()
    date.setHours(+h, +m)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" fontWeight={700} gutterBottom>
          Facilities & Assets
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Browse and book community facilities
        </Typography>
      </Box>

      {/* Filters */}
      <Box
        display="flex"
        flexWrap="wrap"
        gap={2}
        mb={3}
        alignItems="center"
      >
        <TextField
          size="small"
          placeholder="Search facilities..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 220 }}
        />

        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Type</InputLabel>
          <Select
            value={typeFilter}
            label="Type"
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <MenuItem value="all">All Types</MenuItem>
            {ASSET_TYPE_OPTIONS.map((o) => (
              <MenuItem key={o.value} value={o.value}>
                {ASSET_TYPES[o.value]?.icon} {o.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Chip
          label="Bookable only"
          onClick={() => setAvailableOnly((v) => !v)}
          color={availableOnly ? 'primary' : 'default'}
          variant={availableOnly ? 'filled' : 'outlined'}
          clickable
        />

        <Typography variant="body2" color="text.secondary" ml="auto">
          {filtered.length} of {assets.length} facilities
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Asset Grid */}
      {filtered.length === 0 ? (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="text.secondary">
            No facilities found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your filters
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filtered.map((asset) => {
            const typeInfo = ASSET_TYPES[asset.asset_type] || ASSET_TYPES.other
            return (
              <Grid item xs={12} sm={6} md={4} key={asset.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    cursor: 'pointer',
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'box-shadow 0.2s',
                    '&:hover': { boxShadow: 4 },
                  }}
                  onClick={() => navigate(`/assets/${asset.id}`)}
                >
                  {/* Colour banner */}
                  <Box
                    sx={{
                      height: 8,
                      bgcolor: typeInfo.color,
                      borderRadius: '4px 4px 0 0',
                    }}
                  />

                  <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                    {/* Type chip + name */}
                    <Box display="flex" alignItems="flex-start" gap={1} mb={1}>
                      <Typography fontSize={28} lineHeight={1}>
                        {typeInfo.icon}
                      </Typography>
                      <Box>
                        <Typography variant="h6" fontWeight={600} lineHeight={1.2}>
                          {asset.name}
                        </Typography>
                        <Chip
                          label={typeInfo.label}
                          size="small"
                          sx={{
                            mt: 0.5,
                            bgcolor: typeInfo.color + '22',
                            color: typeInfo.color,
                            fontWeight: 600,
                            fontSize: 11,
                          }}
                        />
                      </Box>
                    </Box>

                    {asset.description && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mt: 1,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {asset.description}
                      </Typography>
                    )}

                    <Divider sx={{ my: 1.5 }} />

                    {/* Meta row */}
                    <Box display="flex" flexWrap="wrap" gap={1.5}>
                      {asset.location && (
                        <Tooltip title="Location">
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <LocationOnIcon fontSize="small" color="action" />
                            <Typography variant="caption">{asset.location}</Typography>
                          </Box>
                        </Tooltip>
                      )}
                      {asset.capacity && (
                        <Tooltip title="Capacity">
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <PeopleIcon fontSize="small" color="action" />
                            <Typography variant="caption">{asset.capacity} people</Typography>
                          </Box>
                        </Tooltip>
                      )}
                      {(asset.operating_hours_start && asset.operating_hours_end) && (
                        <Tooltip title="Operating hours">
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <AccessTimeIcon fontSize="small" color="action" />
                            <Typography variant="caption">
                              {fmtTime(asset.operating_hours_start)} – {fmtTime(asset.operating_hours_end)}
                            </Typography>
                          </Box>
                        </Tooltip>
                      )}
                      {Number(asset.hourly_rate) > 0 && (
                        <Tooltip title="Hourly rate">
                          <Box display="flex" alignItems="center" gap={0.5}>
                            <AttachMoneyIcon fontSize="small" color="action" />
                            <Typography variant="caption">₹{asset.hourly_rate}/hr</Typography>
                          </Box>
                        </Tooltip>
                      )}
                    </Box>
                  </CardContent>

                  <CardActions sx={{ px: 2, pb: 2 }}>
                    {asset.is_bookable ? (
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<EventSeatIcon />}
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/assets/${asset.id}`)
                        }}
                        fullWidth
                        sx={{ bgcolor: typeInfo.color, '&:hover': { bgcolor: typeInfo.color + 'dd' } }}
                      >
                        Book Now
                      </Button>
                    ) : (
                      <Button size="small" variant="outlined" disabled fullWidth>
                        Not Bookable
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            )
          })}
        </Grid>
      )}
    </Container>
  )
}

export default AssetList
