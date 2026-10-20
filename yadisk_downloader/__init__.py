"""yadisk-downloader — Yandex Disk Downloader with CLI and GUI."""

__version__ = "1.3.0"

# Config
from .config.schema import (
    DownloadSettings,
    ProxySettings,
    Settings,
    get_config,
    get_settings,
)

# Core
from .core import (
    M3U8_CACHE,
    Cache,
    build_proxy_dict,
    download_hls_parallel,
    download_hls_parallel_sync,
    parse_proxy_url,
    sanitize_proxy_for_log,
    sanitize_url_for_log,
    validate_output_path,
)

# Downloader (new plugin-based API + backward compat)
from .core.downloader import (
    download_file,
    download_from_api,
    download_hls,
    download_via_browser,
    download_via_docviewer,
)

# DI
from .di.container import Container, get_container

# Events
from .events import (
    ConversionCompleted,
    ConversionFailed,
    ConversionStarted,
    DownloadCompleted,
    DownloadFailed,
    DownloadProgress,
    DownloadStarted,
    Event,
    EventBus,
    FolderScanCompleted,
    FolderScanStarted,
    QueueProcessCompleted,
    QueueProcessStarted,
    StateSaved,
    get_event_bus,
    set_event_bus,
)

# Plugins
from .plugins.base import (
    DownloadContext,
    DownloadResult,
    DownloadStrategy,
    FileInfo,
    StrategyRegistry,
    get_registry,
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
