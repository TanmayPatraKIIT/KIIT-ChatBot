# KIIT Assistant - Frontend

Modern, AI-powered chatbot frontend for KIIT University students built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- **Dark Cyberspace Theme**: Stunning dark blue/black aesthetic with neon accents
- **Advanced Animations**: Framer Motion animations, parallax effects, glassmorphism
- **Real-time Chat**: WebSocket integration for streaming responses
- **Smart Search**: Browse and filter university notices and documents
- **Authentication**: User registration, login, and session management
- **Responsive Design**: Mobile-first approach with responsive layouts
- **Source Citations**: Every AI response includes links to original sources
- **Type-Safe**: Full TypeScript coverage for better development experience

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **State Management**: Zustand
- **Form Handling**: React Hook Form + Zod
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see `/backend` directory)

### Installation

1. **Install dependencies:**

```bash
npm install
```

2. **Configure environment variables:**

```bash
cp .env.example .env.local
```

Edit `.env.local` and update the API URLs:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. **Run the development server:**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Landing page
│   ├── register/page.tsx    # Registration page
│   ├── login/page.tsx       # Login page
│   ├── chat/page.tsx        # Chat interface
│   ├── search/page.tsx      # Search/browse notices
│   ├── layout.tsx           # Root layout with background
│   └── globals.css          # Global styles and animations
├── lib/                      # Utility libraries
│   └── api.ts               # API client and service functions
├── public/                   # Static assets
├── tailwind.config.ts       # Tailwind configuration
└── package.json             # Dependencies and scripts
```

## Key Pages

### Landing Page (`/`)
- Hero section with parallax effects
- Features showcase
- How it works
- Call-to-action sections
- Registration buttons

### Registration (`/register`)
- User registration form
- Password strength indicator
- Form validation with react-hook-form
- Success animation

### Login (`/login`)
- User authentication
- Remember me option
- Password visibility toggle
- Guest access option

### Chat (`/chat`)
- Real-time chat interface
- WebSocket streaming for responses
- Source citations display
- Suggested questions
- Chat history (authenticated users)

### Search (`/search`)
- Browse latest notices
- Search with filters
- Filter by source type and date range
- Notice cards with external links

## Theme & Design

### Color Palette
- **Space Dark**: `#0A0E27` - Background
- **Midnight**: `#151B3B` - Surface
- **Electric Blue**: `#3B82F6` - Primary accent
- **Neon Cyan**: `#06B6D4` - Secondary accent
- **Mystic Purple**: `#8B5CF6` - Tertiary accent

### Animations
- **Float**: Floating orb animations (6s loop)
- **Glow Pulse**: Pulsing glow effects (2s loop)
- **Shimmer**: Loading shimmer effect
- **Parallax**: Scroll-based parallax effects
- **Card Hover**: 3D transform on hover
- **Typing Indicator**: Animated dots for AI typing

### Design Patterns
- **Glass Morphism**: Translucent cards with backdrop blur
- **Neon Borders**: Animated gradient borders
- **Gradient Text**: Color gradient text effects
- **Cyber Grid**: Animated background grid pattern

## API Integration

The frontend communicates with the backend through a centralized API client (`lib/api.ts`):

### Authentication
```typescript
import { authAPI } from '@/lib/api'

// Register
await authAPI.register({ name, email, password })

// Login
await authAPI.login({ email, password })

// Get current user
const user = await authAPI.getCurrentUser()

// Logout
await authAPI.logout()
```

### Chat
```typescript
import { chatAPI } from '@/lib/api'

// Send message (REST)
const response = await chatAPI.sendMessage(query, sessionId, filters)

// Stream chat (WebSocket)
const eventSource = chatAPI.streamChat(query, sessionId, filters)
```

### Search
```typescript
import { searchAPI } from '@/lib/api'

// Search notices
const results = await searchAPI.search(query, filters, limit)

// Get latest notices
const notices = await searchAPI.getLatestNotices(10)
```

## WebSocket Integration

The chat page uses WebSocket for real-time streaming responses:

```typescript
const websocket = new WebSocket(`${WS_URL}/ws/chat`)

websocket.onmessage = (event) => {
  const data = JSON.parse(event.data)

  if (data.type === 'token') {
    // Stream token received
  } else if (data.type === 'sources') {
    // Sources received
  } else if (data.type === 'done') {
    // Streaming complete
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket base URL | `ws://localhost:8000` |

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

```bash
npm run build
npm run start
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t kiit-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 kiit-frontend
```

## Performance Optimizations

- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Next.js font optimization
- **SSR/SSG**: Static generation where possible
- **API Caching**: Response caching with proper headers

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus indicators
- Color contrast (WCAG AA)

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new files
3. Add proper type definitions
4. Test on multiple screen sizes
5. Ensure accessibility standards

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub or contact the development team.

---

Built with ❤️ for KIIT students
