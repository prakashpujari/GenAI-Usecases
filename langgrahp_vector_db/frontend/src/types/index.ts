// ---------------------------------------------------------------------------
// Shared TypeScript types – mirrors the FastAPI Pydantic schemas exactly
// ---------------------------------------------------------------------------

export type RouteType = 'rag' | 'sql' | 'both' | 'unknown'

export type StepStatus = 'completed' | 'error' | 'skipped'

export interface PipelineStep {
  node:   string
  status: StepStatus
  output: string
}

export interface QueryRequest {
  question: string
}

export interface QueryResponse {
  question:       string
  route:          RouteType
  retrieved_docs: string[]
  sql_results:    string | null
  final_answer:   string
  pipeline_steps: PipelineStep[]
}

export interface HealthResponse {
  status:       string
  vector_store: string
  database:     string
  llm_model:    string
}

// ---------------------------------------------------------------------------
// PDF ingestion types
// ---------------------------------------------------------------------------

export interface DocumentInfo {
  filename: string
  pages:    number
  chunks:   number
  skipped:  boolean
  message:  string
}

export interface IngestResponse {
  message:      string
  documents:    DocumentInfo[]
  total_chunks: number
}

// ---------------------------------------------------------------------------
// UI-only types
// ---------------------------------------------------------------------------

export type MessageRole = 'user' | 'assistant'

export interface ChatMessage {
  id:        string
  role:      MessageRole
  content:   string
  timestamp: Date
  response?: QueryResponse   // attached only to assistant messages
}
