import { httpClient } from '../client'
import { RiskResponse, ExplainResponse } from '../types'

export const riskApi = {
  /**
   * Get risk metrics for a loan
   */
  getRisk: (loanId: string) =>
    httpClient.get<RiskResponse>(`/loans/${loanId}/risk`),

  /**
   * Get explainability details for a loan
   */
  getExplain: (loanId: string) =>
    httpClient.get<ExplainResponse>(`/loans/${loanId}/explain`),
}
