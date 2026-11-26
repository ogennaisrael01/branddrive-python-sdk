from __future__ import annotations

from typing import Optional, Any

from branddrive.config import settings
from branddrive.exceptions import handle_api_exception, InvalidAPIKeyException, InvalidBaseURLException

import httpx
import time
import random


class Client:
    def __init__(
            self, api_key: Optional[str], 
            base_url: Optional[str], 
            timeout: Optional[int] = 30
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        if not self.api_key:
            raise InvalidAPIKeyException("API key is required. Please set the BRANDDRIVE_API_KEY environment variable or provide it as an argument.")

        if not self.base_url:
            raise InvalidBaseURLException("Base URL is required. Please set the BRANDDRIVE_BASE_URL environment variable or provide it as an argument.")

    def _client(self) -> httpx.Client:

        """Create an HTTP client with the specified settings."""

        return httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    def __exit__(self, exc_type, exc, tb):

        """Close the HTTP client when exiting the context."""
        self._client().close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client().close()


class BrandDriveClient:
    """BrandDrive API client."""

    def __init__(
            self, api_key: str = settings.api_key, 
            base_url: str = settings.base_url, 
            timeout: int = 10,
            max_retries: int = 3,
    ) -> None:
        client = Client(api_key, base_url, timeout)

        self._httpx = client._client()
        self._max_retries = max_retries


    def request(self, method: str, path: str, **kwargs) -> Any:
        """Send a request to the BrandDrive API with retry logic."""

        attempt = 0
        while True:
            delay = 0.5 * 2**attempt + random.uniform(0, 0.25) # Exponential backoff delay
            try:
                response = self._httpx.request(method, path, **kwargs)
            except httpx.TransportError:
                if attempt >= self._max_retries:
                    raise
            else:
                status_code = response.status_code
                if response.is_success:
                    return response.json()

                retryable = status_code == 500 # Retry server error, return client error back to the user
                if not retryable or attempt >= self._max_retries:
                    return handle_api_exception(response)

            time.sleep(delay)
            attempt += 1

