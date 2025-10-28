"""
MongoDB database connection and operations.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global MongoDB client
_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_client() -> MongoClient:
    """Get MongoDB client, creating if necessary"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000
            )
            # Verify connection
            _client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    return _client


def get_database() -> Database:
    """Get MongoDB database"""
    global _database
    if _database is None:
        client = get_client()
        _database = client[settings.MONGODB_DB_NAME]
        logger.info(f"Using database: {settings.MONGODB_DB_NAME}")
    return _database


def get_collection(collection_name: str) -> Collection:
    """Get MongoDB collection"""
    db = get_database()
    return db[collection_name]


def init_indexes():
    """Initialize MongoDB indexes for optimal query performance"""
    db = get_database()

    # Notices collection indexes
    notices = db.notices
    notices.create_index([("source_type", ASCENDING), ("date_published", DESCENDING)])
    notices.create_index([("content_hash", ASCENDING)])
    notices.create_index([("is_latest", ASCENDING), ("date_published", DESCENDING)])
    notices.create_index([("faiss_index_id", ASCENDING)])
    logger.info("Created indexes on 'notices' collection")

    # Chat history collection indexes
    chat_history = db.chat_history
    chat_history.create_index([("session_id", ASCENDING), ("last_updated", DESCENDING)])
    chat_history.create_index([("created_at", ASCENDING)])
    logger.info("Created indexes on 'chat_history' collection")

    # Daily stats collection indexes
    daily_stats = db.daily_stats
    daily_stats.create_index([("date", DESCENDING)])
    logger.info("Created indexes on 'daily_stats' collection")


def close_connection():
    """Close MongoDB connection"""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")
