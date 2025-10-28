"""
User data models for authentication and personalization (future phase).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    VISITOR = "visitor"
    ADMIN = "admin"


class User(BaseModel):
    """User models for future authentication"""
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    name: str
    role: UserRole = UserRole.VISITOR
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: dict = Field(default_factory=dict)
    bookmarked_notices: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class UserPreferences(BaseModel):
    """User preferences for notifications and filters"""
    notify_exam: bool = True
    notify_general: bool = True
    notify_holiday: bool = False
    language: str = "en"