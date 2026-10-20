"""Events module exports."""

from .bus import (
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

__all__ = [
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
]
