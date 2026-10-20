"""Pydantic-based configuration with validation and environment variable support."""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DownloadSettings(BaseSettings):
    """Download-specific settings."""

    model_config = SettingsConfigDict(
        env_prefix="YDD_DOWNLOAD_",
        case_sensitive=False,
    )

    resolution: Literal["240p", "360p", "480p", "720p", "1080p"] = Field(default="720p", description="Video resolution")
    output_dir: Path = Field(default_factory=lambda: Path.cwd() / "downloads")
    workers: int = Field(default=4, ge=1, le=32, description="Parallel folder/worker count")
    parallel_segments: int = Field(default=4, ge=1, le=16, description="HLS segment parallelism")
    pool_size: int = Field(default=10, ge=1, le=100, description="HTTP connection pool size")
    resume: bool = Field(default=True, description="Resume interrupted downloads")
    checksum: bool = Field(default=False, description="Verify MD5 after download")
    delete_original: bool = Field(default=False, description="Delete original after conversion")
    preset: str | None = Field(default=None, description="Conversion preset")
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff: float = Field(default=1.0, ge=0.1, le=60.0)

    @field_validator("output_dir", mode="before")
    @classmethod
    def expand_output_dir(cls, v: Path | str) -> Path:
        if isinstance(v, str):
            v = os.path.expanduser(v)
            v = os.path.expandvars(v)
        return Path(v)


class ProxySettings(BaseSettings):
    """Proxy configuration."""

    model_config = SettingsConfigDict(
        env_prefix="YDD_PROXY_",
        case_sensitive=False,
    )

    enabled: bool = Field(default=False)
    url: str | None = Field(default=None, description="Proxy URL (http://user:pass@host:port)")
    auth_username: str | None = Field(default=None)
    auth_password: str | None = Field(default=None)

    @field_validator("url", mode="before")
    @classmethod
    def parse_proxy_url(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not any(v.startswith(p) for p in ("http://", "https://", "socks4://", "socks5://")):
            return f"http://{v}"
        return v

    @property
    def proxy_dict(self) -> dict[str, str] | None:
        """Build proxy dict for requests."""
        if not self.url:
            return None
        auth = ""
        if self.auth_username and self.auth_password:
            auth = f"{self.auth_username}:{self.auth_password}@"
        elif self.auth_username:
            auth = f"{self.auth_username}@"
        if "://" in self.url:
            scheme, rest = self.url.split("://", 1)
            return {scheme: f"{scheme}://{auth}{rest}"}
        return None


class NotificationSettings(BaseSettings):
    """Notification settings."""

    model_config = SettingsConfigDict(
        env_prefix="YDD_NOTIFY_",
        case_sensitive=False,
    )

    enabled: bool = Field(default=False)
    telegram_bot_token: str | None = Field(default=None)
    telegram_chat_id: str | None = Field(default=None)
    webhook_url: str | None = Field(default=None)


class SchedulerSettings(BaseSettings):
    """Scheduler settings."""

    model_config = SettingsConfigDict(
        env_prefix="YDD_SCHED_",
        case_sensitive=False,
    )

    enabled: bool = Field(default=False)
    check_interval: int = Field(default=60, ge=10, description="Seconds between schedule checks")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    download: DownloadSettings = Field(default_factory=DownloadSettings)
    proxy: ProxySettings = Field(default_factory=ProxySettings)
    notify: NotificationSettings = Field(default_factory=NotificationSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)

    # OAuth token for private folders / higher limits
    yadisk_oauth_token: SecretStr | None = Field(default=None, description="Yandex Disk OAuth token")

    # App-level
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    cache_ttl_hours: int = Field(default=24, ge=1, le=168)
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".yadisk-downloader" / "cache")
    state_dir: Path = Field(default_factory=lambda: Path.home() / ".yadisk-downloader" / "state")
    config_dir: Path = Field(default_factory=lambda: Path.home() / ".yadisk-downloader")

    @field_validator("cache_dir", "state_dir", "config_dir", mode="before")
    @classmethod
    def expand_path(cls, v: Path | str) -> Path:
        if isinstance(v, str):
            v = os.path.expanduser(v)
            v = os.path.expandvars(v)
        return Path(v)

    @property
    def oauth_headers(self) -> dict[str, str]:
        """Get OAuth headers for API requests."""
        if self.yadisk_oauth_token:
            return {"Authorization": f"OAuth {self.yadisk_oauth_token.get_secret_value()}"}
        return {}

    def get_cache_dir(self, subdir: str = "") -> Path:
        """Get cache directory for specific purpose."""
        path = self.cache_dir / subdir if subdir else self.cache_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_state_dir(self) -> Path:
        """Get state directory."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        return self.state_dir

    def get_config_path(self) -> Path:
        """Get config file path."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        return self.config_dir / "config.json"

    def save(self, path: Path | None = None) -> None:
        """Save config to JSON file."""
        path = path or self.get_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclude SecretStr from JSON
        data = self.model_dump(exclude={"yadisk_oauth_token"})
        if self.yadisk_oauth_token:
            data["yadisk_oauth_token"] = self.yadisk_oauth_token.get_secret_value()
        with path.open("w", encoding="utf-8") as f:
            import json
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    @classmethod
    def load(cls, path: Path | None = None) -> "Settings":
        """Load config from JSON file."""
        path = path or cls().get_config_path()
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                import json
                data = json.load(f)
            return cls(**data)
        return cls()


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance (for dependency injection)."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment/config."""
    global settings
    settings = Settings()
    return settings


# Alias for backward compatibility
get_config = get_settings
