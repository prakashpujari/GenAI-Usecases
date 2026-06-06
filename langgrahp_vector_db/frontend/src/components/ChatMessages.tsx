import { forwardRef, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import clsx from 'clsx'
import { Bot, User } from 'lucide-react'
import type { ChatMessage } from '@/types'
import { RouteBadge } from './RouteBadge'
import { useAgentStore } from '@/store/agentStore'

// ---------------------------------------------------------------------------
// Single message bubble
// ---------------------------------------------------------------------------
interface BubbleProps {
  message: ChatMessage
  isSelected: boolean
  onSelect: () => void
}

function MessageBubble({ message, isSelected, onSelect }: BubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={clsx(
        'group flex gap-3 animate-slide-up',
        isUser ? 'flex-row-reverse' : 'flex-row',
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          'mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          isUser
            ? 'bg-brand-500 text-white'
            : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300',
        )}
      >
        {isUser ? <User size={15} /> : <Bot size={15} />}
      </div>

      {/* Bubble */}
      <div className="flex max-w-[78%] flex-col gap-1.5">
        <div
          className={clsx(
            'rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm',
            isUser
              ? 'rounded-tr-sm bg-brand-500 text-white'
              : clsx(
                  'rounded-tl-sm bg-white text-zinc-800 dark:bg-zinc-800 dark:text-zinc-100',
                  'ring-1 ring-zinc-200 dark:ring-zinc-700',
                  !isUser && 'cursor-pointer transition hover:ring-brand-400',
                  isSelected && '!ring-2 !ring-brand-500',
                ),
          )}
          onClick={!isUser ? onSelect : undefined}
          title={!isUser ? 'Click to inspect pipeline trace' : undefined}
        >
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Meta row */}
        <div
          className={clsx(
            'flex items-center gap-2 px-1 text-[11px] text-zinc-400',
            isUser ? 'flex-row-reverse' : 'flex-row',
          )}
        >
          <span>
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          {message.response && <RouteBadge route={message.response.route} />}
          {!isUser && message.response && (
            <span className="opacity-0 transition group-hover:opacity-100">
              click to inspect →
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Typing indicator
// ---------------------------------------------------------------------------
function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-100 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300">
        <Bot size={15} />
      </div>
      <div className="rounded-2xl rounded-tl-sm bg-white px-4 py-3.5 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-800 dark:ring-zinc-700">
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="inline-block h-2 w-2 rounded-full bg-zinc-400 animate-pulse-dot"
              style={{ animationDelay: `${i * 0.16}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Chat message list (scrollable)
// ---------------------------------------------------------------------------
export const ChatMessages = forwardRef<HTMLDivElement>((_, ref) => {
  const messages   = useAgentStore((s) => s.messages)
  const isLoading  = useAgentStore((s) => s.isLoading)
  const selectedId = useAgentStore((s) => s.selectedId)
  const select     = useAgentStore((s) => s.selectMessage)

  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-zinc-400 dark:text-zinc-500">
        <Bot size={40} strokeWidth={1.2} />
        <p className="text-sm">Ask anything – RAG, SQL, or both.</p>
      </div>
    )
  }

  return (
    <div ref={ref} className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-4">
      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          isSelected={msg.id === selectedId}
          onSelect={() => select(msg.id)}
        />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
})
ChatMessages.displayName = 'ChatMessages'
