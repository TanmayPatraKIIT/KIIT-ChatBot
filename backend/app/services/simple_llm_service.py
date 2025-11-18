"""
Simplified LLM service using OpenAI via Replit AI Integrations
"""
import os
from openai import OpenAI
from app.config import settings


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL

    def generate_response(self, query: str, context: str = "") -> str:
        """Generate a response using OpenAI"""
        try:
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"You are a helpful KIIT University assistant. Use the following context to answer the question:\n\n{context}"
                })
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful KIIT University assistant. Provide accurate information about KIIT."
                })
            
            messages.append({
                "role": "user",
                "content": query
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error processing your request."

    def generate_embedding(self, text: str) -> list:
        """Generate embeddings using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []


# Global instance
llm_service = LLMService()
