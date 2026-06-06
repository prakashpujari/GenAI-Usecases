import { AlertCircle } from 'lucide-react'
import { useAgentStore } from '@/store/agentStore'

export function ErrorBanner() {
  const error = useAgentStore((s) => s.error)

  // Clear error by re-invoking — simplest approach is to expose a setter
  // We'll just reload (error disappears on next query)
  if (!error) return null

  return (
    <div className="mx-4 mt-2 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-300">
      <AlertCircle size={13} className="mt-0.5 shrink-0" />
      <span className="flex-1">{error}</span>
    </div>
  )
}
