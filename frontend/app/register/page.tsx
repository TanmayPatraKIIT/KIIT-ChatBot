'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Bot, Mail, Lock, User, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address').refine(
    (email) => email.endsWith('@kiit.ac.in') || email.includes('@'),
    'Please use a valid email address'
  ),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

type RegisterFormData = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterFormData>()

  const password = watch('password')

  const passwordStrength = (pwd: string) => {
    if (!pwd) return { strength: 0, label: '', color: '' }
    let strength = 0
    if (pwd.length >= 8) strength++
    if (pwd.length >= 12) strength++
    if (/[A-Z]/.test(pwd)) strength++
    if (/[a-z]/.test(pwd)) strength++
    if (/[0-9]/.test(pwd)) strength++
    if (/[^A-Za-z0-9]/.test(pwd)) strength++

    if (strength <= 2) return { strength: 33, label: 'Weak', color: 'bg-red-500' }
    if (strength <= 4) return { strength: 66, label: 'Medium', color: 'bg-yellow-500' }
    return { strength: 100, label: 'Strong', color: 'bg-green-500' }
  }

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)
    setError(null)

    try {
      // TODO: Replace with actual API call
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          password: data.password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Registration failed')
      }

      setSuccess(true)
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to register. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const pwdStrength = passwordStrength(password || '')

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
          <h1 className="text-3xl font-bold text-white mb-2">Create Your Account</h1>
          <p className="text-slate-400">Join thousands of KIIT students using AI assistance</p>
        </motion.div>

        {/* Registration Form */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="glass p-8 rounded-2xl border border-electric-blue/30 neon-border"
        >
          {success ? (
            <div className="text-center py-8">
              <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4 animate-pulse" />
              <h2 className="text-2xl font-bold text-white mb-2">Registration Successful!</h2>
              <p className="text-slate-400">Redirecting to login...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Name Field */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    id="name"
                    type="text"
                    {...register('name', { required: true })}
                    className="w-full pl-11 pr-4 py-3 bg-midnight/50 border border-electric-blue/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all"
                    placeholder="Enter your full name"
                  />
                </div>
                {errors.name && (
                  <p className="mt-1 text-sm text-red-400">{errors.name.message}</p>
                )}
              </div>

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
                    {...register('email', { required: true })}
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
                <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    id="password"
                    type="password"
                    {...register('password', { required: true })}
                    className="w-full pl-11 pr-4 py-3 bg-midnight/50 border border-electric-blue/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all"
                    placeholder="Create a strong password"
                  />
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
                )}

                {/* Password Strength Indicator */}
                {password && password.length > 0 && (
                  <div className="mt-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-slate-400">Password Strength</span>
                      <span className={`text-xs font-semibold ${
                        pwdStrength.label === 'Weak' ? 'text-red-400' :
                        pwdStrength.label === 'Medium' ? 'text-yellow-400' :
                        'text-green-400'
                      }`}>
                        {pwdStrength.label}
                      </span>
                    </div>
                    <div className="h-2 bg-midnight rounded-full overflow-hidden">
                      <div
                        className={`h-full ${pwdStrength.color} transition-all duration-300`}
                        style={{ width: `${pwdStrength.strength}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm Password Field */}
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    id="confirmPassword"
                    type="password"
                    {...register('confirmPassword', { required: true })}
                    className="w-full pl-11 pr-4 py-3 bg-midnight/50 border border-electric-blue/30 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-electric-blue focus:ring-2 focus:ring-electric-blue/20 transition-all"
                    placeholder="Re-enter your password"
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="mt-1 text-sm text-red-400">{errors.confirmPassword.message}</p>
                )}
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
                    <span>Creating Account...</span>
                  </div>
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>

              {/* Terms */}
              <p className="text-xs text-slate-400 text-center">
                By creating an account, you agree to our{' '}
                <Link href="#" className="text-electric-blue hover:text-neon-cyan transition-colors">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="#" className="text-electric-blue hover:text-neon-cyan transition-colors">
                  Privacy Policy
                </Link>
              </p>
            </form>
          )}
        </motion.div>

        {/* Login Link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-6"
        >
          <p className="text-slate-400">
            Already have an account?{' '}
            <Link href="/login" className="text-electric-blue hover:text-neon-cyan font-semibold transition-colors">
              Sign In
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
      </div>
    </main>
  )
}
