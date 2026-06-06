export interface BorrowerIn {
  borrowerId: string
  name: string
  ssnHash?: string | null
  dob?: string | null
}

export interface LoanIn {
  loanId: string
  amount: number
  status: string
  purpose: string
  originationDate?: string | null
  ltv?: number
  dti?: number
}

export interface PropertyIn {
  propertyId: string
  address: string
  city: string
  state: string
  zip: string
  type: string
}

export interface IncomeSourceIn {
  incomeId: string
  type: string
  employerName: string
  annualIncome: number
  startDate?: string | null
}

export interface DocumentIn {
  documentId: string
  type: string
  sourceSystem: string
  uploadedAt?: string | null
}

export interface LoanIngestPayload {
  borrower: BorrowerIn
  loan: LoanIn
  property: PropertyIn
  income: IncomeSourceIn
  documents: DocumentIn[]
}

export interface IngestResponse {
  loanId: string
  violations: string[]
  status: 'ingested' | 'pending'
}

// New types for UI endpoints
export interface LoanSummary {
  loanId: string
  borrowerName: string
  amount: number
  status: string
  riskScore?: number | null
  createdAt: string
}

export interface LoanDetail {
  loan: LoanIn
  borrower: BorrowerIn
  property: PropertyIn
  income: IncomeSourceIn
  documents: DocumentIn[]
  riskScore?: number | null
  networkRiskScore?: number | null
}

export interface LoanListResponse {
  items: LoanSummary[]
  total: number
}

export interface RiskResponse {
  loanId: string
  ltv: number
  dti: number
  riskScore: number
  networkRiskScore: number
  fraudCommunity?: number | null
  riskCentrality?: number | null
  sharedContacts?: number
  similarityFlags?: string[]
  violations: string[]
}

export interface Rule {
  ruleId: string
  name: string
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  violationReason?: string
}

export interface Regulation {
  jurisdictionCode: string
  regulationName: string
  regulationId: string
}

export interface GraphSignal {
  signalName: string
  value: number
  contribution: number // 0-1, how much it contributes to risk
}

export interface ExplainResponse {
  loanId: string
  rules: Rule[]
  regulations: Regulation[]
  graphSignals: GraphSignal[]
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'unavailable'
  database?: string
}

export interface MetricsResponse {
  totalLoans: number
  totalBorrowers: number
  avgRiskScore?: number | null
  networkDensity?: number | null
  lastGdsJobTime?: string | null
  lastGdsJobStatus?: string | null
}

export interface Job {
  jobId: string
  type: 'gds' | 'etl'
  status: 'pending' | 'running' | 'completed' | 'failed'
  startTime: string
  endTime?: string | null
  progress: number // 0-100
  log?: string
}

export interface JobListResponse {
  jobs: Job[]
}

export interface JobResponse {
  jobId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
}

export interface GraphQueryRequest {
  cypher: string
  params?: Record<string, unknown>
}

export interface GraphQueryResponse {
  columns: string[]
  rows: Array<Record<string, unknown>>
}

export interface GraphNode {
  id: string
  labels: string[]
  properties: Record<string, unknown>
}

export interface GraphRelationship {
  id: string
  type: string
  startNodeId: string
  endNodeId: string
  properties: Record<string, unknown>
}

export interface NodeDetailsResponse {
  id: string
  labels: string[]
  properties: Record<string, unknown>
  relationships: GraphRelationship[]
}

export interface ErrorResponse {
  error: string
  code: string
  details?: Record<string, unknown>
}
