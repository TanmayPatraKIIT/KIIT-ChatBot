"""
Simplified FastAPI main application for Replit
Uses PostgreSQL, OpenAI, and in-memory caching
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, SessionLocal, Notice, Course, ChatHistory, Embedding
from app.services.llm_service import llm_service
from app.services.cache import cache
from app.services.search import search_service
from pydantic import BaseModel
from typing import Optional
import json

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting KIIT ChatBot API (Replit Edition)...")
    
    try:
        # Initialize database
        logger.info("Initializing PostgreSQL database...")
        init_db()
        
        # Seed data if needed
        db = SessionLocal()
        notice_count = db.query(Notice).count()
        db.close()
        
        if notice_count == 0:
            logger.info("Seeding database with basic KIIT data...")
            from app.seed_data import seed_basic_data
            seed_basic_data()
        
        logger.info("KIIT ChatBot API started successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down KIIT ChatBot API...")


# Create FastAPI app
app = FastAPI(
    title="KIIT ChatBot API",
    description="RAG-based chatbot for KIIT University (Replit Edition)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting"""
    if request.url.path in ["/api/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    is_allowed, count = cache.check_rate_limit(
        client_ip,
        limit=settings.RATE_LIMIT_PER_MINUTE,
        window=60
    )
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }
        )
    
    return await call_next(request)


# Pydantic models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KIIT ChatBot API (Replit Edition)",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "postgresql",
        "llm": "openai",
        "cache": "in-memory"
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with RAG"""
    try:
        # Search for relevant information
        results = search_service.search_all(request.query, limit=3)
        
        # Build context from search results
        context_parts = []
        sources = []
        
        for result in results:
            if result["type"] == "notice":
                context_parts.append(f"Title: {result['title']}\n{result['content']}")
                sources.append({
                    "title": result["title"],
                    "url": result.get("url", ""),
                    "type": "notice"
                })
            elif result["type"] == "course":
                context_parts.append(f"Course: {result['name']} ({result['code']})\n{result['description']}")
                sources.append({
                    "title": result["name"],
                    "code": result["code"],
                    "type": "course"
                })
        
        context = "\n\n".join(context_parts)
        
        # Generate response using LLM
        response_text = llm_service.generate_response(request.query, context)
        
        # Save to chat history
        if request.session_id:
            db = SessionLocal()
            try:
                db.add(ChatHistory(
                    session_id=request.session_id,
                    role="user",
                    content=request.query
                ))
                db.add(ChatHistory(
                    session_id=request.session_id,
                    role="assistant",
                    content=response_text
                ))
                db.commit()
            except Exception as e:
                logger.error(f"Error saving chat history: {e}")
            finally:
                db.close()
        
        return {
            "response": response_text,
            "sources": sources,
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search(query: str, limit: int = 10):
    """Search endpoint"""
    try:
        results = search_service.search_all(query, limit)
        return {
            "results": results,
            "total": len(results),
            "query": query
        }
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses")
async def get_courses(limit: int = 20):
    """Get all courses"""
    db = SessionLocal()
    try:
        courses = db.query(Course).limit(limit).all()
        return [{
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "description": c.description,
            "department": c.department,
            "duration": c.duration,
            "eligibility": c.eligibility
        } for c in courses]
    finally:
        db.close()


@app.get("/api/notices/latest")
async def get_latest_notices(limit: int = 10):
    """Get latest notices"""
    db = SessionLocal()
    try:
        notices = db.query(Notice).order_by(Notice.created_at.desc()).limit(limit).all()
        return [{
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "url": n.url,
            "source_type": n.source_type,
            "date": n.date.isoformat() if n.date else None
        } for n in notices]
    finally:
        db.close()


@app.get("/api/admin/stats")
async def get_stats():
    """Get database statistics"""
    db = SessionLocal()
    try:
        return {
            "notices": db.query(Notice).count(),
            "courses": db.query(Course).count(),
            "chat_history": db.query(ChatHistory).count(),
            "embeddings": db.query(Embedding).count()
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
