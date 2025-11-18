# KIIT University Chatbot - Replit Edition

## Overview
RAG-based chatbot for KIIT University students providing AI-powered assistance with information about courses, notices, and university details. Successfully migrated from Vercel to Replit.

## Recent Changes (November 18, 2025)
### Complete Migration to Replit Stack
- **Database**: Migrated from MongoDB to PostgreSQL (Replit built-in)
- **LLM**: Replaced Ollama (local) with OpenAI via Replit AI Integrations
- **Cache**: Replaced Redis with in-memory caching (cachetools)
- **Embeddings**: Simplified vector search using PostgreSQL storage
- **Deployment**: Optimized for Replit environment

### Key Features
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ OpenAI integration (no API key required - uses Replit credits)
- ✅ In-memory caching for performance
- ✅ Rate limiting middleware
- ✅ RAG (Retrieval Augmented Generation) for accurate responses
- ✅ Next.js frontend with modern UI
- ✅ FastAPI backend with async support
- ✅ Auto-seeding with basic KIIT information

## Tech Stack

### Frontend
- **Framework**: Next.js 14.0.3 with React 18.2.0
- **Styling**: Tailwind CSS with custom theme
- **Animations**: Framer Motion, React Particles
- **Forms**: React Hook Form with Zod validation
- **State**: Zustand
- **HTTP**: Axios
- **Port**: 5000 (configured for Replit)

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL via SQLAlchemy
- **LLM**: OpenAI GPT-4o-mini via Replit AI Integrations
- **Embeddings**: OpenAI text-embedding-3-small
- **Cache**: In-memory (cachetools)
- **Port**: 8000

## Project Structure

```
├── frontend/                 # Next.js frontend
│   ├── app/                 # App router pages
│   │   ├── chat/           # Chat interface
│   │   ├── login/          # Login page
│   │   ├── register/       # Registration page
│   │   └── page.tsx        # Landing page
│   ├── components/         # Reusable components
│   ├── lib/                # API client and utilities
│   └── .env.local          # Frontend environment variables
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── simple_main.py  # Main FastAPI application (Replit version)
│   │   ├── database.py     # SQLAlchemy models and database setup
│   │   ├── config.py       # Configuration management
│   │   ├── seed_data.py    # Database seeding with KIIT info
│   │   └── services/       # Service layer
│   │       ├── simple_llm_service.py    # OpenAI integration
│   │       ├── simple_cache.py          # In-memory cache
│   │       └── simple_search.py         # Search service
│   └── .env                # Backend environment variables
│
└── start.sh                # Startup script (launches both servers)
```

## Database Schema

### Tables
1. **notices** - KIIT notices and information
   - id, title, content, url, source_type, date, created_at

2. **courses** - KIIT courses and programs
   - id, name, code, description, department, duration, eligibility, created_at

3. **chat_history** - User chat sessions
   - id, session_id, role, content, timestamp

4. **embeddings** - Vector embeddings for search
   - id, content_id, content_type, text, embedding_vector, created_at

5. **users** - User accounts (for future auth)
   - id, name, email, password_hash, created_at

## Environment Variables

### Automatically Set by Replit
- `DATABASE_URL` - PostgreSQL connection string
- `AI_INTEGRATIONS_OPENAI_API_KEY` - OpenAI API key
- `AI_INTEGRATIONS_OPENAI_BASE_URL` - OpenAI base URL
- `REPLIT_DEV_DOMAIN` - Replit domain for the app

### Backend Configuration
All other configuration is in `backend/.env`:
- API host/port settings
- Rate limiting configuration
- Cache TTL settings
- CORS configuration

### Frontend Configuration
In `frontend/.env.local`:
- `NEXT_PUBLIC_API_URL` - Backend API URL (auto-set to Replit domain)

## API Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/chat` - Send chat message (RAG-enabled)
- `GET /api/search` - Search notices and courses
- `GET /api/courses` - Get all courses
- `GET /api/notices/latest` - Get latest notices

### Admin Endpoints
- `GET /api/admin/stats` - Database statistics

### Future Endpoints (Planned)
- `/api/auth/*` - Authentication endpoints
- `/api/chat/stream` - Streaming chat responses

## Development

### Starting the Application
```bash
bash start.sh
```

This automatically:
1. Checks for required services (PostgreSQL, OpenAI)
2. Starts FastAPI backend on port 8000
3. Starts Next.js frontend on port 5000
4. Seeds database if empty

### Database Operations

Initialize/reset database:
```bash
cd backend
python -c "from app.database import init_db; init_db()"
```

Seed basic KIIT data:
```bash
cd backend
python app/seed_data.py
```

### Testing Backend Directly
```bash
# Health check
curl http://localhost:8000/api/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is KIIT?","session_id":"test123"}'

# Get statistics
curl http://localhost:8000/api/admin/stats
```

## Data Sources

### Current Data (Basic Seed)
The application is seeded with basic KIIT information:
- 5 foundational notices (About KIIT, Location, Accreditation, Admissions, Facilities)
- 8 academic programs (B.Tech, CSE, ECE, ME, MBA, BCA, M.Tech, B.Sc)

### Future Data Sources
Users can expand the dataset by:
1. Adding more notices and courses directly to PostgreSQL
2. Implementing scrapers for official KIIT websites
3. Importing structured data from KIIT resources
4. Using the admin API to add new content

## Features

### Current Features
- ✅ Natural language chat interface with AI responses
- ✅ RAG-based search using PostgreSQL and OpenAI embeddings
- ✅ Course and notice browsing
- ✅ Session-based chat history
- ✅ Rate limiting and caching
- ✅ Responsive modern UI
- ✅ Health monitoring

### Future Enhancements (To-Do)
- [ ] User authentication system
- [ ] Advanced vector similarity search with FAISS/pgvector
- [ ] Streaming chat responses (SSE)
- [ ] Automated content scraping from KIIT websites
- [ ] Admin dashboard for content management
- [ ] User feedback and rating system
- [ ] Export chat history
- [ ] Multi-language support

## User Preferences
- **Development Style**: Pragmatic and efficient - prioritize working solutions
- **Code Organization**: Clean, modular structure with clear separation of concerns
- **Documentation**: Keep comprehensive documentation in replit.md
- **Testing**: Manual testing via curl and browser for now
- **Dependencies**: Prefer Replit-native services (PostgreSQL, AI Integrations) over external services

## Architecture Decisions

### Why PostgreSQL?
- Native Replit integration (no external setup)
- Reliable, ACID-compliant
- Future-ready for pgvector extension for better vector search
- Easier to manage than MongoDB in Replit environment

### Why OpenAI via Replit AI Integrations?
- No API key management required
- Costs billed to Replit credits
- Automatic credential rotation
- Better performance than local models (Ollama)
- Production-ready and maintained by Replit

### Why In-Memory Caching?
- Simpler than Redis for small-scale deployment
- No additional service dependencies
- Sufficient for current traffic levels
- Easy to upgrade to Redis later if needed

### Why Simplified Search?
- Keyword-based search works well for current dataset size
- Can be enhanced with vector similarity when dataset grows
- PostgreSQL full-text search available as next upgrade
- FAISS or pgvector can be added later for semantic search

## Known Issues & Limitations

### Current Limitations
1. **Limited Dataset**: Only basic KIIT information (5 notices, 8 courses)
   - Solution: User can add more data or implement scrapers

2. **Simple Search**: Keyword-based, not semantic
   - Solution: Can upgrade to vector similarity search later

3. **No Authentication**: Auth endpoints exist but not implemented
   - Solution: Implement JWT-based auth in future release

4. **In-Memory Cache**: Lost on restart
   - Solution: Acceptable for now, can add Redis if needed

### Non-Issues
- React hook warnings in browser console: These are deprecation warnings from `react-scroll-parallax` using `findDOMNode` in StrictMode. Not breaking errors.

## Deployment to Production

To deploy this application to production on Replit:

1. Click the "Publish" button in Replit
2. Choose deployment type:
   - **Autoscale**: Best for this stateless web app (recommended)
   - **VM**: If you need persistent connections
3. Replit will automatically:
   - Set up PostgreSQL for production
   - Configure OpenAI credentials
   - Scale as needed
   - Provide custom domain options

### Production Considerations
- Update `API_KEY` in backend/.env for security
- Review `CORS_ORIGINS` settings
- Monitor OpenAI usage (billed to Replit credits)
- Consider upgrading cache to Redis for high traffic
- Implement proper authentication before going live

## Support & Maintenance

### Logs and Debugging
- Frontend logs: Browser console
- Backend logs: Visible in workflow output
- Database errors: Check backend logs for SQLAlchemy errors

### Common Issues

**Backend not starting?**
- Check DATABASE_URL is set (Replit should do this automatically)
- Check OpenAI integration is configured
- Look at workflow logs for error messages

**Frontend can't reach backend?**
- Verify backend is running on port 8000
- Check .env.local has correct REPLIT_DEV_DOMAIN
- Try accessing http://localhost:8000/api/health directly

**Database issues?**
- Reinitialize: `python -c "from app.database import init_db; init_db()"`
- Reseed: `python app/seed_data.py`
- Check PostgreSQL is enabled in Replit

## Credits
- Original architecture: Vercel-based chatbot
- Migration to Replit: November 2025
- University: KIIT (Kalinga Institute of Industrial Technology)
- Location: Bhubaneswar, Odisha, India
