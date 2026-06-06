import { FileText } from 'lucide-react'

interface Props {
  docs: string[]
}

export function SourceDocs({ docs }: Props) {
  if (docs.length === 0) {
    return (
      <p className="text-center text-xs text-zinc-400 dark:text-zinc-500">
        No documents retrieved.
      </p>
    )
  }

  return (
    <ul className="flex flex-col gap-2">
      {docs.map((doc, i) => (
        <li
          key={i}
          className="flex items-start gap-2 rounded-lg border border-blue-100 bg-blue-50 px-3 py-2 text-xs text-blue-800 dark:border-blue-900/40 dark:bg-blue-950/30 dark:text-blue-300"
        >
          <FileText size={13} className="mt-0.5 shrink-0 text-blue-400" />
          <span className="leading-relaxed">{doc}</span>
        </li>
      ))}
    </ul>
  )
}
