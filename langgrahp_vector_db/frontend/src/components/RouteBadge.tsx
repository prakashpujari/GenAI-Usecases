import type { RouteType } from '@/types'
import clsx from 'clsx'

const labels: Record<RouteType, string> = {
  rag:     'RAG',
  sql:     'SQL',
  both:    'RAG + SQL',
  unknown: '—',
}

const colours: Record<RouteType, string> = {
  rag:     'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  sql:     'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
  both:    'bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300',
  unknown: 'bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400',
}

interface Props {
  route: RouteType
}

export function RouteBadge({ route }: Props) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
        colours[route],
      )}
    >
      {labels[route]}
    </span>
  )
}
