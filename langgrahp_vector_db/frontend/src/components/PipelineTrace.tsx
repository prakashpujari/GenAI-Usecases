import { useState } from 'react'
import clsx from 'clsx'
import {
  CheckCircle2,
  XCircle,
  SkipForward,
  ChevronDown,
  ChevronRight,
  GitBranch,
  Search,
  Database,
  Brain,
} from 'lucide-react'
import type { PipelineStep, StepStatus } from '@/types'

// ---------------------------------------------------------------------------
// Node icon map
// ---------------------------------------------------------------------------
const NODE_ICONS: Record<string, React.ReactNode> = {
  router:   <GitBranch  size={14} />,
  retrieve: <Search     size={14} />,
  sql:      <Database   size={14} />,
  llm:      <Brain      size={14} />,
}

// ---------------------------------------------------------------------------
// Status icon + colour
// ---------------------------------------------------------------------------
function StatusIcon({ status }: { status: StepStatus }) {
  if (status === 'completed') return <CheckCircle2 size={14} className="text-emerald-500" />
  if (status === 'error')     return <XCircle      size={14} className="text-red-500" />
  return <SkipForward size={14} className="text-zinc-400" />
}

const stepBorder: Record<StepStatus, string> = {
  completed: 'border-emerald-200 dark:border-emerald-800',
  error:     'border-red-200    dark:border-red-800',
  skipped:   'border-zinc-200   dark:border-zinc-700',
}

const stepBg: Record<StepStatus, string> = {
  completed: 'bg-emerald-50  dark:bg-emerald-950/30',
  error:     'bg-red-50      dark:bg-red-950/30',
  skipped:   'bg-zinc-50     dark:bg-zinc-800/40',
}

// ---------------------------------------------------------------------------
// Single collapsible step card
// ---------------------------------------------------------------------------
function StepCard({ step, index }: { step: PipelineStep; index: number }) {
  const [open, setOpen] = useState(false)

  return (
    <div className={clsx('rounded-lg border text-xs', stepBorder[step.status], stepBg[step.status])}>
      {/* Header row */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left"
      >
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/60 font-mono font-bold text-zinc-500 ring-1 ring-zinc-200 dark:bg-zinc-900/60 dark:ring-zinc-700">
          {index + 1}
        </span>

        <span className="flex items-center gap-1 font-semibold capitalize text-zinc-700 dark:text-zinc-200">
          {NODE_ICONS[step.node] ?? null}
          {step.node}
        </span>

        <StatusIcon status={step.status} />

        <span className="ml-auto text-zinc-400">
          {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </span>
      </button>

      {/* Expandable output */}
      {open && (
        <pre className="overflow-x-auto whitespace-pre-wrap break-words border-t border-inherit px-3 py-2 font-mono text-[11px] leading-relaxed text-zinc-600 dark:text-zinc-300">
          {step.output}
        </pre>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Pipeline panel
// ---------------------------------------------------------------------------
interface Props {
  steps: PipelineStep[]
}

export function PipelineTrace({ steps }: Props) {
  if (steps.length === 0) {
    return (
      <p className="text-center text-xs text-zinc-400 dark:text-zinc-500">
        No pipeline data yet.
      </p>
    )
  }

  return (
    <ol className="flex flex-col gap-2">
      {steps.map((step, i) => (
        <li key={i}>
          <StepCard step={step} index={i} />
        </li>
      ))}
    </ol>
  )
}
