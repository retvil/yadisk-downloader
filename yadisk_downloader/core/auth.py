"""Authentication module for Yandex Disk OAuth token support."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import urllib.parse

from yadisk_downloader.config.schema import get_settings


@dataclass(frozen=True)
class YandexAuth:
    """Yandex Disk authentication handler."""

    token: Optional[str] = None

    @classmethod
    def from_settings(cls) -> "YandexAuth":
        """Create auth from global settings."""
        settings = get_settings()
        token = None
        if settings.yadisk_oauth_token:
            token = settings.yadisk_oauth_token.get_secret_value()
        return cls(token=token)

    def get_headers(self) -> dict[str, str]:
        """Get Authorization headers for API requests."""
        if self.token:
            return {"Authorization": f"OAuth {self.token}"}
        return {}

    def enhance_url(self, url: str) -> str:
        """Add OAuth token to URL if available."""
        if not self.token or "disk.yandex" not in url:
            return url
        # Only add to public folder URLs
        if "?oauth_token=" in url:
            return url
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}oauth_token={urllib.parse.quote(self.token)}"

    def enhance_public_key(self, public_key: str) -> str:
        """Add token to public key parameter."""
        if not self.token:
            return public_key
        return f"{public_key}&oauth_token={urllib.parse.quote(self.token)}"


def create_authenticated_session() -> "requests.Session":
    """Create requests session with OAuth headers."""
    import requests
    session = requests.Session()
    auth = YandexAuth.from_settings()
    if auth.token:
        session.headers.update(auth.get_headers())
    return session


def get_api_headers() -> dict[str, str]:
    """Get API headers with OAuth if available."""
    return YandexAuth.from_settings().get_headers()


def enhance_api_url(url: str) -> str:
    """Enhance API URL with OAuth token if available."""
    return YandexAuth.from_settings().enhance_url(url)