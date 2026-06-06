import { httpClient } from '../client'
import { LoanIngestPayload, IngestResponse, LoanListResponse, LoanDetail } from '../types'

export const loansApi = {
  /**
   * Ingest a new loan bundle
   */
  ingestLoan: (payload: LoanIngestPayload) =>
    httpClient.post<IngestResponse>('/loans/ingest', payload),

  /**
   * Get paginated list of loans
   */
  getLoanList: (limit = 10, offset = 0) =>
    httpClient.get<LoanListResponse>('/loans', {
      params: { limit, offset },
    }),

  /**
   * Get detailed loan information
   */
  getLoanDetail: (loanId: string) =>
    httpClient.get<LoanDetail>(`/loans/${loanId}`),
}
