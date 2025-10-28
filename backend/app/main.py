"""
FastAPI main application.
Entry point for the KIIT ChatBot backend API.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging

from app.config import settings
from app.utils.logger import setup_logging
from app.db.mongodb import init_indexes, get_database
from app.db.faiss_store import get_index

# Import routers
from app.api.routes import chat, search, health, admin

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the startup and shutdown events.
    """
    # Startup
    logger.info("Starting KIIT ChatBot API...")

    try:
        # Initialize MongoDB indexes
        logger.info("Initializing MongoDB indexes...")
        init_indexes()

        # Load FAISS index
        logger.info("Loading FAISS index...")
        get_index()

        # Preload embedding model
        logger.info("Preloading embedding model...")
        from app.services.embedding_service import get_model
        get_model()

        logger.info("KIIT ChatBot API started successfully")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    yield  # Application runs

    # Shutdown
    logger.info("Shutting down KIIT ChatBot API...")

    try:
        # Close database connections
        from app.db.mongodb import close_connection
        from app.db.redis_client import close_connections

        close_connection()
        close_connections()

        logger.info("KIIT ChatBot API shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="KIIT ChatBot API",
    description="RAG-based chatbot for KIIT University information",
    version="1.0.0",
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


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()

    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time
    duration_ms = int(duration * 1000)

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration_ms}ms - "
        f"Client: {client_ip}"
    )

    # Add custom headers
    response.headers["X-Process-Time"] = str(duration_ms)

    return response


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting based on IP address"""
    # Skip rate limiting for health check and docs
    if request.url.path in ["/api/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    try:
        from app.services.cache_service import get_cache_service

        cache_service = get_cache_service()
        is_allowed, count = cache_service.check_rate_limit(
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

    except Exception as e:
        logger.error(f"Error in rate limiting: {e}")
        # On error, allow request

    return await call_next(request)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid request data",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please try again later."
        }
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KIIT ChatBot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# Enable Prometheus metrics (optional)
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
    logger.info("Prometheus metrics enabled at /metrics")

except ImportError:
    logger.info("Prometheus instrumentation not available (prometheus-fastapi-instrumentator not installed)")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
