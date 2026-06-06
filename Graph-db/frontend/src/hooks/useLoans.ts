import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { loansApi } from '@api/endpoints/loans'
import { LoanIngestPayload, IngestResponse } from '@api/types'
import { handleApiSuccess, handleApiError } from '@api/client'
import { useLoanStore } from '@store/loans'

const LOANS_QUERY_KEY = ['loans']
const LOAN_DETAIL_QUERY_KEY = (id: string) => ['loan', id]

/**
 * Hook to fetch paginated loan list
 */
export const useLoansQuery = (limit = 10, offset = 0) => {
  return useQuery({
    queryKey: [...LOANS_QUERY_KEY, limit, offset],
    queryFn: () => loansApi.getLoanList(limit, offset),
    staleTime: 60000, // 1 minute
  })
}

/**
 * Hook to fetch loan detail
 */
export const useLoanDetailQuery = (loanId?: string) => {
  return useQuery({
    queryKey: LOAN_DETAIL_QUERY_KEY(loanId || ''),
    queryFn: () => loansApi.getLoanDetail(loanId!),
    enabled: !!loanId,
    staleTime: 30000, // 30 seconds
  })
}

/**
 * Hook to ingest a new loan
 */
export const useIngestLoanMutation = () => {
  const queryClient = useQueryClient()
  const { addRecentLoan } = useLoanStore()

  return useMutation({
    mutationFn: (payload: LoanIngestPayload) => loansApi.ingestLoan(payload),
    onSuccess: (response: IngestResponse) => {
      // Invalidate loans list
      queryClient.invalidateQueries({ queryKey: LOANS_QUERY_KEY })

      // Add to recent loans cache
      addRecentLoan({
        loanId: response.loanId,
        borrowerName: '',
        amount: 0,
        status: 'ingested',
        createdAt: new Date().toISOString(),
      })

      handleApiSuccess(`Loan ${response.loanId} ingested successfully`)
    },
    onError: (error: unknown) => {
      handleApiError(error, 'Failed to ingest loan')
    },
  })
}
