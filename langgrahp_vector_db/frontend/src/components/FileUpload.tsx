import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import clsx from 'clsx'
import { UploadCloud, FileText, CheckCircle2, XCircle, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { useAgentStore } from '@/store/agentStore'

export function FileUpload() {
  const ingestPdfs   = useAgentStore((s) => s.ingestPdfs)
  const isIngesting  = useAgentStore((s) => s.isIngesting)
  const ingestResult = useAgentStore((s) => s.ingestResult)
  const ingestError  = useAgentStore((s) => s.ingestError)

  const [dragging, setDragging]   = useState(false)
  const [expanded, setExpanded]   = useState(false)
  const [queued, setQueued]       = useState<File[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  // -------------------------------------------------------------------------
  function pickFiles(files: FileList | null) {
    if (!files) return
    const pdfs = Array.from(files).filter((f) => f.type === 'application/pdf')
    if (pdfs.length) setQueued(pdfs)
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragging(false)
    pickFiles(e.dataTransfer.files)
  }

  function onInputChange(e: ChangeEvent<HTMLInputElement>) {
    pickFiles(e.target.files)
    e.target.value = ''          // allow re-selecting the same file
  }

  async function handleUpload() {
    if (!queued.length) return
    await ingestPdfs(queued)
    setQueued([])
  }

  // -------------------------------------------------------------------------
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-zinc-100 bg-zinc-50 p-3 dark:border-zinc-700 dark:bg-zinc-800">

      {/* Header row */}
      <button
        className="flex w-full items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
        onClick={() => setExpanded((v) => !v)}
      >
        <span className="flex items-center gap-1.5">
          <UploadCloud size={12} />
          Ingest PDFs
        </span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {expanded && (
        <>
          {/* Drop zone */}
          <div
            role="button"
            tabIndex={0}
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
            className={clsx(
              'flex cursor-pointer flex-col items-center justify-center gap-1 rounded-lg border-2 border-dashed px-3 py-4 text-center transition',
              dragging
                ? 'border-brand-500 bg-brand-50 dark:bg-brand-950/30'
                : 'border-zinc-300 hover:border-brand-400 dark:border-zinc-600 dark:hover:border-brand-500',
            )}
          >
            <UploadCloud size={20} className="text-zinc-400 dark:text-zinc-500" />
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Drop PDFs here or <span className="text-brand-600 dark:text-brand-400">browse</span>
            </p>
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf"
              multiple
              className="hidden"
              onChange={onInputChange}
            />
          </div>

          {/* Queued file list */}
          {queued.length > 0 && (
            <ul className="flex flex-col gap-1">
              {queued.map((f) => (
                <li key={f.name} className="flex items-center gap-1.5 text-xs text-zinc-600 dark:text-zinc-300">
                  <FileText size={11} className="shrink-0 text-zinc-400" />
                  <span className="truncate">{f.name}</span>
                  <span className="ml-auto shrink-0 text-zinc-400">
                    {(f.size / 1024 / 1024).toFixed(1)} MB
                  </span>
                </li>
              ))}
            </ul>
          )}

          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={!queued.length || isIngesting}
            className={clsx(
              'flex items-center justify-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition',
              queued.length && !isIngesting
                ? 'bg-brand-600 text-white hover:bg-brand-700'
                : 'cursor-not-allowed bg-zinc-200 text-zinc-400 dark:bg-zinc-700 dark:text-zinc-500',
            )}
          >
            {isIngesting ? (
              <><Loader2 size={12} className="animate-spin" /> Ingesting…</>
            ) : (
              <><UploadCloud size={12} /> Ingest {queued.length > 0 ? `${queued.length} file${queued.length > 1 ? 's' : ''}` : ''}</>
            )}
          </button>

          {/* Result summary */}
          {ingestResult && !isIngesting && (
            <div className="rounded-lg bg-emerald-50 p-2 dark:bg-emerald-950/30">
              <p className="flex items-center gap-1 text-xs font-medium text-emerald-700 dark:text-emerald-400">
                <CheckCircle2 size={11} /> {ingestResult.message}
              </p>
              <ul className="mt-1 flex flex-col gap-0.5">
                {ingestResult.documents.map((d) => (
                  <li key={d.filename} className="text-[11px] text-emerald-600 dark:text-emerald-500">
                    {d.filename} — {d.skipped ? 'skipped' : `${d.chunks} chunks`}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Error */}
          {ingestError && !isIngesting && (
            <div className="flex items-start gap-1.5 rounded-lg bg-red-50 p-2 text-xs text-red-600 dark:bg-red-950/30 dark:text-red-400">
              <XCircle size={11} className="mt-0.5 shrink-0" />
              {ingestError}
            </div>
          )}
        </>
      )}
    </div>
  )
}
