import { httpClient } from '../client'
import { JobListResponse, JobResponse, Job } from '../types'

export type GdsJobType =
  | 'project-fraud'
  | 'project-risk'
  | 'community-detection'
  | 'centrality'
  | 'similarity'
  | 'run-all'

export const jobsApi = {
  /**
   * Get list of recent GDS/ETL jobs
   */
  listJobs: () =>
    httpClient.get<JobListResponse>('/jobs'),

  /**
   * Get status of a specific job
   */
  getJobStatus: (jobId: string) =>
    httpClient.get<Job>(`/jobs/${jobId}`),

  /**
   * Trigger a GDS job
   */
  runGdsJob: (jobType: GdsJobType) =>
    httpClient.post<JobResponse>(`/jobs/gds/${jobType}`),

  /**
   * Watch job progress via WebSocket (optional - fallback to polling)
   */
  watchJobProgress: (jobId: string): WebSocket | null => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      return new WebSocket(`${protocol}//${window.location.host}/ws/jobs/${jobId}`)
    } catch {
      console.warn('WebSocket not available, will use polling instead')
      return null
    }
  },
}
