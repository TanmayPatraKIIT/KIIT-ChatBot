"""
Search API routes for browsing and filtering notices.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
import logging
from datetime import datetime

from app.models.notice import NoticeResponse, NoticeSearchResponse, NoticeType
from app.db.mongodb import get_collection
from app.services.embedding_service import generate_embedding
from app.db.faiss_store import search, get_notice_ids

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/notices", response_model=NoticeSearchResponse)
async def search_notices(
    q: Optional[str] = Query(None, description="Search query"),
    type: Optional[NoticeType] = Query(None, description="Notice type filter"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=50, description="Results limit"),
    offset: int = Query(0, ge=0, description="Results offset")
):
    """
    Search notices by keyword or filters.

    Args:
        q: Search query (semantic search if provided)
        type: Filter by notice type
        from_date: Filter by start date
        to_date: Filter by end date
        limit: Maximum results to return
        offset: Results offset for pagination

    Returns:
        NoticeSearchResponse with matching notices
    """
    try:
        notices_collection = get_collection('notices')

        if q:
            # Semantic search using FAISS
            logger.info(f"Semantic search for: {q}")

            # Generate query embedding
            query_embedding = generate_embedding(q)

            # Search FAISS (get more results for filtering)
            distances, indices = search(query_embedding, top_k=min(limit * 3, 100))

            # Get MongoDB IDs
            notice_ids = get_notice_ids(indices)

            if not notice_ids:
                return NoticeSearchResponse(total=0, notices=[])

            # Build MongoDB query
            mongo_query = {
                '_id': {'$in': notice_ids},
                'is_latest': True
            }

        else:
            # Regular filtered search
            mongo_query = {'is_latest': True}

        # Apply filters
        if type:
            mongo_query['source_type'] = type

        if from_date or to_date:
            date_filter = {}
            if from_date:
                try:
                    from_dt = datetime.fromisoformat(from_date)
                    date_filter['$gte'] = from_dt
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid from_date format. Use YYYY-MM-DD"
                    )

            if to_date:
                try:
                    to_dt = datetime.fromisoformat(to_date)
                    date_filter['$lte'] = to_dt
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid to_date format. Use YYYY-MM-DD"
                    )

            if date_filter:
                mongo_query['date_published'] = date_filter

        # Get total count
        total = notices_collection.count_documents(mongo_query)

        # Fetch notices with pagination
        notices_cursor = notices_collection.find(mongo_query).sort('date_published', -1).skip(offset).limit(limit)

        notices = []
        for notice_doc in notices_cursor:
            notice_response = NoticeResponse(
                id=str(notice_doc['_id']),
                title=notice_doc['title'],
                excerpt=notice_doc['content'][:150] + "..." if len(notice_doc['content']) > 150 else notice_doc['content'],
                date=notice_doc['date_published'].isoformat(),
                type=notice_doc['source_type'],
                url=notice_doc['source_url']
            )
            notices.append(notice_response)

        logger.info(f"Found {len(notices)} notices (total: {total})")

        return NoticeSearchResponse(
            total=total,
            notices=notices
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching notices: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search notices"
        )


@router.get("/recent", response_model=NoticeSearchResponse)
async def get_recent_notices(
    type: Optional[NoticeType] = Query(None, description="Notice type filter"),
    limit: int = Query(10, ge=1, le=20, description="Results limit")
):
    """
    Get most recent notices.

    Args:
        type: Optional filter by notice type
        limit: Maximum results to return

    Returns:
        NoticeSearchResponse with recent notices
    """
    try:
        notices_collection = get_collection('notices')

        # Build query
        mongo_query = {'is_latest': True}
        if type:
            mongo_query['source_type'] = type

        # Get total count
        total = notices_collection.count_documents(mongo_query)

        # Fetch recent notices
        notices_cursor = notices_collection.find(mongo_query).sort('date_published', -1).limit(limit)

        notices = []
        for notice_doc in notices_cursor:
            notice_response = NoticeResponse(
                id=str(notice_doc['_id']),
                title=notice_doc['title'],
                excerpt=notice_doc['content'][:150] + "..." if len(notice_doc['content']) > 150 else notice_doc['content'],
                date=notice_doc['date_published'].isoformat(),
                type=notice_doc['source_type'],
                url=notice_doc['source_url']
            )
            notices.append(notice_response)

        logger.info(f"Retrieved {len(notices)} recent notices")

        return NoticeSearchResponse(
            total=total,
            notices=notices
        )

    except Exception as e:
        logger.error(f"Error getting recent notices: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent notices"
        )
