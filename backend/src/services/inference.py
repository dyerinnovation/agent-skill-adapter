"""Inference client for OpenAI-compatible TGI endpoints."""
import asyncio
import logging
from typing import Any

import httpx

from src.models.config import settings

logger = logging.getLogger(__name__)


class InferenceClient:
    """Async HTTP client for OpenAI-compatible inference endpoints."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """Initialize the inference client.

        Args:
            base_url: Base URL of the inference endpoint. Defaults to settings.inference_url.
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Maximum number of retries with exponential backoff. Defaults to 3.
        """
        self.base_url = (base_url or settings.inference_url).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with exponential backoff retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON payload for POST requests

        Returns:
            Response JSON

        Raises:
            httpx.HTTPError: If all retries fail
        """
        url = f"{self.base_url}{endpoint}"
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, json=json)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    backoff = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Request to {url} failed (attempt {attempt + 1}/{self.max_retries}): {e}. "
                        f"Retrying in {backoff}s..."
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        f"Request to {url} failed after {self.max_retries} attempts: {e}"
                    )

        raise last_exception  # type: ignore

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion for a prompt using the /v1/completions endpoint.

        Args:
            prompt: Input prompt text
            **kwargs: Additional parameters to pass to the API (e.g., max_tokens, temperature)

        Returns:
            Generated completion text

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]},
        }

        try:
            response_data = await self._request_with_retry(
                "POST", "/v1/completions", json=payload
            )
            # Extract completion text from OpenAI-compatible response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0].get("text", "")
            logger.warning(f"Unexpected response format: {response_data}")
            return ""
        except Exception as e:
            logger.error(f"Completion request failed: {e}")
            raise

    async def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        """Generate chat completion using the /v1/chat/completions endpoint.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional parameters to pass to the API (e.g., max_tokens, temperature)

        Returns:
            Generated assistant message text

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]},
        }

        try:
            response_data = await self._request_with_retry(
                "POST", "/v1/chat/completions", json=payload
            )
            # Extract message content from OpenAI-compatible response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message", {})
                return message.get("content", "")
            logger.warning(f"Unexpected response format: {response_data}")
            return ""
        except Exception as e:
            logger.error(f"Chat completion request failed: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if the inference endpoint is healthy.

        Returns:
            True if the endpoint responds successfully, False otherwise
        """
        try:
            # Try to hit the health endpoint or a simple completions request
            await self._request_with_retry("GET", "/health")
            return True
        except httpx.HTTPError:
            # If /health doesn't exist, try a minimal completion request
            try:
                await self.complete("test", max_tokens=1)
                return True
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return False
