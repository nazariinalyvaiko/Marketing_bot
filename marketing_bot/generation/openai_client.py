from __future__ import annotations

import asyncio
import os
import time
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

from marketing_bot.config import settings
from marketing_bot.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class OpenAIClient:
    """Enhanced OpenAI client with retry logic and error handling."""
    
    def __init__(self):
        self.client = self._create_client()
        self.max_retries = 3
        self.retry_delay = 1.0

    def _create_client(self) -> OpenAI:
        """Create OpenAI client with proper configuration."""
        api_key = settings.OPENAI_API_KEY
        base_url = settings.OPENAI_BASE_URL
        
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        
        return OpenAI(api_key=api_key, base_url=base_url)

    async def generate_marketing_text(
        self,
        prompt: str,
        model: str | None = None,
        tone: Literal["friendly", "professional", "playful", "urgent"] = "professional",
        max_tokens: int = 400,
    ) -> str:
        """Generate marketing text with retry logic and error handling."""
        
        # Check offline mode
        if settings.OFFLINE_MODE or not settings.OPENAI_API_KEY:
            logger.warning("OFFLINE_MODE active or OPENAI_API_KEY missing — returning mock content.")
            return self._mock_response(prompt, tone)

        model_name = model or settings.OPENAI_MODEL
        system = f"You are a {tone} marketing copywriter. Create concise, high-conversion copy."
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                logger.debug(f"Generating text (attempt {attempt + 1}/{self.max_retries})")
                
                response: ChatCompletion = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                
                generation_time = int((time.time() - start_time) * 1000)
                logger.info(f"Generated text in {generation_time}ms")
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All {self.max_retries} attempts failed, falling back to mock")
                    return self._mock_response(prompt, tone)

    def _mock_response(self, prompt: str, tone: str) -> str:
        """Generate mock response for offline mode or fallback."""
        if "Subject:" in prompt or "marketing email" in prompt.lower():
            return (
                f"Subject: [MOCK] Your Exclusive Offer\n\n"
                f"Hello! Here's a sample email in {tone} tone.\n"
                f"Take advantage of this offer today and click the CTA button.\n"
                f"— Marketing Bot (offline)"
            )
        return (
            f"[MOCK] Try our product now and get a discount! "
            f"#sale #offer #demo"
        )


# Global instance
_client = None

def get_openai_client() -> OpenAIClient:
    """Get singleton OpenAI client instance."""
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client

# Backward compatibility
def generate_marketing_text(
    prompt: str,
    model: str | None = None,
    tone: Literal["friendly", "professional", "playful", "urgent"] = "professional",
    max_tokens: int = 400,
) -> str:
    """Backward compatible function with proper OFFLINE_MODE handling."""
    
    # Check offline mode first
    if settings.OFFLINE_MODE or not settings.OPENAI_API_KEY:
        logger.warning("OFFLINE_MODE active or OPENAI_API_KEY missing — returning mock content.")
        return _mock_response(prompt, tone)
    
    # Use the async client for real generation
    client = get_openai_client()
    return asyncio.run(client.generate_marketing_text(prompt, model, tone, max_tokens))


def _mock_response(prompt: str, tone: str) -> str:
    """Generate mock response for offline mode or fallback."""
    if "Subject:" in prompt or "marketing email" in prompt.lower():
        return (
            f"Subject: [MOCK] Your Exclusive Offer\n\n"
            f"Hello! Here's a sample email in {tone} tone.\n"
            f"Take advantage of this offer today and click the CTA button.\n"
            f"— Marketing Bot (offline)"
        )
    return (
        f"[MOCK] Try our product now and get a discount! "
        f"#sale #offer #demo"
    )
