'use client'

import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { Bot, Search, Sparkles, Filter, Calendar, FileText, ExternalLink, RefreshCw, AlertCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { searchAPI } from '@/lib/api'
import type { SearchResult, NoticeFilters } from '@/lib/api'

const SOURCE_TYPES = [
  { value: '', label: 'All Sources' },
  { value: 'general_notices', label: 'General Notices' },
  { value: 'exam_notices', label: 'Exam Notices' },
  { value: 'holidays', label: 'Holidays' },
  { value: 'academic_calendar', label: 'Academic Calendar' },
]

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [latestNotices, setLatestNotices] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const [filters, setFilters] = useState<NoticeFilters>({
    source_type: '',
    start_date: '',
    end_date: '',
  })

  // Load latest notices on mount
  useEffect(() => {
    loadLatestNotices()
  }, [])

  const loadLatestNotices = async () => {
    try {
      const notices = await searchAPI.getLatestNotices(12)
      setLatestNotices(notices)
    } catch (error) {
      console.error('Failed to load latest notices:', error)
    }
  }

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()

    if (!query.trim()) {
      setResults([])
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await searchAPI.search(query, filters, 20)
      setResults(response.results)
    } catch (err: any) {
      setError(err.message || 'Failed to search. Please try again.')
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFilterChange = (key: keyof NoticeFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  const clearFilters = () => {
    setFilters({
      source_type: '',
      start_date: '',
      end_date: '',
    })
  }

  const hasActiveFilters = filters.source_type || filters.start_date || filters.end_date

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Navigation */}
      <motion.nav
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
            <Link href="/chat" className="text-slate-300 hover:text-electric-blue transition-colors">
              Chat
            </Link>
            <Link
              href="/login"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-electric-blue to-neon-cyan text-white font-semibold hover:shadow-glow-blue transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* Background Elements */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute top-20 left-10 w-64 h-64 bg-electric-blue/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-mystic-purple/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '-3s' }} />
      </div>

      <div className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-4 gradient-text">
              Search Notices & Information
            </h1>
            <p className="text-xl text-slate-400">
              Browse and search through thousands of KIIT documents
            </p>
          </motion.div>

          {/* Search Bar */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="max-w-3xl mx-auto mb-8"
          >
            <form onSubmit={handleSearch} className="relative">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search for notices, exams, holidays..."
                  className="w-full pl-12 pr-32 py-4 bg-midnight/50 border border-electric-blue/30 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowFilters(!showFilters)}
                    className={`p-2 rounded-lg transition-all ${
                      hasActiveFilters
                        ? 'bg-electric-blue text-white'
                        : 'glass border border-electric-blue/30 text-slate-300 hover:text-white'
                    }`}
                    title="Filters"
                  >
                    <Filter className="w-5 h-5" />
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading || !query.trim()}
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-electric-blue to-neon-cyan text-white font-semibold hover:shadow-glow-blue transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <RefreshCw className="w-5 h-5 animate-spin" />
                    ) : (
                      'Search'
                    )}
                  </button>
                </div>
              </div>
            </form>

            {/* Filters Panel */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 p-6 glass rounded-2xl border border-electric-blue/30 overflow-hidden"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Filters</h3>
                    {hasActiveFilters && (
                      <button
                        onClick={clearFilters}
                        className="text-xs text-electric-blue hover:text-neon-cyan transition-colors"
                      >
                        Clear All
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Source Type */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Source Type
                      </label>
                      <select
                        value={filters.source_type}
                        onChange={(e) => handleFilterChange('source_type', e.target.value)}
                        className="w-full px-3 py-2 bg-midnight/50 border border-electric-blue/30 rounded-lg text-white focus:outline-none focus:border-electric-blue transition-all"
                      >
                        {SOURCE_TYPES.map((type) => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Start Date */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Start Date
                      </label>
                      <input
                        type="date"
                        value={filters.start_date}
                        onChange={(e) => handleFilterChange('start_date', e.target.value)}
                        className="w-full px-3 py-2 bg-midnight/50 border border-electric-blue/30 rounded-lg text-white focus:outline-none focus:border-electric-blue transition-all"
                      />
                    </div>

                    {/* End Date */}
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        End Date
                      </label>
                      <input
                        type="date"
                        value={filters.end_date}
                        onChange={(e) => handleFilterChange('end_date', e.target.value)}
                        className="w-full px-3 py-2 bg-midnight/50 border border-electric-blue/30 rounded-lg text-white focus:outline-none focus:border-electric-blue transition-all"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-3xl mx-auto mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-400">{error}</p>
            </motion.div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-16"
            >
              <h2 className="text-2xl font-bold text-white mb-6">
                Search Results ({results.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((result, index) => (
                  <NoticeCard key={result.id} notice={result} index={index} />
                ))}
              </div>
            </motion.div>
          )}

          {/* Latest Notices */}
          {results.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Latest Notices</h2>
                <button
                  onClick={loadLatestNotices}
                  className="p-2 glass rounded-lg border border-electric-blue/30 hover:border-electric-blue text-slate-300 hover:text-white transition-all"
                  title="Refresh"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
              </div>

              {latestNotices.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {latestNotices.map((notice, index) => (
                    <NoticeCard key={notice.id} notice={notice} index={index} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 glass rounded-2xl border border-electric-blue/30">
                  <FileText className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                  <p className="text-slate-400">No notices available</p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </main>
  )
}

// Notice Card Component
function NoticeCard({ notice, index }: { notice: SearchResult; index: number }) {
  const getSourceTypeLabel = (type: string) => {
    const source = SOURCE_TYPES.find((s) => s.value === type)
    return source?.label || type
  }

  const getSourceTypeColor = (type: string) => {
    switch (type) {
      case 'general_notices':
        return 'bg-electric-blue/20 text-electric-blue border-electric-blue/30'
      case 'exam_notices':
        return 'bg-mystic-purple/20 text-mystic-purple border-mystic-purple/30'
      case 'holidays':
        return 'bg-neon-cyan/20 text-neon-cyan border-neon-cyan/30'
      case 'academic_calendar':
        return 'bg-glow-purple/20 text-glow-purple border-glow-purple/30'
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30'
    }
  }

  return (
    <motion.a
      href={notice.url}
      target="_blank"
      rel="noopener noreferrer"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group block glass p-6 rounded-2xl border border-electric-blue/20 hover:border-electric-blue card-hover"
    >
      {/* Source Badge */}
      <div className="flex items-center justify-between mb-4">
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium border ${getSourceTypeColor(
            notice.source_type
          )}`}
        >
          {getSourceTypeLabel(notice.source_type)}
        </span>
        <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-electric-blue transition-colors" />
      </div>

      {/* Title */}
      <h3 className="text-lg font-bold text-white mb-3 line-clamp-2 group-hover:text-electric-blue transition-colors">
        {notice.title}
      </h3>

      {/* Content Preview */}
      <p className="text-sm text-slate-400 mb-4 line-clamp-3">{notice.content}</p>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          <span>{new Date(notice.date).toLocaleDateString()}</span>
        </div>
        {notice.relevance_score && (
          <div className="flex items-center gap-1">
            <span>Relevance:</span>
            <span className="font-semibold text-electric-blue">
              {(notice.relevance_score * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>
    </motion.a>
  )
}
