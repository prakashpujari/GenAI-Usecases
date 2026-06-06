import axios from 'axios'
import type { HealthResponse, IngestResponse, QueryRequest, QueryResponse } from '@/types'

// All requests go through Vite's proxy → http://localhost:8000
const http = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60_000,
})

// ---------------------------------------------------------------------------
// Response interceptor – normalise error messages
// ---------------------------------------------------------------------------
http.interceptors.response.use(
  (res) => res,
  (err) => {
    const message: string =
      err?.response?.data?.detail ?? err?.message ?? 'Unknown error'
    return Promise.reject(new Error(message))
  },
)

// ---------------------------------------------------------------------------
// API methods
// ---------------------------------------------------------------------------

export async function postQuery(body: QueryRequest): Promise<QueryResponse> {
  const { data } = await http.post<QueryResponse>('/query', body)
  return data
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await http.get<HealthResponse>('/health')
  return data
}

export async function uploadPdfs(
  files: File[],
  replace = false,
): Promise<IngestResponse> {
  const form = new FormData()
  files.forEach((f) => form.append('files', f))

  const { data } = await axios.post<IngestResponse>(
    `/api/ingest?replace=${replace}`,
    form,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120_000,
    },
  )
  return data
}
