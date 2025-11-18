/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable SWC minification for faster builds
  swcMinify: true,

  // Image optimization
  images: {
    domains: ['localhost', 'kiitassistant.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Environment variables validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
  },

  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },

  // Redirects
  async redirects() {
    return [
      // Add any redirects here if needed
    ]
  },

  // Rewrites for API proxy (optional, for development)
  async rewrites() {
    return [
      // Uncomment to proxy API requests to avoid CORS in development
      // {
      //   source: '/api/:path*',
      //   destination: 'http://localhost:8000/api/:path*',
      // },
    ]
  },

  // Experimental features
  experimental: {
    // Enable Server Actions if needed in future
    // serverActions: true,
  },

  // Output configuration
  output: 'standalone', // For Docker deployment

  // Webpack configuration (if needed)
  webpack: (config, { isServer }) => {
    // Custom webpack config can go here
    return config
  },
}

module.exports = nextConfig
