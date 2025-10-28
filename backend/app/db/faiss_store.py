"""
FAISS vector store for semantic search.
Handles embedding indexing and similarity search.
"""

import faiss
import numpy as np
import json
import os
from typing import List, Tuple, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global FAISS index and mapping
_index: Optional[faiss.IndexFlatL2] = None
_mapping: dict = {}  # Maps FAISS index position to MongoDB notice ID


def init_index(dimension: int = 768) -> faiss.IndexFlatL2:
    """Initialize FAISS index"""
    global _index
    _index = faiss.IndexFlatL2(dimension)
    logger.info(f"Initialized FAISS IndexFlatL2 with dimension {dimension}")
    return _index


def get_index() -> faiss.IndexFlatL2:
    """Get FAISS index, loading from disk if exists, otherwise create new"""
    global _index, _mapping

    if _index is not None:
        return _index

    # Try to load from disk
    if os.path.exists(settings.FAISS_INDEX_PATH):
        try:
            _index = faiss.read_index(settings.FAISS_INDEX_PATH)
            logger.info(f"Loaded FAISS index from {settings.FAISS_INDEX_PATH}")

            # Load mapping
            if os.path.exists(settings.FAISS_MAPPING_PATH):
                with open(settings.FAISS_MAPPING_PATH, 'r') as f:
                    _mapping = json.load(f)
                logger.info(f"Loaded FAISS mapping with {len(_mapping)} entries")
            else:
                logger.warning("FAISS mapping file not found, starting with empty mapping")
                _mapping = {}

            return _index
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            logger.info("Creating new FAISS index")

    # Create new index
    _index = init_index()
    return _index


def add_embedding(notice_id: str, embedding: np.ndarray) -> int:
    """
    Add embedding to FAISS index.

    Args:
        notice_id: MongoDB notice ID
        embedding: Embedding vector (768-dimensional)

    Returns:
        FAISS index position
    """
    global _mapping
    index = get_index()

    # Ensure embedding is correct shape
    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)

    # Add to FAISS index
    index.add(embedding.astype('float32'))

    # Get the position (last index)
    position = index.ntotal - 1

    # Update mapping
    _mapping[str(position)] = notice_id

    logger.debug(f"Added embedding for notice {notice_id} at position {position}")

    return position


def batch_add_embeddings(notice_ids: List[str], embeddings: np.ndarray) -> List[int]:
    """
    Add multiple embeddings to FAISS index.

    Args:
        notice_ids: List of MongoDB notice IDs
        embeddings: Array of embedding vectors (n, 768)

    Returns:
        List of FAISS index positions
    """
    global _mapping
    index = get_index()

    # Get current count
    start_position = index.ntotal

    # Add embeddings
    index.add(embeddings.astype('float32'))

    # Update mappings
    positions = []
    for i, notice_id in enumerate(notice_ids):
        position = start_position + i
        _mapping[str(position)] = notice_id
        positions.append(position)

    logger.info(f"Added {len(notice_ids)} embeddings to FAISS index")

    return positions


def search(query_embedding: np.ndarray, top_k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Search FAISS index for similar vectors.

    Args:
        query_embedding: Query vector (768-dimensional)
        top_k: Number of results to return

    Returns:
        Tuple of (distances, indices)
        distances: L2 distances to nearest neighbors
        indices: FAISS index positions of nearest neighbors
    """
    index = get_index()

    # Ensure query is correct shape
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    # Search
    distances, indices = index.search(query_embedding.astype('float32'), top_k)

    # Return first row (single query)
    return distances[0], indices[0]


def get_notice_ids(faiss_indices: np.ndarray) -> List[str]:
    """
    Convert FAISS indices to MongoDB notice IDs.

    Args:
        faiss_indices: Array of FAISS index positions

    Returns:
        List of MongoDB notice IDs
    """
    global _mapping
    notice_ids = []
    for idx in faiss_indices:
        idx_str = str(int(idx))
        if idx_str in _mapping:
            notice_ids.append(_mapping[idx_str])
        else:
            logger.warning(f"FAISS index {idx} not found in mapping")
    return notice_ids


def save_index():
    """Save FAISS index and mapping to disk"""
    global _index, _mapping

    if _index is None:
        logger.warning("No FAISS index to save")
        return

    try:
        # Ensure directories exist
        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)

        # Save index
        faiss.write_index(_index, settings.FAISS_INDEX_PATH)
        logger.info(f"Saved FAISS index to {settings.FAISS_INDEX_PATH}")

        # Save mapping
        with open(settings.FAISS_MAPPING_PATH, 'w') as f:
            json.dump(_mapping, f)
        logger.info(f"Saved FAISS mapping to {settings.FAISS_MAPPING_PATH}")

    except Exception as e:
        logger.error(f"Failed to save FAISS index: {e}")
        raise


def get_index_stats() -> dict:
    """Get FAISS index statistics"""
    index = get_index()
    return {
        "total_vectors": index.ntotal,
        "dimension": index.d,
        "is_trained": index.is_trained,
        "mapping_size": len(_mapping)
    }


def rebuild_index(notice_embeddings: List[Tuple[str, np.ndarray]]):
    """
    Rebuild FAISS index from scratch.

    Args:
        notice_embeddings: List of (notice_id, embedding) tuples
    """
    global _index, _mapping

    logger.info(f"Rebuilding FAISS index with {len(notice_embeddings)} embeddings")

    # Create new index
    _index = init_index()
    _mapping = {}

    # Add all embeddings
    if notice_embeddings:
        notice_ids = [item[0] for item in notice_embeddings]
        embeddings = np.array([item[1] for item in notice_embeddings])
        batch_add_embeddings(notice_ids, embeddings)

    # Save to disk
    save_index()

    logger.info("FAISS index rebuild completed")
