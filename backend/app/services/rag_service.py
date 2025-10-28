"""
RAG (Retrieval-Augmented Generation) service.
Combines semantic search with LLM generation for accurate, source-grounded responses.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Generator
import logging
from datetime import datetime

from app.services.embedding_service import generate_embedding
from app.services.llm_service import get_llm_service
from app.db.faiss_store import search, get_notice_ids
from app.db.mongodb import get_collection
from app.models.notice import Notice, NoticeType
from app.models.chat import SourceReference

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieval-augmented generation"""

    def __init__(self):
        self.llm_service = get_llm_service()
        self.similarity_threshold = 1.5  # L2 distance threshold
        self.max_context_tokens = 2000

    def search_relevant_notices(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant notices using semantic search.

        Args:
            query: User query
            top_k: Number of results to return
            filters: Optional filters (type, date range)

        Returns:
            List of notice dictionaries with similarity scores
        """
        try:
            logger.info(f"Searching for relevant notices: {query[:50]}...")

            # Generate query embedding
            query_embedding = generate_embedding(query)

            # Search FAISS index (get 2x results for filtering)
            distances, indices = search(query_embedding, top_k=top_k * 2)

            # Convert FAISS indices to MongoDB notice IDs
            notice_ids = get_notice_ids(indices)

            if not notice_ids:
                logger.warning("No notices found in FAISS index")
                return []

            # Retrieve full notices from MongoDB
            notices_collection = get_collection('notices')

            # Build MongoDB query
            mongo_query = {
                '_id': {'$in': notice_ids},
                'is_latest': True
            }

            # Apply filters
            if filters:
                if filters.get('type'):
                    mongo_query['source_type'] = filters['type']

                if filters.get('from_date') or filters.get('to_date'):
                    date_filter = {}
                    if filters.get('from_date'):
                        date_filter['$gte'] = filters['from_date']
                    if filters.get('to_date'):
                        date_filter['$lte'] = filters['to_date']
                    mongo_query['date_published'] = date_filter

            # Fetch notices
            notices = list(notices_collection.find(mongo_query))

            # Combine with similarity scores
            results = []
            for i, notice_id in enumerate(notice_ids):
                # Find matching notice
                notice = next((n for n in notices if str(n['_id']) == notice_id), None)

                if notice and i < len(distances):
                    distance = float(distances[i])

                    # Filter by similarity threshold
                    if distance <= self.similarity_threshold:
                        # Convert distance to similarity score (0-1, higher is better)
                        similarity_score = 1 / (1 + distance)

                        results.append({
                            'notice': notice,
                            'similarity_score': similarity_score,
                            'distance': distance
                        })

            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)

            # Return top k
            results = results[:top_k]

            logger.info(f"Found {len(results)} relevant notices")
            return results

        except Exception as e:
            logger.error(f"Error searching relevant notices: {e}")
            return []

    def build_context(
        self,
        search_results: List[Dict[str, Any]],
        max_tokens: int = 2000
    ) -> str:
        """
        Build context string from search results.

        Args:
            search_results: List of search result dicts
            max_tokens: Maximum tokens for context

        Returns:
            Formatted context string
        """
        if not search_results:
            return ""

        context_parts = ["Context from official KIIT sources:\n"]

        # Estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        current_chars = len(context_parts[0])

        for i, result in enumerate(search_results, 1):
            notice = result['notice']

            # Format notice entry
            title = notice.get('title', 'Untitled')
            date = notice.get('date_published', datetime.now()).strftime('%Y-%m-%d')
            source_type = notice.get('source_type', 'general')
            url = notice.get('source_url', '')
            content = notice.get('content', '')

            entry = f"\n[{i}] {title} (Published: {date}, Source: {source_type})\n"
            entry += f"URL: {url}\n"
            entry += f"Content: {content}\n"

            entry_len = len(entry)

            # Check if adding this entry exceeds limit
            if current_chars + entry_len > max_chars:
                # Try to add truncated content
                remaining_chars = max_chars - current_chars - 200  # Leave buffer
                if remaining_chars > 100:
                    truncated_content = content[:remaining_chars] + "..."
                    entry = f"\n[{i}] {title} (Published: {date}, Source: {source_type})\n"
                    entry += f"URL: {url}\n"
                    entry += f"Content: {truncated_content}\n"
                    context_parts.append(entry)
                break
            else:
                context_parts.append(entry)
                current_chars += entry_len

        context = ''.join(context_parts)
        logger.debug(f"Built context with {len(context)} characters from {len(search_results)} notices")
        return context

    def build_prompt(self, query: str, context: str) -> str:
        """
        Build complete prompt for LLM.

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Complete prompt string
        """
        prompt = f"""You are a helpful assistant for KIIT University students, faculty, and visitors.
Your role is to provide accurate information based on official KIIT notices and announcements.

{context}

User Question: {query}

Instructions:
1. Answer ONLY using the provided context above
2. If the context doesn't contain relevant information, say: "I don't have recent information about that. Please check the official KIIT website or contact the administration."
3. Always cite your sources by mentioning the notice title and date
4. Be concise but complete
5. If dates are mentioned, format them clearly (e.g., "November 3, 2025")
6. Use bullet points or numbered lists for multiple items
7. Maintain a helpful and professional tone

Answer:"""

        return prompt

    def generate_response(
        self,
        query: str,
        context: str,
        stream: bool = False
    ) -> str:
        """
        Generate response using LLM.

        Args:
            query: User query
            context: Retrieved context
            stream: Whether to stream response

        Returns:
            Generated response text
        """
        try:
            # Build prompt
            prompt = self.build_prompt(query, context)

            # Generate response
            if stream:
                # For streaming, collect all tokens
                tokens = []
                for token in self.llm_service.stream_generate(prompt):
                    tokens.append(token)
                response = ''.join(tokens)
            else:
                response = self.llm_service.generate(prompt)

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

    def generate_response_stream(
        self,
        query: str,
        context: str
    ) -> Generator[str, None, None]:
        """
        Generate streaming response using LLM.

        Args:
            query: User query
            context: Retrieved context

        Yields:
            Response tokens
        """
        try:
            # Build prompt
            prompt = self.build_prompt(query, context)

            # Stream response
            for token in self.llm_service.stream_generate(prompt):
                yield token

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield "I apologize, but I'm having trouble generating a response right now."

    def extract_sources(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[SourceReference]:
        """
        Extract source references from search results.

        Args:
            search_results: List of search result dicts

        Returns:
            List of SourceReference objects
        """
        sources = []

        for result in search_results:
            notice = result['notice']

            source = SourceReference(
                title=notice.get('title', 'Untitled'),
                date=notice.get('date_published', datetime.now()).strftime('%Y-%m-%d'),
                url=notice.get('source_url', ''),
                type=notice.get('source_type', 'general')
            )
            sources.append(source)

        return sources

    def query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: search + generate.

        Args:
            query: User query
            filters: Optional search filters
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with response and sources
        """
        try:
            logger.info(f"RAG query: {query[:50]}...")

            # Step 1: Search relevant notices
            search_results = self.search_relevant_notices(query, top_k=top_k, filters=filters)

            if not search_results:
                return {
                    'response': "I don't have recent information about that. Please check the official KIIT website or contact the administration.",
                    'sources': [],
                    'context_used': False
                }

            # Step 2: Build context
            context = self.build_context(search_results, max_tokens=self.max_context_tokens)

            # Step 3: Generate response
            response = self.generate_response(query, context, stream=False)

            # Step 4: Extract sources
            sources = self.extract_sources(search_results)

            return {
                'response': response,
                'sources': sources,
                'context_used': True,
                'num_sources': len(sources)
            }

        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                'response': "I apologize, but I encountered an error while processing your query. Please try again.",
                'sources': [],
                'context_used': False,
                'error': str(e)
            }

    def query_stream(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> tuple:
        """
        Complete RAG pipeline with streaming response.

        Args:
            query: User query
            filters: Optional search filters
            top_k: Number of documents to retrieve

        Returns:
            Tuple of (response_generator, sources_list)
        """
        try:
            logger.info(f"RAG streaming query: {query[:50]}...")

            # Search relevant notices
            search_results = self.search_relevant_notices(query, top_k=top_k, filters=filters)

            if not search_results:
                def error_gen():
                    yield "I don't have recent information about that. Please check the official KIIT website or contact the administration."

                return error_gen(), []

            # Build context
            context = self.build_context(search_results, max_tokens=self.max_context_tokens)

            # Generate streaming response
            response_gen = self.generate_response_stream(query, context)

            # Extract sources
            sources = self.extract_sources(search_results)

            return response_gen, sources

        except Exception as e:
            logger.error(f"Error in RAG streaming query: {e}")

            def error_gen():
                yield "I apologize, but I encountered an error while processing your query."

            return error_gen(), []


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get RAG service singleton"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
