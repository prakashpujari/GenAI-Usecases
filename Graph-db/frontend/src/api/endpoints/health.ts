import { httpClient } from '../client'
import { HealthResponse, MetricsResponse } from '../types'

export const healthApi = {
  /**
   * Check API and database health status
   */
  checkHealth: () =>
    httpClient.get<HealthResponse>('/health'),

  /**
   * Get dashboard metrics
   */
  getMetrics: () =>
    httpClient.get<MetricsResponse>('/metrics'),
}
