"""
Simplified search service using PostgreSQL and OpenAI embeddings
"""
from app.database import SessionLocal, Notice, Course
from app.services.simple_llm_service import llm_service
from sqlalchemy import or_
import numpy as np
import json
import os


class SearchService:
    def __init__(self):
        self.embeddings_cache = {}
        self.load_embeddings()
    
    def load_embeddings(self):
        """Load pre-computed embeddings if available"""
        try:
            from app.config import settings
            if os.path.exists(settings.FAISS_MAPPING_PATH):
                with open(settings.FAISS_MAPPING_PATH, 'r') as f:
                    self.embeddings_cache = json.load(f)
        except:
            pass
    
    def search_notices(self, query: str, limit: int = 5):
        """Search notices using keyword matching"""
        db = SessionLocal()
        try:
            # Simple keyword search
            results = db.query(Notice).filter(
                or_(
                    Notice.title.ilike(f"%{query}%"),
                    Notice.content.ilike(f"%{query}%")
                )
            ).limit(limit).all()
            
            return [{
                "id": r.id,
                "title": r.title,
                "content": r.content,
                "url": r.url,
                "source_type": r.source_type,
                "date": r.date.isoformat() if r.date else None
            } for r in results]
        finally:
            db.close()
    
    def search_courses(self, query: str, limit: int = 5):
        """Search courses using keyword matching"""
        db = SessionLocal()
        try:
            results = db.query(Course).filter(
                or_(
                    Course.name.ilike(f"%{query}%"),
                    Course.code.ilike(f"%{query}%"),
                    Course.description.ilike(f"%{query}%")
                )
            ).limit(limit).all()
            
            return [{
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "description": r.description,
                "department": r.department,
                "duration": r.duration
            } for r in results]
        finally:
            db.close()
    
    def search_all(self, query: str, limit: int = 10):
        """Search both notices and courses"""
        notices = self.search_notices(query, limit // 2)
        courses = self.search_courses(query, limit // 2)
        
        # Combine results
        all_results = []
        for notice in notices:
            all_results.append({
                "type": "notice",
                **notice
            })
        for course in courses:
            all_results.append({
                "type": "course",
                **course
            })
        
        return all_results


# Global instance
search_service = SearchService()
