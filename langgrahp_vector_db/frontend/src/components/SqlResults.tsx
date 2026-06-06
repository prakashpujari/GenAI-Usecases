import { Database } from 'lucide-react'

interface Props {
  results: string | null
}

export function SqlResults({ results }: Props) {
  if (!results) {
    return (
      <p className="text-center text-xs text-zinc-400 dark:text-zinc-500">
        No SQL results.
      </p>
    )
  }

  return (
    <div className="flex items-start gap-2 rounded-lg border border-emerald-100 bg-emerald-50 px-3 py-2 dark:border-emerald-900/40 dark:bg-emerald-950/30">
      <Database size={13} className="mt-0.5 shrink-0 text-emerald-500" />
      <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-emerald-800 dark:text-emerald-300">
        {results}
      </pre>
    </div>
  )
}
