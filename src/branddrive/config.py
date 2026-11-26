from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Settings for BrandDrive SDK."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("BRANDDRIVE_API_KEY", "")
        self.base_url = os.environ.get("BRANDDRIVE_BASE_URL", "https://api.branddrive.com")

settings = Settings()