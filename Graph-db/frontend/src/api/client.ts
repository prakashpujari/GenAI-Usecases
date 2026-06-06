import axios, { AxiosError, AxiosInstance } from 'axios'
import { QueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number,
    public code?: string,
    public originalError?: AxiosError,
  ) {
    super(message)
    this.name = 'AppError'
  }
}

const API_BASE_URL = (import.meta.env as Record<string, string>).VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance with defaults
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use((config) => {
  // Add auth token if available (placeholder for future RBAC)
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor with retry logic
let retryCount = 0
const MAX_RETRIES = 3

axiosInstance.interceptors.response.use(
  (response) => {
    retryCount = 0
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config

    // Retry on 5xx errors (except 501 Not Implemented)
    if (
      error.response?.status &&
      error.response.status >= 500 &&
      error.response.status !== 501 &&
      retryCount < MAX_RETRIES &&
      originalRequest
    ) {
      retryCount++
      const backoffMs = Math.min(1000 * Math.pow(2, retryCount - 1), 8000)
      await new Promise((resolve) => setTimeout(resolve, backoffMs))
      return axiosInstance(originalRequest)
    }

    // Transform to AppError
    const statusCode = error.response?.status || 0
    const errorData = error.response?.data as { error?: string; code?: string } | undefined
    const message = errorData?.error || error.message || 'Unknown error'
    const code = errorData?.code || `HTTP_${statusCode}`

    const appError = new AppError(message, statusCode, code, error)

    // Log errors (in production, send to Sentry)
    console.error(`[API Error] ${code}: ${message}`, { statusCode, originalRequest: originalRequest?.url })

    return Promise.reject(appError)
  },
)

// HTTP client with typed methods
export const httpClient = {
  get: <T = unknown>(url: string, config?: any) =>
    axiosInstance.get<T>(url, config).then((res) => res.data),
  post: <T = unknown>(url: string, data?: unknown, config?: any) =>
    axiosInstance.post<T>(url, data, config).then((res) => res.data),
  put: <T = unknown>(url: string, data?: unknown, config?: any) =>
    axiosInstance.put<T>(url, data, config).then((res) => res.data),
  patch: <T = unknown>(url: string, data?: unknown, config?: any) =>
    axiosInstance.patch<T>(url, data, config).then((res) => res.data),
  delete: <T = unknown>(url: string, config?: any) =>
    axiosInstance.delete<T>(url, config).then((res) => res.data),
}

// React Query setup
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      gcTime: 5 * 60 * 1000, // 5 minutes (was cacheTime in v4)
      retry: (failureCount: number, error: unknown) => {
        if (error instanceof AppError && error.statusCode === 404) {
          return false // Don't retry 404s
        }
        return failureCount < 3
      },
    },
    mutations: {
      retry: (failureCount: number, error: unknown) => {
        if (error instanceof AppError && error.statusCode === 404) {
          return false
        }
        return failureCount < 2
      },
    },
  },
})

export const handleApiError = (error: unknown, fallbackMessage?: string) => {
  const appError = error instanceof AppError ? error : new AppError(fallbackMessage || 'An error occurred', 0)
  toast.error(appError.message)
  console.error('[API Error]', appError)
  return appError
}

export const handleApiSuccess = (message: string) => {
  toast.success(message)
}

export { API_BASE_URL }
