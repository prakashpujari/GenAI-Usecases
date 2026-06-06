import React from 'react'
import { Grid, Box, Paper, Typography, CircularProgress, Alert } from '@mui/material'
import { CheckCircle, Error as ErrorIcon, Warning as WarningIcon } from '@mui/icons-material'
import { useHealthQuery, useMetricsQuery } from '@hooks/useHealth'

const Dashboard: React.FC = () => {
  const { data: health, isLoading: healthLoading, error: healthError } = useHealthQuery()
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useMetricsQuery()

  const getHealthColor = () => {
    if (!health) return 'default'
    return health.status === 'ok' ? 'success' : health.status === 'degraded' ? 'warning' : 'error'
  }

  const getHealthIcon = () => {
    if (!health) return null
    if (health.status === 'ok') return <CheckCircle sx={{ color: 'success.main' }} />
    if (health.status === 'degraded') return <WarningIcon sx={{ color: 'warning.main' }} />
    return <ErrorIcon sx={{ color: 'error.main' }} />
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Dashboard
      </Typography>

      {/* Health Status Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            {healthLoading ? (
              <CircularProgress size={40} />
            ) : healthError ? (
              <ErrorIcon sx={{ fontSize: 40, color: 'error.main' }} />
            ) : (
              getHealthIcon()
            )}
            <Box>
              <Typography variant="caption" color="textSecondary">
                API Health
              </Typography>
              <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                {healthLoading ? 'Checking...' : health?.status || 'Unknown'}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Total Loans */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="caption" color="textSecondary">
              Total Loans
            </Typography>
            <Typography variant="h5">
              {metricsLoading ? <CircularProgress size={24} /> : metrics?.totalLoans || 0}
            </Typography>
          </Paper>
        </Grid>

        {/* Average Risk Score */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="caption" color="textSecondary">
              Avg Risk Score
            </Typography>
            <Typography variant="h5">
              {metricsLoading
                ? <CircularProgress size={24} />
                : (metrics?.avgRiskScore?.toFixed(1) || 'N/A')}
            </Typography>
          </Paper>
        </Grid>

        {/* Last GDS Job */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="caption" color="textSecondary">
              Last GDS Job
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              {metricsLoading ? (
                <CircularProgress size={20} />
              ) : metrics?.lastGdsJobStatus ? (
                <span style={{ textTransform: 'capitalize' }}>{metrics.lastGdsJobStatus}</span>
              ) : (
                'Never run'
              )}
            </Typography>
            {metrics?.lastGdsJobTime && (
              <Typography variant="caption" color="textSecondary">
                {new Date(metrics.lastGdsJobTime).toLocaleString()}
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Quick Start
        </Typography>
        <Alert severity="info">
          Welcome to the Mortgage Graph Platform! Use the navigation menu to explore loan ingestion, risk analysis, graph
          data, and job monitoring.
        </Alert>
      </Paper>
    </Box>
  )
}

export default Dashboard
