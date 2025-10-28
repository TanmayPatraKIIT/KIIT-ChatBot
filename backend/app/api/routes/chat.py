"""
Chat API routes for chatbot interactions.
Includes REST endpoint and WebSocket for streaming.
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import Optional
import time
import logging
import uuid
import json

from app.models.chat import ChatRequest, ChatResponse, ChatHistoryResponse, SourceReference
from app.services.rag_service import get_rag_service
from app.services.cache_service import get_cache_service
from app.db.mongodb import get_collection
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Process chat query and return responses.

    Args:
        request: ChatRequest with query and optional session_id

    Returns:
        ChatResponse with answer and sources
    """
    start_time = time.time()

    try:
        logger.info(f"Chat request: {request.query[:50]}...")

        # Get services
        cache_service = get_cache_service()
        rag_service = get_rag_service()

        # Check cache first
        cached_response = cache_service.get_cached_response(request.query)

        if cached_response:
            # Return cached response
            query_time_ms = int((time.time() - start_time) * 1000)
            cached_response["query_time_ms"] = query_time_ms
            cached_response["from_cache"] = True
            return ChatResponse(**cached_response)

        # Not in cache - perform RAG query
        result = rag_service.query(request.query, top_k=5)

        # Calculate query time
        query_time_ms = int((time.time() - start_time) * 1000)

        # Prepare response
        response = ChatResponse(
            response=result['response'],
            sources=result['sources'],
            query_time_ms=query_time_ms,
            from_cache=False
        )

        # Cache the response
        cache_service.set_cached_response(
            query=request.query,
            response=result['response'],
            sources=[s.dict() for s in result['sources']],
            query_time_ms=query_time_ms,
            ttl=3600  # 1 hour
        )

        # Store in chat history if session_id provided
        if request.session_id:
            try:
                await store_chat_message(
                    session_id=request.session_id,
                    user_id=request.user_id,
                    query=request.query,
                    response=result['response'],
                    sources=result['sources'],
                    query_time_ms=query_time_ms
                )
            except Exception as e:
                logger.error(f"Failed to store chat history: {e}")
                # Don't fail the request if history storage fails

        return response

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query. Please try again."
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a session.

    Args:
        session_id: Session identifier

    Returns:
        ChatHistoryResponse with message history
    """
    try:
        chat_history_collection = get_collection('chat_history')

        history = chat_history_collection.find_one({"session_id": session_id})

        if not history:
            return ChatHistoryResponse(
                session_id=session_id,
                messages=[]
            )

        return ChatHistoryResponse(
            session_id=session_id,
            messages=history.get('messages', [])
        )

    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat responses.

    Protocol:
    - Client sends: {"query": "...", "session_id": "..."}
    - Server streams: {"type": "token", "content": "word"}
    - Server sends: {"type": "sources", "data": [...]}
    - Server sends: {"type": "done"}
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            query = message.get('query')
            session_id = message.get('session_id')

            if not query:
                await websocket.send_json({
                    "type": "error",
                    "content": "Query is required"
                })
                continue

            logger.info(f"WebSocket query: {query[:50]}...")

            # Get RAG service
            rag_service = get_rag_service()

            # Stream response
            try:
                response_gen, sources = rag_service.query_stream(query, top_k=5)

                # Stream tokens
                full_response = []
                for token in response_gen:
                    await websocket.send_json({
                        "type": "token",
                        "content": token
                    })
                    full_response.append(token)

                # Send sources
                await websocket.send_json({
                    "type": "sources",
                    "data": [s.dict() for s in sources]
                })

                # Send done signal
                await websocket.send_json({
                    "type": "done"
                })

                # Store in history
                if session_id:
                    try:
                        await store_chat_message(
                            session_id=session_id,
                            user_id=None,
                            query=query,
                            response=''.join(full_response),
                            sources=sources,
                            query_time_ms=0  # Not tracking for streaming
                        )
                    except Exception as e:
                        logger.error(f"Failed to store WebSocket chat history: {e}")

            except Exception as e:
                logger.error(f"Error in WebSocket streaming: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": "Failed to generate response"
                })

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass


async def store_chat_message(
    session_id: str,
    user_id: Optional[str],
    query: str,
    response: str,
    sources: list,
    query_time_ms: int
):
    """
    Store chat message in history.

    Args:
        session_id: Session identifier
        user_id: Optional user identifier
        query: User query
        response: Bot response
        sources: List of source references
        query_time_ms: Query execution time
    """
    chat_history_collection = get_collection('chat_history')

    # Create message objects
    user_message = {
        "role": "user",
        "content": query,
        "timestamp": datetime.utcnow()
    }

    assistant_message = {
        "role": "assistant",
        "content": response,
        "timestamp": datetime.utcnow(),
        "sources": [s.dict() if hasattr(s, 'dict') else s for s in sources],
        "query_time_ms": query_time_ms
    }

    # Update or create chat history
    chat_history_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "$each": [user_message, assistant_message]
                }
            },
            "$set": {
                "last_updated": datetime.utcnow()
            },
            "$setOnInsert": {
                "user_id": user_id,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
