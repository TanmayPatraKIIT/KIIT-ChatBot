"""
Health check endpoint for monitoring system status.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    services: Dict[str, str]
    stats: Dict[str, any]


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    Returns status of all services and basic statistics.
    """
    services_status = {}
    stats = {}

    # Check MongoDB
    try:
        from app.db.mongodb import get_database

        db = get_database()
        db.command('ping')
        services_status["mongodb"] = "connected"

        # Get notice count
        stats["total_notices"] = db.notices.count_documents({"is_latest": True})

    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        services_status["mongodb"] = "disconnected"
        stats["total_notices"] = 0

    # Check Redis
    try:
        from app.db.redis_client import get_cache_client

        redis_client = get_cache_client()
        redis_client.ping()
        services_status["redis"] = "connected"

    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        services_status["redis"] = "disconnected"

    # Check FAISS
    try:
        from app.db.faiss_store import get_index_stats

        faiss_stats = get_index_stats()
        services_status["faiss"] = "loaded"
        stats["faiss_index_size"] = faiss_stats.get("total_vectors", 0)

    except Exception as e:
        logger.error(f"FAISS health check failed: {e}")
        services_status["faiss"] = "not_loaded"
        stats["faiss_index_size"] = 0

    # Check LLM
    try:
        from app.services.llm_service import get_llm_service

        llm_service = get_llm_service()
        if llm_service.is_available():
            services_status["llm"] = "available"
        else:
            services_status["llm"] = "unavailable"

    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        services_status["llm"] = "unavailable"

    # Determine overall status
    all_healthy = all(
        status in ["connected", "loaded", "available"]
        for status in services_status.values()
    )
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        services=services_status,
        stats=stats
    )
