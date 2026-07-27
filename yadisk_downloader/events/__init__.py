"""Events module exports."""

from .bus import (
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