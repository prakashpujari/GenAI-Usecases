import React, { useState } from 'react'
import { Box, Paper, Typography, Button, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert } from '@mui/material'
import { PlayArrow as PlayIcon, Refresh as RefreshIcon } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi, GdsJobType } from '@api/endpoints/jobs'
import { handleApiSuccess, handleApiError } from '@api/client'

const JobsMonitor: React.FC = () => {
  const queryClient = useQueryClient()
  const [selectedJob, setSelectedJob] = useState<string | null>(null)
  const [jobLogDialog, setJobLogDialog] = useState(false)

  const { data: jobs, isLoading, refetch } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.listJobs(),
    refetchInterval: 10000, // Poll every 10s
  })

  const { mutate: runGdsJob, isPending: jobPending } = useMutation({
    mutationFn: (jobType: GdsJobType) => jobsApi.runGdsJob(jobType),
    onSuccess: (response) => {
      handleApiSuccess(`Job ${response.jobId} started`)
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
    onError: (error: unknown) => {
      handleApiError(error, 'Failed to start job')
    },
  })

  const jobTypeButtons: Array<{ label: string; type: GdsJobType }> = [
    { label: 'Project Fraud', type: 'project-fraud' },
    { label: 'Project Risk', type: 'project-risk' },
    { label: 'Community Detection', type: 'community-detection' },
    { label: 'Centrality Analysis', type: 'centrality' },
    { label: 'Similarity Scoring', type: 'similarity' },
    { label: 'Run All', type: 'run-all' },
  ]

  const getStatusColor = (status: string): 'default' | 'primary' | 'success' | 'error' | 'warning' => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      case 'running':
        return 'primary'
      default:
        return 'default'
    }
  }

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start).getTime()
    const endTime = end ? new Date(end).getTime() : Date.now()
    const seconds = Math.floor((endTime - startTime) / 1000)
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
    return `${Math.floor(seconds / 3600)}h`
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Jobs Monitor
      </Typography>

      {/* Job Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Trigger GDS Jobs
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {jobTypeButtons.map((btn) => (
            <Button
              key={btn.type}
              variant="outlined"
              size="small"
              startIcon={jobPending ? <CircularProgress size={16} /> : <PlayIcon />}
              onClick={() => runGdsJob(btn.type)}
              disabled={jobPending}
            >
              {btn.label}
            </Button>
          ))}
          <Button
            variant="text"
            size="small"
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
            disabled={isLoading}
          >
            Refresh
          </Button>
        </Box>
      </Paper>

      {/* Job List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Active & Recent Jobs
        </Typography>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
            <CircularProgress />
          </Box>
        ) : !jobs?.jobs || jobs.jobs.length === 0 ? (
          <Alert severity="info">No jobs found. Trigger a job to get started.</Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell>Job ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="center">Progress</TableCell>
                  <TableCell>Start Time</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {jobs.jobs.map((job) => (
                  <TableRow key={job.jobId} hover>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>{job.jobId}</TableCell>
                    <TableCell sx={{ textTransform: 'capitalize' }}>{job.type}</TableCell>
                    <TableCell>
                      <Chip label={job.status} color={getStatusColor(job.status)} size="small" />
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
                        <CircularProgress variant="determinate" value={job.progress} size={30} thickness={4} />
                        <Typography variant="caption" sx={{ minWidth: '30px' }}>
                          {job.progress}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.875rem' }}>
                      {new Date(job.startTime).toLocaleString()}
                    </TableCell>
                    <TableCell>{formatDuration(job.startTime, job.endTime)}</TableCell>
                    <TableCell align="center">
                      <Button
                        size="small"
                        variant="text"
                        onClick={() => {
                          setSelectedJob(job.jobId)
                          setJobLogDialog(true)
                        }}
                      >
                        View Log
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Job Log Dialog */}
      <Dialog open={jobLogDialog} onClose={() => setJobLogDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Job Log</DialogTitle>
        <DialogContent>
          {selectedJob && jobs?.jobs ? (
            (() => {
              const job = jobs.jobs.find((j) => j.jobId === selectedJob)
              return job ? (
                <Box
                  sx={{
                    backgroundColor: '#f5f5f5',
                    p: 2,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    maxHeight: '300px',
                    overflowY: 'auto',
                  }}
                >
                  <pre>{job.log || 'No log output available'}</pre>
                </Box>
              ) : (
                <Typography>Job not found</Typography>
              )
            })()
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setJobLogDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default JobsMonitor
