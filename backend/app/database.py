"""
Database setup using SQLAlchemy with PostgreSQL
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Notice(Base):
    """Model for KIIT notices/information"""
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1000))
    source_type = Column(String(100), index=True)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Embedding(Base):
    """Model for storing OpenAI embeddings"""
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, index=True)
    content_type = Column(String(50), index=True)
    text = Column(Text)
    embedding_vector = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Course(Base):
    """Model for KIIT courses"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    code = Column(String(50), unique=True)
    description = Column(Text)
    department = Column(String(200))
    duration = Column(String(100))
    eligibility = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    """Model for chat history"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(200), index=True)
    role = Column(String(50))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Model for users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    email = Column(String(200), unique=True, index=True)
    password_hash = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
