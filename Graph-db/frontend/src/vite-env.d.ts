/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_ENABLE_GRAPH_EXPLORER: string
  readonly VITE_ENABLE_JOB_MONITOR: string
  readonly VITE_ENABLE_RBAC: string
  readonly VITE_SENTRY_DSN?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
