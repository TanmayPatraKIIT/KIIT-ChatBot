import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'KIIT Assistant - AI-Powered University Chatbot',
  description: 'Your intelligent companion for KIIT University information, notices, and assistance.',
  keywords: 'KIIT, university, chatbot, AI, assistant, notices, academic',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-space-dark text-slate-100 antialiased`}>
        {/* Background Elements */}
        <div className="fixed inset-0 -z-50">
          {/* Animated Grid */}
          <div className="cyber-grid-bg absolute inset-0 opacity-30" />

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-space-dark via-midnight to-space-dark opacity-90" />

          {/* Floating Orbs */}
          <div className="absolute top-20 left-20 w-64 h-64 bg-electric-blue/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-20 right-20 w-80 h-80 bg-mystic-purple/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '-3s' }} />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-neon-cyan/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '-1.5s' }} />
        </div>

        {/* Main Content */}
        <div className="relative z-0">
          {children}
        </div>

        {/* Global Scripts */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Add smooth scrolling behavior
              document.addEventListener('DOMContentLoaded', function() {
                // Enhanced smooth scrolling for anchor links
                const links = document.querySelectorAll('a[href^="#"]');
                links.forEach(link => {
                  link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                      target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                      });
                    }
                  });
                });
              });
            `,
          }}
        />
      </body>
    </html>
  )
}