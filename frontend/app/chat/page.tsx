'use client'

import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { Bot, Send, Sparkles, User, ExternalLink, Calendar, FileText, Clock, Menu, X, LogOut } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { chatAPI, getCurrentUser, isAuthenticated, clearAuth } from '@/lib/api'
import type { ChatMessage, Source } from '@/lib/api'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [streamingMessage, setStreamingMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const user = getCurrentUser()
  const authenticated = isAuthenticated()

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingMessage])

  // Load chat history if authenticated
  useEffect(() => {
    if (authenticated) {
      loadChatHistory()
    }
  }, [authenticated])

  const loadChatHistory = async () => {
    try {
      const history = await chatAPI.getChatHistory(sessionId)
      setMessages(history)
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  // WebSocket connection
  const connectWebSocket = () => {
    const websocket = new WebSocket(`${WS_URL}/ws/chat`)

    websocket.onopen = () => {
      console.log('WebSocket connected')
      setWs(websocket)
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'token') {
        setStreamingMessage((prev) => prev + data.content)
      } else if (data.type === 'sources') {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: streamingMessage,
          timestamp: new Date().toISOString(),
          sources: data.data,
        }
        setMessages((prev) => [...prev, assistantMessage])
        setStreamingMessage('')
        setIsTyping(false)
        setIsLoading(false)
      } else if (data.type === 'done') {
        setIsTyping(false)
        setIsLoading(false)
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsTyping(false)
      setIsLoading(false)
    }

    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      setWs(null)
    }

    return websocket
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setIsTyping(true)

    try {
      // Use WebSocket if available, otherwise fallback to REST API
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            query: userMessage.content,
            session_id: sessionId,
          })
        )
      } else {
        // Fallback to REST API
        const response = await chatAPI.sendMessage(userMessage.content, sessionId)
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
          sources: response.sources,
        }
        setMessages((prev) => [...prev, assistantMessage])
        setIsTyping(false)
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      setIsTyping(false)
      setIsLoading(false)

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    }
  }

  const handleLogout = () => {
    clearAuth()
    window.location.href = '/login'
  }

  const suggestedQuestions = [
    'When is the next exam?',
    'Show me recent notices',
    'What are the holidays this month?',
    'Tell me about the academic calendar',
  ]

  return (
    <main className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Header */}
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4 backdrop-blur-xl bg-space-dark/80 border-b border-electric-blue/20"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative">
              <Bot className="w-8 h-8 text-electric-blue animate-pulse" />
              <Sparkles className="w-4 h-4 text-neon-cyan absolute -top-1 -right-1 animate-spin-slow" />
            </div>
            <span className="text-xl font-bold gradient-text">KIIT Assistant</span>
          </Link>

          <div className="flex items-center gap-4">
            {authenticated && user ? (
              <div className="hidden md:flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-2 glass rounded-lg border border-electric-blue/30">
                  <User className="w-4 h-4 text-electric-blue" />
                  <span className="text-sm text-slate-300">{user.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 glass rounded-lg border border-electric-blue/30 hover:border-electric-blue text-slate-300 hover:text-white transition-all"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="hidden md:flex items-center gap-3">
                <Link
                  href="/login"
                  className="px-4 py-2 glass rounded-lg border border-electric-blue/30 hover:border-electric-blue text-white transition-all"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-electric-blue to-neon-cyan text-white font-semibold hover:shadow-glow-blue transition-all"
                >
                  Sign Up
                </Link>
              </div>
            )}

            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden p-2 glass rounded-lg border border-electric-blue/30"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </motion.header>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 20 }}
            className="fixed top-20 right-0 bottom-0 w-64 glass border-l border-electric-blue/30 p-6 z-40 md:hidden"
          >
            <div className="flex flex-col gap-4">
              {authenticated && user ? (
                <>
                  <div className="flex items-center gap-2 p-3 glass rounded-lg border border-electric-blue/30">
                    <User className="w-4 h-4 text-electric-blue" />
                    <span className="text-sm text-slate-300">{user.name}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 p-3 glass rounded-lg border border-electric-blue/30 hover:border-electric-blue text-slate-300 hover:text-white transition-all"
                  >
                    <LogOut className="w-5 h-5" />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="px-4 py-2 glass rounded-lg border border-electric-blue/30 hover:border-electric-blue text-white text-center transition-all"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/register"
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-electric-blue to-neon-cyan text-white font-semibold hover:shadow-glow-blue text-center transition-all"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col pt-20 pb-32 px-4 md:px-6">
        <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-6 py-8">
            {messages.length === 0 && !streamingMessage && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-12"
              >
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-electric-blue to-mystic-purple flex items-center justify-center shadow-glow-blue">
                  <Bot className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Welcome to KIIT Assistant
                </h2>
                <p className="text-slate-400 mb-8">
                  Ask me anything about exams, notices, schedules, and more!
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                  {suggestedQuestions.map((question, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setInput(question)}
                      className="p-4 glass rounded-xl border border-electric-blue/30 hover:border-electric-blue text-left text-slate-300 hover:text-white transition-all card-hover"
                    >
                      {question}
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}

            <AnimatePresence mode="popLayout">
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-electric-blue to-mystic-purple flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}

                  <div
                    className={`max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-electric-blue to-mystic-purple text-white rounded-2xl rounded-tr-sm px-4 py-3'
                        : 'glass border border-electric-blue/30 rounded-2xl rounded-tl-sm px-4 py-3'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {message.content}
                    </p>

                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-electric-blue/20">
                        <p className="text-xs text-slate-400 mb-2 flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          Sources:
                        </p>
                        <div className="space-y-2">
                          {message.sources.map((source, idx) => (
                            <a
                              key={idx}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="block p-2 bg-midnight/50 rounded-lg border border-electric-blue/20 hover:border-electric-blue transition-all group"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-medium text-white truncate group-hover:text-electric-blue transition-colors">
                                    {source.title}
                                  </p>
                                  {source.date && (
                                    <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                                      <Calendar className="w-3 h-3" />
                                      {new Date(source.date).toLocaleDateString()}
                                    </p>
                                  )}
                                </div>
                                <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-electric-blue transition-colors flex-shrink-0" />
                              </div>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    <p className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neon-cyan to-electric-blue flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Streaming Message */}
            {streamingMessage && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 justify-start"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-electric-blue to-mystic-purple flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="max-w-[80%] glass border border-electric-blue/30 rounded-2xl rounded-tl-sm px-4 py-3">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {streamingMessage}
                    <span className="inline-block w-1 h-4 bg-electric-blue animate-pulse ml-1" />
                  </p>
                </div>
              </motion.div>
            )}

            {/* Typing Indicator */}
            {isTyping && !streamingMessage && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 justify-start"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-electric-blue to-mystic-purple flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="glass border border-electric-blue/30 rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-electric-blue rounded-full typing-dot" />
                    <div className="w-2 h-2 bg-electric-blue rounded-full typing-dot" />
                    <div className="w-2 h-2 bg-electric-blue rounded-full typing-dot" />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Bar */}
      <motion.div
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-0 left-0 right-0 px-4 md:px-6 py-4 backdrop-blur-xl bg-space-dark/80 border-t border-electric-blue/20"
      >
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about KIIT..."
              disabled={isLoading}
              className="w-full pl-6 pr-14 py-4 bg-midnight/50 border border-electric-blue/30 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-3 rounded-xl bg-gradient-to-r from-electric-blue to-neon-cyan text-white hover:shadow-glow-blue transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>

          <p className="text-xs text-slate-500 text-center mt-3">
            KIIT Assistant may occasionally make mistakes. Always verify important information.
          </p>
        </div>
      </motion.div>
    </main>
  )
}
