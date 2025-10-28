'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Bot, Mail, Lock, ArrowRight, Sparkles, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

type LoginFormData = {
  email: string
  password: string
  rememberMe: boolean
}

export default function LoginPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>()

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    setError(null)

    try {
      // TODO: Replace with actual API call
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Login failed')
      }

      const result = await response.json()

      // Store token and user data
      if (data.rememberMe) {
        localStorage.setItem('auth_token', result.token)
        localStorage.setItem('user', JSON.stringify(result.user))
      } else {
        sessionStorage.setItem('auth_token', result.token)
        sessionStorage.setItem('user', JSON.stringify(result.user))
      }

      // Redirect to chat
      router.push('/chat')
    } catch (err: any) {
      setError(err.message || 'Failed to login. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6 py-12 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-10 w-64 h-64 bg-electric-blue/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-mystic-purple/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '-3s' }} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-neon-cyan/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '-1.5s' }} />
      </div>

      <div className="max-w-md w-full relative z-10">
        {/* Logo/Brand */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <Link href="/" className="inline-flex items-center gap-2 group mb-4">
            <div className="relative">
              <Bot className="w-10 h-10 text-electric-blue animate-pulse" />
              <Sparkles className="w-4 h-4 text-neon-cyan absolute -top-1 -right-1 animate-spin-slow" />
            </div>
            <span className="text-2xl font-bold gradient-text">KIIT Assistant</span>
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-slate-400">Sign in to access your AI assistant</p>
        </motion.div>

        {/* Login Form */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="glass p-8 rounded-2xl border border-electric-blue/30 neon-border"
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                  className="w-full pl-11 pr-4 py-3 bg-midnight/50 border border-electric-blue/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all"
                  placeholder="your.email@kiit.ac.in"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="password" className="block text-sm font-medium text-slate-300">
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  className="text-xs text-electric-blue hover:text-neon-cyan transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
                    },
                  })}
                  className="w-full pl-11 pr-12 py-3 bg-midnight/50 border border-electric-blue/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-electric-blue transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                id="rememberMe"
                type="checkbox"
                {...register('rememberMe')}
                className="w-4 h-4 rounded border-electric-blue/30 bg-midnight/50 text-electric-blue focus:ring-electric-blue focus:ring-offset-0 focus:ring-2 transition-all"
              />
              <label htmlFor="rememberMe" className="ml-2 text-sm text-slate-300">
                Remember me for 30 days
              </label>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full group px-6 py-4 rounded-xl bg-gradient-to-r from-electric-blue via-mystic-purple to-neon-cyan text-white font-bold text-lg shadow-glow-blue hover:shadow-glow-purple transition-all btn-ripple flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Signing In...</span>
                </div>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-electric-blue/20" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-midnight/80 text-slate-400">Or continue with</span>
              </div>
            </div>

            {/* Guest Access */}
            <Link
              href="/chat"
              className="w-full block text-center px-6 py-3 rounded-xl glass border border-neon-cyan/50 hover:border-neon-cyan hover:bg-neon-cyan/10 text-neon-cyan font-semibold transition-all"
            >
              Continue as Guest
            </Link>
          </form>
        </motion.div>

        {/* Register Link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-6"
        >
          <p className="text-slate-400">
            Don't have an account?{' '}
            <Link href="/register" className="text-electric-blue hover:text-neon-cyan font-semibold transition-colors">
              Sign Up
            </Link>
          </p>
        </motion.div>

        {/* Back to Home */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center mt-4"
        >
          <Link href="/" className="text-slate-500 hover:text-electric-blue text-sm transition-colors">
            ← Back to Home
          </Link>
        </motion.div>

        {/* Security Notice */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-8 p-4 glass rounded-xl border border-electric-blue/20 text-center"
        >
          <p className="text-xs text-slate-400">
            🔒 Your credentials are encrypted and secure. We never share your personal information.
          </p>
        </motion.div>
      </div>
    </main>
  )
}
