import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import { api } from '../services/api'

const SUGGESTIONS = [
  'What is my total spending this month?',
  'Show me my top spending categories',
  'Find my recurring expenses',
  'Check my budget status',
  'Compare last two months',
]

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm FinTrack AI, your personal finance assistant. I can analyze your spending, check budgets, find recurring expenses, and more. How can I help?",
    },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return

    const userMsg = text.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const res = await api.chat(userMsg, sessionId)
      if (!sessionId) setSessionId(res.session_id)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.reply, tools: res.tool_calls },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message}. Make sure your GEMINI_API_KEY is configured.`, error: true },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page chat-page">
      <header className="page-header">
        <h2><Sparkles size={24} className="inline-icon" /> AI Finance Assistant</h2>
        <p>Powered by Gemini & LangGraph — ask anything about your finances</p>
      </header>

      <div className="chat-container card">
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble chat-${msg.role} ${msg.error ? 'chat-error' : ''}`}>
              <div className="chat-avatar">
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="chat-content">
                <p>{msg.content}</p>
                {msg.tools?.length > 0 && (
                  <div className="tool-badges">
                    {msg.tools.map((t, j) => (
                      <span key={j} className="tool-badge">🔧 {t}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-bubble chat-assistant">
              <div className="chat-avatar"><Bot size={18} /></div>
              <div className="chat-content"><p className="typing">Thinking...</p></div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="suggestion-chip" onClick={() => sendMessage(s)} disabled={loading}>
              {s}
            </button>
          ))}
        </div>

        <form
          className="chat-input-bar"
          onSubmit={(e) => { e.preventDefault(); sendMessage(input) }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your finances..."
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  )
}
