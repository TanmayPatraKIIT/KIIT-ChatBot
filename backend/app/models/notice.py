"""
Notice data model for storing scraped KIIT notices and announcements.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NoticeType(str, Enum):
    GENERAL = "general"
    EXAM = "exam"
    ACADEMIC = "academic"
    HOLIDAY = "holiday"


class NoticeMetadata(BaseModel):
    """Metadata for notice content analysis"""
    word_count: int = 0
    has_dates: bool = False
    extracted_dates: List[datetime] = Field(default_factory=list)
    language: str = "en"


class Notice(BaseModel):
    """Notice data model matching MongoDB schemas"""

    id: Optional[str] = Field(None, alias="_id")
    title: str
    content: str
    date_published: datetime
    date_scraped: datetime
    source_url: str
    source_type: NoticeType
    content_hash: str
    attachments: List[str] = Field(default_factory=list)
    metadata: NoticeMetadata = Field(default_factory=NoticeMetadata)
    faiss_index_id: Optional[int] = None
    version: int = 1
    is_latest: bool = True
    previous_version_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Mid-Semester Exam Schedule Autumn 2025",
                "content": "The mid-semester examinations will be conducted from November 3rd to November 10th, 2025.",
                "date_published": "2025-10-15T00:00:00Z",
                "date_scraped": "2025-10-27T08:00:00Z",
                "source_url": "http://coe.kiit.ac.in/notices.php",
                "source_type": "exam",
                "content_hash": "sha256_hash_string",
                "attachments": ["https://kiit.ac.in/path/to/schedule.pdf"],
                "metadata": {
                    "word_count": 450,
                    "has_dates": True,
                    "extracted_dates": ["2025-11-03", "2025-11-10"],
                    "language": "en"
                },
                "faiss_index_id": 123,
                "version": 1,
                "is_latest": True
            }
        }


class NoticeCreate(BaseModel):
    """Model for creating new notices"""
    title: str
    content: str
    date_published: datetime
    source_url: str
    source_type: NoticeType
    attachments: List[str] = Field(default_factory=list)


class NoticeUpdate(BaseModel):
    """Model for updating existing notices"""
    title: Optional[str] = None
    content: Optional[str] = None
    date_published: Optional[datetime] = None
    source_url: Optional[str] = None
    source_type: Optional[NoticeType] = None
    attachments: Optional[List[str]] = None


class NoticeResponse(BaseModel):
    """Model for notice API responses"""
    id: str
    title: str
    excerpt: str  # First 150 characters of content
    date: str  # ISO date string
    type: NoticeType
    url: str  # source_url

    @classmethod
    def from_notice(cls, notice: Notice) -> "NoticeResponse":
        """Create response model from Notice"""
        return cls(
            id=notice.id or "",
            title=notice.title,
            excerpt=notice.content[:150] + "..." if len(notice.content) > 150 else notice.content,
            date=notice.date_published.isoformat(),
            type=notice.source_type,
            url=notice.source_url
        )


class NoticeSearch(BaseModel):
    """Model for notice search parameters"""
    query: Optional[str] = None
    type: Optional[NoticeType] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = Field(default=10, le=50)
    offset: int = Field(default=0, ge=0)


class NoticeSearchResponse(BaseModel):
    """Model for notice search API response"""
    total: int
    notices: List[NoticeResponse]