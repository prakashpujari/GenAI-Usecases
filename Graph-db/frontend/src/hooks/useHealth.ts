import { useQuery } from '@tanstack/react-query'
import { healthApi } from '@api/endpoints/health'

const HEALTH_QUERY_KEY = ['health']
const METRICS_QUERY_KEY = ['metrics']

/**
 * Hook to check API health status (with polling)
 */
export const useHealthQuery = (refetchInterval = 30000) => {
  return useQuery({
    queryKey: HEALTH_QUERY_KEY,
    queryFn: () => healthApi.checkHealth(),
    staleTime: 10000, // 10 seconds
    refetchInterval,
  })
}

/**
 * Hook to fetch dashboard metrics
 */
export const useMetricsQuery = (refetchInterval = 60000) => {
  return useQuery({
    queryKey: METRICS_QUERY_KEY,
    queryFn: () => healthApi.getMetrics(),
    staleTime: 30000, // 30 seconds
    refetchInterval,
  })
}
