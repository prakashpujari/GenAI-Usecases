import { useEffect } from 'react'
import clsx from 'clsx'
import { Bot, Trash2, Moon, Sun, XCircle, Loader2 } from 'lucide-react'
import { useAgentStore } from '@/store/agentStore'
import { FileUpload } from '@/components/FileUpload'

interface Props {
  dark: boolean
  onToggleDark: () => void
}

export function Sidebar({ dark, onToggleDark }: Props) {
  const clearChat    = useAgentStore((s) => s.clearChat)
  const fetchHealth  = useAgentStore((s) => s.fetchHealth)
  const health       = useAgentStore((s) => s.health)
  const healthError  = useAgentStore((s) => s.healthError)
  const messages     = useAgentStore((s) => s.messages)

  useEffect(() => { fetchHealth() }, [fetchHealth])

  return (
    <aside className="flex w-60 shrink-0 flex-col gap-6 border-r border-zinc-200 bg-white px-4 py-5 dark:border-zinc-700 dark:bg-zinc-900">
      {/* Brand */}
      <div className="flex items-center gap-2 text-base font-bold text-brand-600 dark:text-brand-400">
        <Bot size={20} />
        RAG Agent
      </div>

      {/* Stats */}
      <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-3 dark:border-zinc-700 dark:bg-zinc-800">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Session</p>
        <p className="mt-1 text-2xl font-bold text-zinc-700 dark:text-zinc-200">
          {messages.filter((m) => m.role === 'user').length}
        </p>
        <p className="text-xs text-zinc-400">questions asked</p>
      </div>

      {/* Backend health */}
      <div className="rounded-xl border border-zinc-100 bg-zinc-50 p-3 dark:border-zinc-700 dark:bg-zinc-800">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Backend</p>
          <button
            onClick={fetchHealth}
            className="text-[10px] text-zinc-400 hover:text-brand-500"
          >
            refresh
          </button>
        </div>

        {!health && !healthError && (
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Loader2 size={12} className="animate-spin" /> checking…
          </div>
        )}

        {healthError && (
          <div className="flex items-center gap-1.5 text-xs text-red-500">
            <XCircle size={12} /> offline
          </div>
        )}

        {health && (
          <ul className="flex flex-col gap-1">
            {[
              ['API',    health.status === 'ok' ? 'ready' : health.status],
              ['FAISS',  health.vector_store],
              ['DB',     health.database],
              ['Model',  health.llm_model],
            ].map(([label, value]) => (
              <li key={label} className="flex items-center justify-between text-xs">
                <span className="text-zinc-500 dark:text-zinc-400">{label}</span>
                <span className={clsx(
                  'font-medium',
                  value === 'ready' || value === 'ok'
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-zinc-600 dark:text-zinc-300',
                )}>
                  {value}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* PDF Ingestion */}
      <FileUpload />

      {/* Spacer */}
      <div className="flex-1" />

      {/* Actions */}
      <div className="flex flex-col gap-2">
        <button
          onClick={onToggleDark}
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-600 transition hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          {dark ? <Sun size={15} /> : <Moon size={15} />}
          {dark ? 'Light mode' : 'Dark mode'}
        </button>
        <button
          onClick={clearChat}
          className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-600 transition hover:bg-red-50 hover:text-red-600 dark:text-zinc-300 dark:hover:bg-red-950/30 dark:hover:text-red-400"
        >
          <Trash2 size={15} />
          Clear chat
        </button>
      </div>
    </aside>
  )
}
