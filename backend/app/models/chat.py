"""
Chat data models for user conversations and message history.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class SourceReference(BaseModel):
    """Sources reference for chatbot responses"""
    title: str
    date: str
    url: str
    type: str


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: MessageRole
    content: str
    timestamp: datetime
    sources: Optional[List[SourceReference]] = None
    query_time_ms: Optional[int] = None


class ChatHistory(BaseModel):
    """Chat history for a session"""
    id: Optional[str] = Field(None, alias="_id")
    session_id: str
    user_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., min_length=1, max_length=500)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "When is the mid-semester exam?",
                "session_id": "abc123"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    sources: List[SourceReference]
    query_time_ms: int
    from_cache: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Based on recent notices, the mid-semester exams are scheduled from November 3-10, 2025.",
                "sources": [
                    {
                        "title": "Mid-Semester Exam Schedule",
                        "date": "2025-10-15",
                        "url": "http://coe.kiit.ac.in/notices.php",
                        "type": "exam"
                    }
                ],
                "query_time_ms": 450,
                "from_cache": False
            }
        }


class ChatHistoryResponse(BaseModel):
    """Response model for chat history endpoint"""
    session_id: str
    messages: List[ChatMessage]

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "messages": [
                    {
                        "role": "user",
                        "content": "When is the exam?",
                        "timestamp": "2025-10-27T10:30:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "The mid-semester exam is on November 3, 2025.",
                        "timestamp": "2025-10-27T10:30:02Z",
                        "sources": [],
                        "query_time_ms": 450
                    }
                ]
            }
        }


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # "token", "sources", "done", "error"
    content: Optional[str] = None
    data: Optional[dict] = None


class FeedbackRequest(BaseModel):
    """User feedback on chatbot responses"""
    query: str
    response: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    session_id: Optional[str] = None