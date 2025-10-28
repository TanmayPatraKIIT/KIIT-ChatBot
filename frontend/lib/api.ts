import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Try to get token from localStorage first, then sessionStorage
    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
        : null

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Handle 401 Unauthorized - token expired or invalid
      if (error.response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token')
          localStorage.removeItem('user')
          sessionStorage.removeItem('auth_token')
          sessionStorage.removeItem('user')

          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login?expired=true'
          }
        }
      }

      // Handle rate limiting
      if (error.response.status === 429) {
        console.error('Rate limit exceeded. Please try again later.')
      }
    } else if (error.request) {
      console.error('Network error. Please check your connection.')
    }

    return Promise.reject(error)
  }
)

// Types
export interface User {
  id: string
  name: string
  email: string
  created_at: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
}

export interface LoginData {
  email: string
  password: string
}

export interface AuthResponse {
  token: string
  user: User
  message: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Source[]
}

export interface Source {
  title: string
  url: string
  excerpt: string
  date?: string
  relevance_score?: number
}

export interface ChatResponse {
  response: string
  sources: Source[]
  session_id: string
}

export interface SearchResult {
  id: string
  title: string
  content: string
  url: string
  date: string
  source_type: string
  relevance_score: number
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
}

export interface NoticeFilters {
  source_type?: string
  start_date?: string
  end_date?: string
}

// Authentication API
export const authAPI = {
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/register', data)
    return response.data
  },

  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/login', data)
    return response.data
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout')
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('user')
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/refresh')
    return response.data
  },
}

// Chat API
export const chatAPI = {
  sendMessage: async (
    query: string,
    sessionId?: string,
    filters?: NoticeFilters
  ): Promise<ChatResponse> => {
    const response = await apiClient.post('/api/chat', {
      query,
      session_id: sessionId,
      filters,
    })
    return response.data
  },

  getChatHistory: async (sessionId: string): Promise<ChatMessage[]> => {
    const response = await apiClient.get(`/api/chat/history/${sessionId}`)
    return response.data
  },

  clearHistory: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/api/chat/history/${sessionId}`)
  },

  // Stream chat (returns EventSource for SSE)
  streamChat: (query: string, sessionId?: string, filters?: NoticeFilters) => {
    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
        : null

    const params = new URLSearchParams()
    params.append('query', query)
    if (sessionId) params.append('session_id', sessionId)
    if (filters?.source_type) params.append('source_type', filters.source_type)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)

    const url = `${API_BASE_URL}/api/chat/stream?${params.toString()}`

    const eventSource = new EventSource(url, {
      withCredentials: token ? true : false,
    })

    return eventSource
  },
}

// Search API
export const searchAPI = {
  search: async (
    query: string,
    filters?: NoticeFilters,
    limit: number = 10
  ): Promise<SearchResponse> => {
    const response = await apiClient.get('/api/search', {
      params: {
        query,
        limit,
        ...filters,
      },
    })
    return response.data
  },

  getNoticeById: async (noticeId: string): Promise<SearchResult> => {
    const response = await apiClient.get(`/api/notices/${noticeId}`)
    return response.data
  },

  getLatestNotices: async (limit: number = 10): Promise<SearchResult[]> => {
    const response = await apiClient.get('/api/notices/latest', {
      params: { limit },
    })
    return response.data
  },

  getNoticesByType: async (
    sourceType: string,
    limit: number = 10
  ): Promise<SearchResult[]> => {
    const response = await apiClient.get(`/api/notices/type/${sourceType}`, {
      params: { limit },
    })
    return response.data
  },
}

// Admin API (requires authentication)
export const adminAPI = {
  getStats: async () => {
    const response = await apiClient.get('/api/admin/stats')
    return response.data
  },

  triggerScrape: async (sourceType?: string) => {
    const response = await apiClient.post('/api/admin/scrape', {
      source_type: sourceType,
    })
    return response.data
  },

  rebuildIndex: async () => {
    const response = await apiClient.post('/api/admin/rebuild-index')
    return response.data
  },

  clearCache: async () => {
    const response = await apiClient.post('/api/admin/clear-cache')
    return response.data
  },
}

// Utility functions
export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
}

export const getCurrentUser = (): User | null => {
  if (typeof window === 'undefined') return null
  const userStr = localStorage.getItem('user') || sessionStorage.getItem('user')
  if (!userStr) return null
  try {
    return JSON.parse(userStr)
  } catch {
    return null
  }
}

export const isAuthenticated = (): boolean => {
  return !!getAuthToken()
}

export const setAuthToken = (token: string, rememberMe: boolean = false): void => {
  if (typeof window === 'undefined') return
  if (rememberMe) {
    localStorage.setItem('auth_token', token)
  } else {
    sessionStorage.setItem('auth_token', token)
  }
}

export const setCurrentUser = (user: User, rememberMe: boolean = false): void => {
  if (typeof window === 'undefined') return
  const userStr = JSON.stringify(user)
  if (rememberMe) {
    localStorage.setItem('user', userStr)
  } else {
    sessionStorage.setItem('user', userStr)
  }
}

export const clearAuth = (): void => {
  if (typeof window === 'undefined') return
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
  sessionStorage.removeItem('auth_token')
  sessionStorage.removeItem('user')
}

export default apiClient
