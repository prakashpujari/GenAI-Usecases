import { useQuery } from '@tanstack/react-query'
import { riskApi } from '@api/endpoints/risk'

const RISK_QUERY_KEY = (id: string) => ['risk', id]
const EXPLAIN_QUERY_KEY = (id: string) => ['explain', id]

/**
 * Hook to fetch risk metrics for a loan
 */
export const useRiskQuery = (loanId?: string) => {
  return useQuery({
    queryKey: RISK_QUERY_KEY(loanId || ''),
    queryFn: () => riskApi.getRisk(loanId!),
    enabled: !!loanId,
    staleTime: 30000, // 30 seconds
  })
}

/**
 * Hook to fetch explainability details for a loan
 */
export const useExplainQuery = (loanId?: string) => {
  return useQuery({
    queryKey: EXPLAIN_QUERY_KEY(loanId || ''),
    queryFn: () => riskApi.getExplain(loanId!),
    enabled: !!loanId,
    staleTime: 30000, // 30 seconds
  })
}
