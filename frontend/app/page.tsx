'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Bot, Sparkles, Zap, Shield, MessageSquare, TrendingUp, ArrowRight, Github, Mail } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function HomePage() {
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <main className="min-h-screen overflow-hidden">
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

          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-slate-300 hover:text-electric-blue transition-colors">
              Features
            </Link>
            <Link href="#about" className="text-slate-300 hover:text-electric-blue transition-colors">
              About
            </Link>
            <Link href="/chat" className="px-4 py-2 rounded-lg bg-gradient-to-r from-electric-blue to-neon-cyan text-white font-semibold hover:shadow-glow-blue transition-all btn-ripple">
              Try Now
            </Link>
          </div>

          <button className="md:hidden">
            <div className="w-6 h-0.5 bg-electric-blue mb-1"></div>
            <div className="w-6 h-0.5 bg-electric-blue mb-1"></div>
            <div className="w-6 h-0.5 bg-electric-blue"></div>
          </button>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 px-6">
        {/* Parallax Background Elements */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ transform: `translateY(${scrollY * 0.5}px)` }}
        >
          <div className="absolute top-40 left-10 w-2 h-2 bg-electric-blue rounded-full animate-pulse" />
          <div className="absolute top-60 right-20 w-3 h-3 bg-neon-cyan rounded-full animate-pulse" style={{ animationDelay: '0.5s' }} />
          <div className="absolute bottom-40 left-1/4 w-2 h-2 bg-mystic-purple rounded-full animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/3 right-1/3 w-2 h-2 bg-glow-blue rounded-full animate-pulse" style={{ animationDelay: '1.5s' }} />
        </div>

        <div className="max-w-6xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-electric-blue/30 mb-8"
            >
              <Sparkles className="w-4 h-4 text-neon-cyan" />
              <span className="text-sm text-slate-300">AI-Powered University Assistant</span>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
            >
              Your Smart Companion for{' '}
              <span className="gradient-text glow-text">KIIT University</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.8 }}
              className="text-xl md:text-2xl text-slate-400 mb-12 max-w-3xl mx-auto"
            >
              Get instant answers about exams, notices, schedules, and more.
              Powered by advanced AI and real-time data from official sources.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.8 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
            >
              <Link
                href="/register"
                className="group px-8 py-4 rounded-xl bg-gradient-to-r from-electric-blue via-mystic-purple to-neon-cyan text-white font-bold text-lg shadow-glow-blue hover:shadow-glow-purple transition-all btn-ripple flex items-center gap-2"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <Link
                href="/login"
                className="px-8 py-4 rounded-xl glass border border-electric-blue/30 hover:border-electric-blue/60 text-white font-semibold text-lg transition-all card-hover"
              >
                Sign In
              </Link>

              <Link
                href="/chat"
                className="px-8 py-4 rounded-xl border-2 border-neon-cyan/50 hover:bg-neon-cyan/10 text-neon-cyan font-semibold text-lg transition-all"
              >
                Try Without Login
              </Link>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.9, duration: 0.8 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
            >
              {[
                { icon: MessageSquare, label: 'Conversations', value: '10K+' },
                { icon: Zap, label: 'Response Time', value: '<2s' },
                { icon: TrendingUp, label: 'Accuracy', value: '95%' },
              ].map((stat, index) => (
                <div
                  key={index}
                  className="glass p-6 rounded-xl border border-electric-blue/20 card-hover"
                >
                  <stat.icon className="w-8 h-8 text-neon-cyan mx-auto mb-3" />
                  <div className="text-3xl font-bold gradient-text">{stat.value}</div>
                  <div className="text-slate-400 text-sm mt-1">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 1 }}
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
        >
          <div className="flex flex-col items-center gap-2 animate-bounce">
            <span className="text-slate-400 text-sm">Scroll to explore</span>
            <div className="w-6 h-10 rounded-full border-2 border-electric-blue/50 flex items-start justify-center p-2">
              <div className="w-1 h-3 bg-electric-blue rounded-full animate-pulse" />
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Powerful Features
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Built with cutting-edge AI technology to serve KIIT students better
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Bot,
                title: 'AI-Powered Responses',
                description: 'Get instant, accurate answers powered by advanced language models and real-time data.',
                color: 'electric-blue',
              },
              {
                icon: Zap,
                title: 'Lightning Fast',
                description: 'Sub-2 second response times with intelligent caching and optimization.',
                color: 'neon-cyan',
              },
              {
                icon: Shield,
                title: 'Always Updated',
                description: 'Automatically scrapes official sources every 6 hours for the latest information.',
                color: 'mystic-purple',
              },
              {
                icon: MessageSquare,
                title: 'Natural Conversations',
                description: 'Chat naturally and get human-like responses with source citations.',
                color: 'electric-blue',
              },
              {
                icon: Sparkles,
                title: 'Smart Search',
                description: 'Semantic search understands your intent, not just keywords.',
                color: 'neon-cyan',
              },
              {
                icon: TrendingUp,
                title: 'Learning System',
                description: 'Continuously improves based on user interactions and feedback.',
                color: 'mystic-purple',
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className="group glass p-8 rounded-2xl border border-electric-blue/20 card-hover cursor-pointer"
              >
                <div className={`w-14 h-14 rounded-xl bg-${feature.color}/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-7 h-7 text-${feature.color}`} />
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-32 px-6 relative">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              How It Works
            </h2>
            <p className="text-xl text-slate-400">Simple, fast, and intelligent</p>
          </motion.div>

          <div className="relative">
            {/* Connection Line */}
            <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-electric-blue via-mystic-purple to-neon-cyan opacity-30 hidden md:block" />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
              {[
                {
                  step: '01',
                  title: 'Ask Anything',
                  description: 'Type your question about exams, notices, schedules, or any university information.',
                },
                {
                  step: '02',
                  title: 'AI Processing',
                  description: 'Our advanced AI searches through thousands of official documents in milliseconds.',
                },
                {
                  step: '03',
                  title: 'Get Answer',
                  description: 'Receive accurate, source-cited answers instantly with links to original documents.',
                },
              ].map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.2, duration: 0.6 }}
                  className="relative"
                >
                  <div className="glass p-8 rounded-2xl border border-electric-blue/30 text-center">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-electric-blue to-mystic-purple flex items-center justify-center text-2xl font-bold mx-auto mb-6 shadow-glow-blue">
                      {step.step}
                    </div>
                    <h3 className="text-xl font-bold mb-4 text-white">{step.title}</h3>
                    <p className="text-slate-400">{step.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="glass p-12 rounded-3xl border border-electric-blue/30 neon-border"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-slate-400 mb-10">
              Join thousands of KIIT students using AI to stay informed
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/register"
                className="px-10 py-5 rounded-xl bg-gradient-to-r from-electric-blue to-neon-cyan text-white font-bold text-lg shadow-glow-blue hover:shadow-glow-purple transition-all btn-ripple"
              >
                Create Free Account
              </Link>
              <Link
                href="/chat"
                className="px-10 py-5 rounded-xl glass border border-neon-cyan/50 hover:border-neon-cyan text-white font-semibold text-lg transition-all"
              >
                Try Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-electric-blue/20 bg-midnight/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Bot className="w-6 h-6 text-electric-blue" />
                <span className="font-bold text-lg gradient-text">KIIT Assistant</span>
              </div>
              <p className="text-slate-400 text-sm">
                Your intelligent companion for KIIT University information.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-white">Product</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><Link href="/chat" className="hover:text-electric-blue transition-colors">Chat</Link></li>
                <li><Link href="/search" className="hover:text-electric-blue transition-colors">Search</Link></li>
                <li><Link href="#features" className="hover:text-electric-blue transition-colors">Features</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-white">Company</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><Link href="#about" className="hover:text-electric-blue transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-electric-blue transition-colors">Privacy</Link></li>
                <li><Link href="#" className="hover:text-electric-blue transition-colors">Terms</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-white">Connect</h3>
              <div className="flex gap-4">
                <a href="https://github.com" className="w-10 h-10 rounded-lg glass border border-electric-blue/30 flex items-center justify-center hover:border-electric-blue transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href="mailto:support@kiitassistant.com" className="w-10 h-10 rounded-lg glass border border-electric-blue/30 flex items-center justify-center hover:border-electric-blue transition-colors">
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-electric-blue/10 text-center text-slate-400 text-sm">
            <p>&copy; 2025 KIIT Assistant. All rights reserved. Built with ❤️ for KIIT students.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
