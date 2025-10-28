"""
Celery background task for scraping, indexing, and maintenance.
"""

from celery import Task
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app.workers.celery_app import celery_app
from app.db.mongodb import get_collection
from app.db.faiss_store import rebuild_index, save_index
from app.services.scraper_service import get_scraper_service
from app.services.embedding_service import get_embedding_service, combine_text_for_embedding
from app.services.cache_service import get_cache_service
from app.utils.hash_utils import generate_content_hash
from app.utils.date_parser import get_current_datetime, extract_dates_from_text

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callbacks for logging"""

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {self.name} [{task_id}] succeeded")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {self.name} [{task_id}] failed: {exc}")


@celery_app.task(base=CallbackTask, name="app.workers.tasks.scrape_all_sources")
def scrape_all_sources():
    """
    Scrape all KIIT data sources and update database.
    Runs every 6 hours via Celery Beat.
    """
    logger.info("Starting scheduled scrape of all sources")

    try:
        # Get services
        scraper = get_scraper_service()
        embedding_service = get_embedding_service()
        cache_service = get_cache_service()

        # Get MongoDB collection
        notices_collection = get_collection('notices')

        # Scrape all sources
        results = scraper.scrape_all_sources()

        # Statistics
        stats = {
            'total_scraped': 0,
            'new_notices': 0,
            'updated_notices': 0,
            'unchanged_notices': 0,
            'by_type': {}
        }

        # Process each source type
        for source_type, notices in results.items():
            logger.info(f"Processing {len(notices)} notices from {source_type}")

            new_count = 0
            updated_count = 0
            unchanged_count = 0

            for notice in notices:
                # Generate content hash
                content_hash = generate_content_hash(notice.title + notice.content)

                # Check if notice already exists
                existing = notices_collection.find_one({
                    'content_hash': content_hash,
                    'source_type': source_type
                })

                if existing:
                    # Notice unchanged
                    unchanged_count += 1
                    continue

                # Check if this is an update to existing notice
                existing_by_title = notices_collection.find_one({
                    'title': notice.title,
                    'source_type': source_type,
                    'is_latest': True
                })

                if existing_by_title:
                    # Update existing notice
                    # Mark old version as not latest
                    notices_collection.update_one(
                        {'_id': existing_by_title['_id']},
                        {'$set': {'is_latest': False}}
                    )
                    version = existing_by_title.get('version', 1) + 1
                    previous_version_id = str(existing_by_title['_id'])
                    updated_count += 1
                else:
                    # New notice
                    version = 1
                    previous_version_id = None
                    new_count += 1

                # Extract dates from content
                extracted_dates = extract_dates_from_text(notice.content)

                # Create notice document
                notice_doc = {
                    'title': notice.title,
                    'content': notice.content,
                    'date_published': notice.date_published,
                    'date_scraped': get_current_datetime(),
                    'source_url': notice.source_url,
                    'source_type': notice.source_type,
                    'content_hash': content_hash,
                    'attachments': notice.attachments,
                    'metadata': {
                        'word_count': len(notice.content.split()),
                        'has_dates': len(extracted_dates) > 0,
                        'extracted_dates': extracted_dates,
                        'language': 'en'
                    },
                    'version': version,
                    'is_latest': True,
                    'previous_version_id': previous_version_id
                }

                # Insert notice
                result = notices_collection.insert_one(notice_doc)
                notice_id = str(result.inserted_id)

                # Generate embedding and add to FAISS
                try:
                    combined_text = combine_text_for_embedding(notice.title, notice.content)
                    embedding_service.embed_notice(notice_id, notice.title, notice.content)
                except Exception as e:
                    logger.error(f"Failed to embed notice {notice_id}: {e}")

            # Update statistics
            stats['total_scraped'] += len(notices)
            stats['new_notices'] += new_count
            stats['updated_notices'] += updated_count
            stats['unchanged_notices'] += unchanged_count
            stats['by_type'][source_type] = {
                'total': len(notices),
                'new': new_count,
                'updated': updated_count
            }

            # Update last scrape time
            cache_service.set_scraper_last_run(source_type, get_current_datetime().isoformat())

        # Invalidate response cache for updated types
        if stats['new_notices'] > 0 or stats['updated_notices'] > 0:
            cache_service.invalidate_all_response_cache()

        logger.info(f"Scraping completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error in scrape_all_sources task: {e}", exc_info=True)
        raise


@celery_app.task(base=CallbackTask, name="app.workers.tasks.rebuild_faiss_index")
def rebuild_faiss_index():
    """
    Rebuild FAISS index from scratch.
    Runs weekly on Sunday at 2 AM.
    """
    logger.info("Starting FAISS index rebuild")

    try:
        # Get MongoDB collection
        notices_collection = get_collection('notices')
        embedding_service = get_embedding_service()

        # Fetch all latest notices
        notices = list(notices_collection.find({'is_latest': True}))

        logger.info(f"Rebuilding index for {len(notices)} notices")

        # Prepare data for batch embedding
        notice_data = [
            (
                str(notice['_id']),
                notice['title'],
                notice['content']
            )
            for notice in notices
        ]

        # Generate embeddings and rebuild index
        if notice_data:
            embedding_service.embed_notices_batch(notice_data)

        logger.info("FAISS index rebuild completed")
        return {"notices_indexed": len(notices)}

    except Exception as e:
        logger.error(f"Error in rebuild_faiss_index task: {e}", exc_info=True)
        raise


@celery_app.task(base=CallbackTask, name="app.workers.tasks.cleanup_old_versions")
def cleanup_old_versions():
    """
    Clean up old notice versions, keeping only last 5 versions.
    Runs monthly on the 1st at 3 AM.
    """
    logger.info("Starting cleanup of old notice versions")

    try:
        notices_collection = get_collection('notices')

        # Find all notices with versions > 5
        pipeline = [
            {'$match': {'version': {'$exists': True}}},
            {'$group': {
                '_id': {'title': '$title', 'source_type': '$source_type'},
                'versions': {'$push': {'id': '$_id', 'version': '$version'}},
                'count': {'$sum': 1}
            }},
            {'$match': {'count': {'$gt': 5}}}
        ]

        notices_with_many_versions = list(notices_collection.aggregate(pipeline))

        deleted_count = 0

        for notice_group in notices_with_many_versions:
            # Sort versions descending
            versions = sorted(notice_group['versions'], key=lambda x: x['version'], reverse=True)

            # Keep top 5, delete rest
            to_delete = [v['id'] for v in versions[5:]]

            if to_delete:
                result = notices_collection.delete_many({'_id': {'$in': to_delete}})
                deleted_count += result.deleted_count

        logger.info(f"Cleanup completed: deleted {deleted_count} old versions")
        return {"deleted_versions": deleted_count}

    except Exception as e:
        logger.error(f"Error in cleanup_old_versions task: {e}", exc_info=True)
        raise


@celery_app.task(base=CallbackTask, name="app.workers.tasks.generate_daily_stats")
def generate_daily_stats():
    """
    Generate daily statistics and store in database.
    Runs daily at midnight.
    """
    logger.info("Generating daily statistics")

    try:
        # Get collections
        chat_history_collection = get_collection('chat_history')
        daily_stats_collection = get_collection('daily_stats')
        cache_service = get_cache_service()

        # Get yesterday's date
        yesterday = (datetime.utcnow() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        today = yesterday + timedelta(days=1)

        # Count queries from yesterday
        total_queries = chat_history_collection.count_documents({
            'last_updated': {
                '$gte': yesterday,
                '$lt': today
            }
        })

        # Count unique sessions
        unique_sessions = len(chat_history_collection.distinct('session_id', {
            'last_updated': {
                '$gte': yesterday,
                '$lt': today
            }
        }))

        # Get popular queries
        popular_queries = cache_service.get_popular_queries(10)

        # Calculate average response time (if tracked)
        # For now, use placeholder
        avg_response_time_ms = 450
        cache_hit_rate = 0.65

        # Create stats document
        stats_doc = {
            'date': yesterday,
            'total_queries': total_queries,
            'unique_sessions': unique_sessions,
            'avg_response_time_ms': avg_response_time_ms,
            'cache_hit_rate': cache_hit_rate,
            'popular_queries': [
                {'query': q, 'count': int(c)} for q, c in popular_queries
            ],
            'generated_at': datetime.utcnow()
        }

        # Store in database
        daily_stats_collection.update_one(
            {'date': yesterday},
            {'$set': stats_doc},
            upsert=True
        )

        logger.info(f"Daily stats generated for {yesterday.date()}: {total_queries} queries")
        return stats_doc

    except Exception as e:
        logger.error(f"Error in generate_daily_stats task: {e}", exc_info=True)
        raise
