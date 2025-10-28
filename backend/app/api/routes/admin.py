"""
Admin API routes for system management and monitoring.
Requires API key authentication.
"""

from fastapi import APIRouter, HTTPException, Header, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime

from app.config import settings
from app.db.mongodb import get_collection

logger = logging.getLogger(__name__)

router = APIRouter()


class ScrapeRequest(BaseModel):
    """Request model for manual scrape triggers"""
    source: str  # "all", "general", "exam", "academic", "holiday"


class ScrapeResponse(BaseModel):
    """Response model for scrape request"""
    message: str
    task_id: Optional[str] = None


class AdminStatsResponse(BaseModel):
    """Response model for admin statistics"""
    total_notices: int
    notices_by_type: dict
    last_scrape: Optional[str]
    total_queries_today: int
    cache_hit_rate: float
    avg_response_time_ms: int


def verify_api_key(x_api_key: str = Header(...)):
    """
    Verify API key for admin endpoints.

    Args:
        x_api_key: API key from request header

    Raises:
        HTTPException if API key is invalid
    """
    if x_api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )


@router.post("/scrape", response_model=ScrapeResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(...)
):
    """
    Manually trigger scraping of KIIT sources.

    Args:
        request: ScrapeRequest with source type
        background_tasks: FastAPI background tasks
        x_api_key: API key for authentication

    Returns:
        ScrapeResponse with task information
    """
    # Verify API key
    verify_api_key(x_api_key)

    try:
        logger.info(f"Manual scrape triggered for source: {request.source}")

        # Add scraping task to background
        from app.services.scraper_service import get_scraper_service

        scraper = get_scraper_service()

        # Queue the scraping task
        if request.source == "all":
            background_tasks.add_task(scraper.scrape_all_sources)
        elif request.source == "general":
            background_tasks.add_task(scraper.scrape_general_notices)
        elif request.source == "exam":
            background_tasks.add_task(scraper.scrape_exam_notices)
        elif request.source == "academic":
            background_tasks.add_task(scraper.scrape_academic_calendar)
        elif request.source == "holiday":
            background_tasks.add_task(scraper.scrape_holiday_list)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source: {request.source}. Must be one of: all, general, exam, academic, holiday"
            )

        return ScrapeResponse(
            message=f"Scraping task queued for source: {request.source}",
            task_id=None  # Could use Celery task ID in production
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering scrape: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger scraping"
        )


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(x_api_key: str = Header(...)):
    """
    Get system statistics for admin dashboard.

    Args:
        x_api_key: API key for authentication

    Returns:
        AdminStatsResponse with system statistics
    """
    # Verify API key
    verify_api_key(x_api_key)

    try:
        # Get MongoDB collections
        notices_collection = get_collection('notices')
        daily_stats_collection = get_collection('daily_stats')

        # Total notices
        total_notices = notices_collection.count_documents({"is_latest": True})

        # Notices by type
        pipeline = [
            {"$match": {"is_latest": True}},
            {"$group": {
                "_id": "$source_type",
                "count": {"$sum": 1}
            }}
        ]
        type_counts = notices_collection.aggregate(pipeline)
        notices_by_type = {item['_id']: item['count'] for item in type_counts}

        # Last scrape time (from cache)
        from app.services.cache_service import get_cache_service

        cache_service = get_cache_service()
        last_scrape = None
        for source_type in ['general', 'exam', 'academic', 'holiday']:
            scrape_time = cache_service.get_scraper_last_run(source_type)
            if scrape_time:
                last_scrape = scrape_time if not last_scrape else max(last_scrape, scrape_time)

        # Today's stats
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_stats = daily_stats_collection.find_one({"date": today})

        total_queries_today = today_stats.get('total_queries', 0) if today_stats else 0
        cache_hit_rate = today_stats.get('cache_hit_rate', 0.0) if today_stats else 0.0
        avg_response_time_ms = today_stats.get('avg_response_time_ms', 0) if today_stats else 0

        return AdminStatsResponse(
            total_notices=total_notices,
            notices_by_type=notices_by_type,
            last_scrape=last_scrape,
            total_queries_today=total_queries_today,
            cache_hit_rate=cache_hit_rate,
            avg_response_time_ms=avg_response_time_ms
        )

    except Exception as e:
        logger.error(f"Error getting admin stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
