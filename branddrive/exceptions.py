from __future__ import annotations

from typing import Optional
import httpx


class InvalidAPIKeyException(Exception):
    """Exception raised for invalid API key errors."""
    def __init__(self, message: str = "Invalid API Key") -> None:
        super().__init__(message)

class InvalidBaseURLException(Exception):
    """Exception raised for invalid base URL errors."""
    def __init__(self, message: str = "Invalid Base URL") -> None:
        super().__init__(message)



class APIException(Exception):
    """Base exception for BrandDrive API errors."""
    def __init__(self, message: str, status_code: Optional[int], request_id: Optional[str]) -> None:
        super().__init__(f"Exception: {message} (Status code: {status_code}, Request ID: {request_id})")
        self.status_code = status_code
        self.request_id = request_id


def handle_api_exception(res: httpx.Response) -> APIException:
    """Handle API exceptions based on the response."""
    try:
        message = res.json().get("message", "Unknown error")
    except (ValueError, KeyError, TypeError):
        message = res.reason_phrase
    return APIException(message, res.status_code, res.headers.get("X-Request-ID"))


