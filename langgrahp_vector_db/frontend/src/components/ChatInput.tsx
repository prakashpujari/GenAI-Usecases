import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { SendHorizonal, Loader2 } from 'lucide-react'
import clsx from 'clsx'
import { useAgentStore } from '@/store/agentStore'

// Preset example questions surfaced as quick-action chips
const SUGGESTIONS = [
  'Who is the engineer and what documents mention engineering?',
  'List all employees and their roles.',
  'What do cloud engineers do?',
  'Which engineers work with data?',
]

export function ChatInput() {
  const [text, setText] = useState('')
  const isLoading  = useAgentStore((s) => s.isLoading)
  const sendQuestion = useAgentStore((s) => s.sendQuestion)

  const canSend = text.trim().length > 0 && !isLoading

  function submit() {
    if (!canSend) return
    const q = text.trim()
    setText('')
    sendQuestion(q)
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function onFormSubmit(e: FormEvent) {
    e.preventDefault()
    submit()
  }

  return (
    <div className="border-t border-zinc-200 bg-white px-4 pb-4 pt-3 dark:border-zinc-700 dark:bg-zinc-900">
      {/* Suggestion chips */}
      <div className="mb-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            disabled={isLoading}
            onClick={() => sendQuestion(s)}
            className="rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1 text-[11px] text-zinc-600 transition hover:border-brand-400 hover:bg-brand-50 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:border-brand-500 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
          >
            {s.length > 48 ? s.slice(0, 46) + '…' : s}
          </button>
        ))}
      </div>

      {/* Input row */}
      <form onSubmit={onFormSubmit} className="flex items-end gap-2">
        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask a question… (Enter to send, Shift+Enter for newline)"
          disabled={isLoading}
          className={clsx(
            'flex-1 resize-none rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-800',
            'placeholder:text-zinc-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200',
            'disabled:cursor-not-allowed disabled:opacity-60',
            'dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder:text-zinc-500',
            'dark:focus:border-brand-500 dark:focus:ring-brand-900/40',
            'max-h-40 overflow-y-auto',
          )}
        />
        <button
          type="submit"
          disabled={!canSend}
          className={clsx(
            'flex h-11 w-11 items-center justify-center rounded-xl transition',
            canSend
              ? 'bg-brand-500 text-white shadow-sm hover:bg-brand-600 active:scale-95'
              : 'cursor-not-allowed bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-600',
          )}
        >
          {isLoading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <SendHorizonal size={18} />
          )}
        </button>
      </form>
    </div>
  )
}
