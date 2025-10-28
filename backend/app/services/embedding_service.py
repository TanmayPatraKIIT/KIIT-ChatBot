"""
Embedding service for generating vector embeddings using sentence-transformers.
Supports semantic search by converting text to dense vector representations.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Union
import re
from bs4 import BeautifulSoup
import logging

from app.config import settings
from app.db.faiss_store import add_embedding, batch_add_embeddings, save_index

logger = logging.getLogger(__name__)

# Global model instance (singleton pattern)
_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    """
    Get the embedding model, loading if necessary.
    Uses singleton pattern to load model only once.

    Returns:
        SentenceTransformer model instance
    """
    global _model
    if _model is None:
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            _model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE
            )
            logger.info(f"Model loaded successfully. Dimension: {_model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    return _model


def preprocess_text(text: str) -> str:
    """
    Preprocess text before embedding generation.

    Steps:
    1. Remove HTML tags
    2. Normalize whitespace
    3. Remove special characters (keep alphanumeric and basic punctuation)
    4. Convert to lowercase

    Args:
        text: Raw text content

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove extra special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)

    # Convert to lowercase for consistency
    text = text.lower()

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_tokens: int = 384) -> str:
    """
    Truncate text to maximum token length.
    Rough approximation: 1 token ≈ 4 characters

    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens (default 384 for model limit)

    Returns:
        Truncated text
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text

    # Truncate at word boundary
    truncated = text[:max_chars]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]

    logger.debug(f"Truncated text from {len(text)} to {len(truncated)} characters")
    return truncated


def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding vector for single text.

    Args:
        text: Input text

    Returns:
        Embedding vector (768-dimensional numpy array)
    """
    if not text:
        logger.warning("Empty text provided for embedding generation")
        return np.zeros(768, dtype=np.float32)

    try:
        # Preprocess text
        cleaned_text = preprocess_text(text)

        # Truncate to model's max length
        truncated_text = truncate_text(cleaned_text, max_tokens=384)

        if not truncated_text:
            logger.warning("Text became empty after preprocessing")
            return np.zeros(768, dtype=np.float32)

        # Generate embedding
        model = get_model()
        embedding = model.encode(truncated_text, convert_to_numpy=True)

        # Ensure correct shape
        if embedding.ndim == 1:
            return embedding.astype(np.float32)
        else:
            return embedding.flatten().astype(np.float32)

    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def batch_generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings for multiple texts efficiently.

    Args:
        texts: List of input texts
        batch_size: Number of texts to process at once (default 32)

    Returns:
        Array of embeddings with shape (n, 768)
    """
    if not texts:
        return np.array([]).reshape(0, 768)

    try:
        # Preprocess all texts
        cleaned_texts = [preprocess_text(text) for text in texts]

        # Truncate all texts
        truncated_texts = [truncate_text(text, max_tokens=384) for text in cleaned_texts]

        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(truncated_texts):
            if text:
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            logger.warning("All texts became empty after preprocessing")
            return np.zeros((len(texts), 768), dtype=np.float32)

        # Generate embeddings in batches
        model = get_model()
        embeddings = model.encode(
            valid_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(valid_texts) > 100
        )

        # Create full embeddings array with zeros for invalid texts
        full_embeddings = np.zeros((len(texts), 768), dtype=np.float32)
        for i, idx in enumerate(valid_indices):
            full_embeddings[idx] = embeddings[i]

        logger.info(f"Generated {len(texts)} embeddings in batches of {batch_size}")
        return full_embeddings

    except Exception as e:
        logger.error(f"Error in batch embedding generation: {e}")
        raise


def embed_and_index_notice(notice_id: str, text: str) -> int:
    """
    Generate embedding for notice and add to FAISS index.

    Args:
        notice_id: MongoDB notice ID
        text: Notice content (title + content combined recommended)

    Returns:
        FAISS index position
    """
    try:
        # Generate embedding
        embedding = generate_embedding(text)

        # Add to FAISS index
        position = add_embedding(notice_id, embedding)

        logger.debug(f"Embedded and indexed notice {notice_id} at position {position}")
        return position

    except Exception as e:
        logger.error(f"Error embedding and indexing notice {notice_id}: {e}")
        raise


def embed_and_index_notices_batch(
    notice_data: List[tuple]
) -> List[int]:
    """
    Generate embeddings for multiple notices and add to FAISS index.

    Args:
        notice_data: List of (notice_id, text) tuples

    Returns:
        List of FAISS index positions
    """
    try:
        if not notice_data:
            return []

        # Separate IDs and texts
        notice_ids = [item[0] for item in notice_data]
        texts = [item[1] for item in notice_data]

        # Generate embeddings in batch
        embeddings = batch_generate_embeddings(texts)

        # Add to FAISS index in batch
        positions = batch_add_embeddings(notice_ids, embeddings)

        logger.info(f"Embedded and indexed {len(notice_data)} notices")

        # Save index to disk
        save_index()

        return positions

    except Exception as e:
        logger.error(f"Error in batch embedding and indexing: {e}")
        raise


def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings.

    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector

    Returns:
        Cosine similarity score (0 to 1, higher is more similar)
    """
    try:
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)

        return float(similarity)

    except Exception as e:
        logger.error(f"Error computing similarity: {e}")
        return 0.0


def get_embedding_stats() -> dict:
    """
    Get embedding model statistics.

    Returns:
        Dictionary with model information
    """
    try:
        model = get_model()
        return {
            "model_name": settings.EMBEDDING_MODEL,
            "dimension": model.get_sentence_embedding_dimension(),
            "max_seq_length": model.max_seq_length,
            "device": str(model.device),
            "model_loaded": _model is not None
        }
    except Exception as e:
        logger.error(f"Error getting embedding stats: {e}")
        return {
            "model_name": settings.EMBEDDING_MODEL,
            "error": str(e),
            "model_loaded": False
        }


def combine_text_for_embedding(title: str, content: str, weight_title: float = 2.0) -> str:
    """
    Combine title and content for embedding generation.
    Title is repeated to give it more weight in semantic search.

    Args:
        title: Notice title
        content: Notice content
        weight_title: How many times to repeat title (default 2.0)

    Returns:
        Combined text optimized for embedding
    """
    # Repeat title based on weight
    title_repeated = " ".join([title] * int(weight_title))

    # Combine title and content
    combined = f"{title_repeated} {content}"

    return combined


class EmbeddingService:
    """Service class for embedding operations"""

    @staticmethod
    def generate(text: str) -> np.ndarray:
        """Generate embedding for text"""
        return generate_embedding(text)

    @staticmethod
    def batch_generate(texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        return batch_generate_embeddings(texts)

    @staticmethod
    def preprocess(text: str) -> str:
        """Preprocess text"""
        return preprocess_text(text)

    @staticmethod
    def embed_notice(notice_id: str, title: str, content: str) -> int:
        """Embed notice and add to index"""
        combined_text = combine_text_for_embedding(title, content)
        return embed_and_index_notice(notice_id, combined_text)

    @staticmethod
    def embed_notices_batch(notices: List[tuple]) -> List[int]:
        """
        Embed multiple notices and add to index.

        Args:
            notices: List of (notice_id, title, content) tuples

        Returns:
            List of FAISS positions
        """
        # Combine title and content for each notice
        notice_data = [
            (notice_id, combine_text_for_embedding(title, content))
            for notice_id, title, content in notices
        ]
        return embed_and_index_notices_batch(notice_data)

    @staticmethod
    def get_stats() -> dict:
        """Get embedding statistics"""
        return get_embedding_stats()


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
