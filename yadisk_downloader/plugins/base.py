"""Plugin system base classes and registry."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional, TypeVar
from pathlib import Path

from yadisk_downloader.events import EventBus, DownloadProgress, DownloadCompleted, DownloadFailed

T = TypeVar("T")


@dataclass(frozen=True)
class FileInfo:
    """Information about a file to download."""
    name: str
    path: str  # Path on Yandex Disk
    size: int
    file_type: str  # video, audio, image, document, etc.
    mime_type: Optional[str] = None
    folder: Optional[str] = None
    download_url: Optional[str] = None  # Direct API URL
    m3u8_url: Optional[str] = None  # HLS playlist URL
    sha256: Optional[str] = None


@dataclass(frozen=True)
class DownloadContext:
    """Context passed to download strategies."""
    settings: Any  # Config object
    event_bus: EventBus
    cache_dir: Path
    state_dir: Path
    proxy_dict: Optional[dict[str, str]] = None
    oauth_headers: Optional[dict[str, str]] = None
    progress_callback: Optional[callable] = None


@dataclass(frozen=True)
class DownloadResult:
    """Result of a download attempt."""
    success: bool
    path: Optional[Path] = None
    size: int = 0
    checksum: Optional[str] = None
    error: Optional[str] = None
    strategy_used: Optional[str] = None


class DownloadStrategy(Protocol):
    """Protocol for download strategies (plugins)."""

    name: str
    priority: int  # Higher = tried first

    def can_handle(self, file_info: FileInfo) -> bool:
        """Return True if this strategy can handle the file."""
        ...

    def download(
        self,
        file_info: FileInfo,
        dest: Path,
        context: DownloadContext,
    ) -> DownloadResult:
        """Download the file. Return result."""
        ...

    def get_default_options(self) -> dict:
        """Return default options for this strategy."""
        return {}


class StrategyRegistry:
    """Registry for download strategies."""

    def __init__(self):
        self._strategies: list[DownloadStrategy] = []

    def register(self, strategy: DownloadStrategy) -> None:
        """Register a strategy."""
        self._strategies.append(strategy)
        self._strategies.sort(key=lambda s: -s.priority)  # Highest priority first

    def unregister(self, name: str) -> bool:
        """Unregister a strategy by name."""
        for i, s in enumerate(self._strategies):
            if s.name == name:
                self._strategies.pop(i)
                return True
        return False

    def get_for_file(self, file_info: FileInfo) -> Optional[DownloadStrategy]:
        """Get the best strategy for a file."""
        for strategy in self._strategies:
            if strategy.can_handle(file_info):
                return strategy
        return None

    def get_all(self) -> list[DownloadStrategy]:
        """Get all registered strategies."""
        return list(self._strategies)

    def clear(self) -> None:
        """Clear all strategies."""
        self._strategies.clear()


# Global registry
_registry: StrategyRegistry | None = None


def get_registry() -> StrategyRegistry:
    """Get global strategy registry."""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
        _register_builtin_strategies(_registry)
    return _registry


def set_registry(registry: StrategyRegistry) -> None:
    """Set global registry (for testing)."""
    global _registry
    _registry = registry


def _register_builtin_strategies(registry: StrategyRegistry) -> None:
    """Register built-in strategies."""
    # Import here to avoid circular imports
    from yadisk_downloader.plugins.hls import HLSVideoStrategy
    from yadisk_downloader.plugins.api import APIFileStrategy
    from yadisk_downloader.plugins.docviewer import DocviewerStrategy
    from yadisk_downloader.plugins.browser import BrowserStrategy

    registry.register(HLSVideoStrategy())
    registry.register(APIFileStrategy())
    registry.register(DocviewerStrategy())
    registry.register(BrowserStrategy())