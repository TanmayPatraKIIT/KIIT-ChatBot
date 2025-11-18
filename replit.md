# KIIT ChatBot - Replit Migration

## Project Overview
This is a full-stack RAG-based chatbot application for KIIT University information, migrated from Vercel to Replit.

**Tech Stack:**
- Frontend: Next.js 14 (React, TypeScript, TailwindCSS)
- Backend: FastAPI (Python 3.11)
- Database: MongoDB
- Cache: Redis
- Vector Store: FAISS
- LLM: Ollama (configurable)

## Current Status
✅ Frontend configured and running on port 5000
✅ Backend dependencies installed
⚠️ Backend requires external services to run

## Migration Completed
1. ✅ Installed Node.js 20 and Python 3.11
2. ✅ Configured Next.js to run on port 5000 with 0.0.0.0 binding (required for Replit)
3. ✅ Added cache control headers to prevent iframe caching issues
4. ✅ Set up environment variables for development
5. ✅ Created workflow for the application
6. ✅ Frontend is accessible and running

## Required Services for Backend

The backend requires these services to be configured before it can run:

### 1. MongoDB Database
The application uses MongoDB to store:
- User accounts and authentication data
- Chat history and sessions
- Notice/document metadata

**Options:**
- Use Replit's built-in PostgreSQL (would require code changes)
- Connect to external MongoDB service (MongoDB Atlas free tier)
- Set up MongoDB locally

### 2. Redis Cache
Used for:
- Rate limiting
- Session caching
- Temporary data storage

**Options:**
- Connect to external Redis service (Redis Cloud free tier)
- Use alternative caching (would require code changes)

### 3. LLM Provider
Currently configured for Ollama, but requires:
- LLM_PROVIDER: Service provider (ollama, openai, etc.)
- LLM_BASE_URL: API endpoint
- LLM_MODEL: Model name

**Options:**
- Use OpenAI API (set OPENAI_API_KEY)
- Use other LLM services
- Run Ollama (requires significant resources)

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://[your-repl-url]:8000
NEXT_PUBLIC_WS_URL=wss://[your-repl-url]:8000
```

### Backend (.env)
```
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kiit_chatbot

# Cache
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3:8b

# Security
API_KEY=your_secret_api_key_here
CORS_ORIGINS=https://[your-repl-domain]
```

## Next Steps

To get the full application running:

1. **Set up MongoDB**
   - Option A: Use MongoDB Atlas (free tier available)
   - Option B: Migrate to Replit's PostgreSQL database

2. **Set up Redis**
   - Option A: Use Redis Cloud (free tier available)
   - Option B: Use alternative caching solution

3. **Configure LLM**
   - Recommended: Use OpenAI API for simplicity
   - Alternative: Configure another LLM service

4. **Update environment variables**
   - Set the secret environment variables in Replit
   - Update CORS_ORIGINS with your Replit domain

5. **Update start script**
   - Modify `start.sh` to start both frontend and backend

## Architecture Notes

- Frontend runs on port 5000 (publicly accessible)
- Backend runs on port 8000 (internal)
- Separation of frontend/backend ensures security
- CORS configured to only allow requests from the Replit domain

## Known Issues

1. Backend dependencies for ML/AI (sentence-transformers, faiss) are heavy
2. Application requires significant memory for embedding models
3. Some npm packages are deprecated (tsparticles v2 -> v3 migration recommended)

## Recent Changes (Nov 18, 2025)

- Migrated from Vercel to Replit
- Configured Next.js for Replit environment (port 5000, 0.0.0.0 binding)
- Added cache control headers for iframe compatibility
- Set up basic environment configuration
- Created workflow for application startup
