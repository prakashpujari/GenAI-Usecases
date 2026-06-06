import { useState } from 'react'
import { Sidebar }        from '@/components/Sidebar'
import { ChatMessages }   from '@/components/ChatMessages'
import { ChatInput }      from '@/components/ChatInput'
import { InspectorPanel } from '@/components/InspectorPanel'
import { ErrorBanner }    from '@/components/ErrorBanner'

export default function App() {
  const [dark, setDark] = useState(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches,
  )

  function toggleDark() {
    setDark((v) => {
      document.documentElement.classList.toggle('dark', !v)
      return !v
    })
  }

  // Apply class on first render
  if (dark) document.documentElement.classList.add('dark')

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-100 font-sans text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      {/* Left sidebar */}
      <Sidebar dark={dark} onToggleDark={toggleDark} />

      {/* Main chat area */}
      <main className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-5 py-3 dark:border-zinc-700 dark:bg-zinc-900">
          <div>
            <h1 className="text-sm font-semibold">Chat</h1>
            <p className="text-[11px] text-zinc-400">LangGraph · OpenAI · FAISS · PostgreSQL</p>
          </div>
        </header>

        {/* Error banner (conditionally shown) */}
        <ErrorBanner />

        {/* Messages */}
        <ChatMessages />

        {/* Input */}
        <ChatInput />
      </main>

      {/* Right inspector panel */}
      <InspectorPanel />
    </div>
  )
}
