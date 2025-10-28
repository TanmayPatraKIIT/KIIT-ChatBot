"""
LLM service for interacting with LLaMA/Mistral models via Ollama.
Handles text generation with streaming support.
"""

import requests
import json
from typing import Generator, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM text generation via Ollama"""

    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE

        # Ollama API endpoints
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"

    def _check_model_availability(self) -> bool:
        """
        Check if Ollama service and model are available.

        Returns:
            True if available, False otherwise
        """
        try:
            # Try to list models
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()

            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]

            if self.model in available_models:
                logger.debug(f"Model {self.model} is available")
                return True
            else:
                logger.warning(f"Model {self.model} not found. Available models: {available_models}")
                return False

        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[list] = None
    ) -> str:
        """
        Generate text completion from prompt (non-streaming).

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stop: Stop sequences

        Returns:
            Generated text
        """
        try:
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature if temperature is not None else self.temperature
            stop = stop or ["\n\nUser:", "\n\nQuestion:", "\n\nContext:"]

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "stop": stop,
                    "top_p": 0.9
                }
            }

            logger.debug(f"Generating with model {self.model}, max_tokens={max_tokens}, temp={temperature}")

            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result.get('response', '')

            logger.info(f"Generated {len(generated_text)} characters")
            return generated_text

        except requests.exceptions.Timeout:
            logger.error("LLM generation timeout")
            raise Exception("LLM service timeout. Please try again.")

        except requests.exceptions.RequestException as e:
            logger.error(f"LLM generation failed: {e}")
            raise Exception("LLM service unavailable")

        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            raise

    def stream_generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[list] = None
    ) -> Generator[str, None, None]:
        """
        Generate text completion with streaming (yields tokens as they arrive).

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences

        Yields:
            Generated tokens
        """
        try:
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature if temperature is not None else self.temperature
            stop = stop or ["\n\nUser:", "\n\nQuestion:", "\n\nContext:"]

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "stop": stop,
                    "top_p": 0.9
                }
            }

            logger.debug(f"Streaming generation with model {self.model}")

            response = requests.post(
                self.generate_endpoint,
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()

            # Stream response line by line
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        token = data.get('response', '')
                        if token:
                            yield token

                        # Check if generation is done
                        if data.get('done', False):
                            break

                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming response: {line}")
                        continue

            logger.info("Streaming generation completed")

        except requests.exceptions.Timeout:
            logger.error("LLM streaming timeout")
            yield "[Error: Generation timeout]"

        except requests.exceptions.RequestException as e:
            logger.error(f"LLM streaming failed: {e}")
            yield "[Error: LLM service unavailable]"

        except Exception as e:
            logger.error(f"Unexpected error in LLM streaming: {e}")
            yield f"[Error: {str(e)}]"

    def chat_generate(
        self,
        messages: list,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response using chat endpoint (supports conversation history).

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated response
        """
        try:
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature if temperature is not None else self.temperature

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                }
            }

            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            message = result.get('message', {})
            generated_text = message.get('content', '')

            return generated_text

        except Exception as e:
            logger.error(f"Chat generation failed: {e}")
            raise

    def is_available(self) -> bool:
        """
        Check if LLM service is available.

        Returns:
            True if service is available and ready
        """
        return self._check_model_availability()

    def get_model_info(self) -> dict:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        try:
            response = requests.get(f"{self.base_url}/api/show", json={"name": self.model}, timeout=5)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                "error": str(e),
                "model": self.model,
                "base_url": self.base_url
            }


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
