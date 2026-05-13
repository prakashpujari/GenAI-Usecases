import { useState, useEffect, useRef } from 'react'
import './App.css'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState({ provider: '...', model: '...' })
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    // Fetch backend provider/model once so users can see which model is active.
    fetch('/api/status')
      .then(r => r.json())
      .then(setStatus)
      .catch(() => {})
  }, [])

  useEffect(() => {
    // Keep the latest message in view after new messages or loading indicator changes.
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function autoResize() {
    const el = textareaRef.current
    if (!el) return
    // Reset first, then grow up to a max height to avoid huge input boxes.
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    // Run after state update so textarea measures the cleared content.
    setTimeout(autoResize, 0)
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      // API returns assistant reply plus usage metadata for the message footer.
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.reply, usage: data.usage, turn: data.turn_count },
      ])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: String(err) }])
    } finally {
      setLoading(false)
    }
  }

  async function resetChat() {
    // Reset both server-side context and local chat state.
    await fetch('/api/reset', { method: 'POST' }).catch(() => {})
    setMessages([])
  }

  function handleKeyDown(e) {
    // Enter sends, Shift+Enter inserts a newline.
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function formatUsage(usage) {
    if (!usage) return ''
    const parts = [`in: ${usage.input}`, `out: ${usage.output}`]
    if (usage.cache_read) parts.push(`cache_read: ${usage.cache_read}`)
    if (usage.cache_write) parts.push(`cache_write: ${usage.cache_write}`)
    return parts.join(' · ')
  }

  return (
    <div className="app">
      <header className="header">
        <span className="header-title">Joshitha's chatbot</span>
        <div className="header-meta">
          <span className="badge">{status.provider}</span>
          <span className="model-name">{status.model}</span>
        </div>
        <button className="reset-btn" onClick={resetChat}>Reset</button>
      </header>

      <main className="messages">
        {messages.length === 0 && !loading && (
          <div className="empty">Send a message to start chatting.</div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">{msg.content}</div>
            {msg.usage && (
              <div className="usage">{formatUsage(msg.usage)} · turn {msg.turn}</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble loading">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <footer className="input-bar">
        <textarea
          ref={textareaRef}
          className="input"
          value={input}
          onChange={e => { setInput(e.target.value); autoResize() }}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
          rows={1}
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </footer>
    </div>
  )
}
