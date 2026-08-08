/**
 * Community Stats Component
 * Displays community-wide statistics in a grid layout
 */
import { Grid } from '@mui/material'
import { StatCard } from '.'
import PeopleIcon from '@mui/icons-material/People'
import HomeIcon from '@mui/icons-material/Home'
import BugReportIcon from '@mui/icons-material/BugReport'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

const CommunityStats = ({ stats, loading, isSecurity }) => {
  return (
    <Grid container spacing={1.5}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={PeopleIcon}
          label="Total Residents"
          value={stats?.total_users || 0}
          color="info"
          isLoading={loading}
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={HomeIcon}
          label="Total Units"
          value={100}
          color="success"
          isLoading={loading}
        />
      </Grid>

      {!isSecurity && <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={BugReportIcon}
          label="Active Issues"
          value={(stats?.open_issues || 0) + (stats?.in_progress_issues || 0)}
          color="warning"
          isLoading={loading}
        />
      </Grid>}

      {!isSecurity && <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={CheckCircleIcon}
          label="Resolved Issues"
          value={stats?.resolved_issues || 0}
          color="success"
          isLoading={loading}
        />
      </Grid>}
    </Grid>
  )
}

export default CommunityStats
