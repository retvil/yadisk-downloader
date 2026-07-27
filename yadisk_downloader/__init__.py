"""yadisk-downloader — Yandex Disk Downloader with CLI and GUI."""

__version__ = "1.2.0"

# Config
from .config.schema import (
    get_settings,
    get_config,
    Settings,
    DownloadSettings,
    ProxySettings,
)

# Events
from .events import (
    EventBus,
    Event,
    DownloadStarted,
    DownloadProgress,
    DownloadCompleted,
    DownloadFailed,
    FolderScanStarted,
    FolderScanCompleted,
    QueueProcessStarted,
    QueueProcessCompleted,
    ConversionStarted,
    ConversionCompleted,
    ConversionFailed,
    StateSaved,
    get_event_bus,
    set_event_bus,
)

# Plugins
from .plugins.base import (
    DownloadStrategy,
    FileInfo,
    DownloadContext,
    DownloadResult,
    StrategyRegistry,
    get_registry,
)

# DI
from .di.container import Container, get_container

# Core
from .core import (
    Cache,
    M3U8_CACHE,
    download_hls_parallel,
    download_hls_parallel_sync,
    sanitize_url_for_log,
    validate_output_path,
    parse_proxy_url,
    sanitize_proxy_for_log,
    build_proxy_dict,
)

# Downloader (new plugin-based API + backward compat)
from .core.downloader import (
    download_file,
    download_hls,
    download_from_api,
    download_via_docviewer,
    download_via_browser,
)

__all__ = [
    # Version
    "__version__",
    # Config
    "get_settings",
    "get_config",
    "Settings",
    "DownloadSettings",
    "ProxySettings",
    # Events
    "EventBus",
    "Event",
    "DownloadStarted",
    "DownloadProgress",
    "DownloadCompleted",
    "DownloadFailed",
    "FolderScanStarted",
    "FolderScanCompleted",
    "QueueProcessStarted",
    "QueueProcessCompleted",
    "ConversionStarted",
    "ConversionCompleted",
    "ConversionFailed",
    "StateSaved",
    "get_event_bus",
    "set_event_bus",
    # Plugins
    "DownloadStrategy",
    "FileInfo",
    "DownloadContext",
    "DownloadResult",
    "StrategyRegistry",
    "get_registry",
    # DI
    "Container",
    "get_container",
    # Core
    "Cache",
    "M3U8_CACHE",
    "download_hls_parallel",
    "download_hls_parallel_sync",
    "sanitize_url_for_log",
    "validate_output_path",
    "parse_proxy_url",
    "sanitize_proxy_for_log",
    "build_proxy_dict",
    # Downloader
    "download_file",
    "download_hls",
    "download_from_api",
    "download_via_docviewer",
    "download_via_browser",
]