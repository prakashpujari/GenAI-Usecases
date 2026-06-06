import { useEffect, useState } from 'react'
import clsx from 'clsx'
import { Activity, FileText, Database, GitBranch, X } from 'lucide-react'
import { useAgentStore } from '@/store/agentStore'
import { PipelineTrace } from './PipelineTrace'
import { SourceDocs }    from './SourceDocs'
import { SqlResults }    from './SqlResults'
import { RouteBadge }    from './RouteBadge'

type Tab = 'pipeline' | 'sources' | 'sql'

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'pipeline', label: 'Pipeline',  icon: <GitBranch size={13} /> },
  { id: 'sources',  label: 'Documents', icon: <FileText  size={13} /> },
  { id: 'sql',      label: 'SQL',       icon: <Database  size={13} /> },
]

export function InspectorPanel() {
  const [tab, setTab] = useState<Tab>('pipeline')
  const selectedId = useAgentStore((s) => s.selectedId)
  const messages   = useAgentStore((s) => s.messages)
  const select     = useAgentStore((s) => s.selectMessage)

  const selected = messages.find((m) => m.id === selectedId && m.response)
  const response = selected?.response

  // Reset to pipeline tab whenever a new message is selected
  useEffect(() => { setTab('pipeline') }, [selectedId])

  if (!response) {
    return (
      <aside className="hidden w-80 shrink-0 flex-col gap-4 overflow-y-auto border-l border-zinc-200 bg-zinc-50 px-4 py-5 dark:border-zinc-700 dark:bg-zinc-900 lg:flex">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-500 dark:text-zinc-400">
          <Activity size={15} />
          Inspector
        </div>
        <p className="text-center text-xs text-zinc-400 dark:text-zinc-500">
          Click an assistant message to inspect its pipeline trace.
        </p>
      </aside>
    )
  }

  return (
    <aside className="flex w-80 shrink-0 flex-col overflow-hidden border-l border-zinc-200 bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 lg:flex">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-700">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-700 dark:text-zinc-200">
          <Activity size={14} />
          Inspector
        </div>
        <div className="flex items-center gap-2">
          <RouteBadge route={response.route} />
          <button
            onClick={() => select(null)}
            className="rounded p-0.5 text-zinc-400 transition hover:bg-zinc-200 hover:text-zinc-600 dark:hover:bg-zinc-700 dark:hover:text-zinc-300"
          >
            <X size={13} />
          </button>
        </div>
      </div>

      {/* Question */}
      <div className="border-b border-zinc-200 px-4 py-2 dark:border-zinc-700">
        <p className="text-[11px] font-medium uppercase tracking-wider text-zinc-400">Question</p>
        <p className="mt-0.5 text-xs text-zinc-700 dark:text-zinc-200">{response.question}</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-zinc-200 dark:border-zinc-700">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={clsx(
              'flex flex-1 items-center justify-center gap-1.5 py-2.5 text-[11px] font-medium transition',
              tab === t.id
                ? 'border-b-2 border-brand-500 text-brand-600 dark:text-brand-400'
                : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300',
            )}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab body */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {tab === 'pipeline' && <PipelineTrace steps={response.pipeline_steps} />}
        {tab === 'sources'  && <SourceDocs   docs={response.retrieved_docs} />}
        {tab === 'sql'      && <SqlResults   results={response.sql_results} />}
      </div>
    </aside>
  )
}
