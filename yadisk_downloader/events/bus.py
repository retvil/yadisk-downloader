"""Event bus for decoupled communication between components."""

import asyncio
from collections import defaultdict
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Event:
    """Base event class."""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""


@dataclass(frozen=True)
class DownloadStarted(Event):
    """Download started for a file."""
    url: str = ""
    file_path: str = ""
    file_size: int = 0


@dataclass(frozen=True)
class DownloadProgress(Event):
    """Download progress update."""
    url: str = ""
    file_path: str = ""
    downloaded: int = 0
    total: int = 0
    speed: float = 0.0

    @property
    def percent(self) -> float:
        return (self.downloaded / self.total * 100) if self.total > 0 else 0.0


@dataclass(frozen=True)
class DownloadCompleted(Event):
    """Download completed successfully."""
    url: str = ""
    file_path: str = ""
    size: int = 0
    checksum: str | None = None
    elapsed: float = 0.0


@dataclass(frozen=True)
class DownloadFailed(Event):
    """Download failed."""
    url: str = ""
    file_path: str = ""
    error: str = ""
    attempt: int = 1


@dataclass(frozen=True)
class FolderScanStarted(Event):
    """Folder scan started."""
    url: str = ""


@dataclass(frozen=True)
class FolderScanCompleted(Event):
    """Folder scan completed."""
    url: str = ""
    file_count: int = 0
    total_size: int = 0
    files: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class QueueProcessStarted(Event):
    """Queue processing started."""
    count: int = 0


@dataclass(frozen=True)
class QueueProcessCompleted(Event):
    """Queue processing completed."""
    success: int = 0
    failed: int = 0
    total: int = 0


@dataclass(frozen=True)
class ConversionStarted(Event):
    """Video conversion started."""
    input_path: str = ""
    preset: str = ""


@dataclass(frozen=True)
class ConversionCompleted(Event):
    """Video conversion completed."""
    input_path: str = ""
    output_path: str = ""
    preset: str = ""
    size: int = 0


@dataclass(frozen=True)
class ConversionFailed(Event):
    """Video conversion failed."""
    input_path: str = ""
    preset: str = ""
    error: str = ""


@dataclass(frozen=True)
class StateSaved(Event):
    """Download state saved."""
    state_file: str = ""
    files_tracked: int = 0


class EventBus:
    """Async event bus for publish-subscribe pattern."""

    def __init__(self):
        self._handlers: dict[type[Event], list[Callable[[Event], Any]]] = defaultdict(list)
        self._async_handlers: dict[type[Event], list[Callable[[Event], Coroutine[Any, Any, None]]]] = defaultdict(list)

    def subscribe(self, event_type: type[Event], handler: Callable[[Event], Any]) -> None:
        """Subscribe a sync handler to an event type."""
        self._handlers[event_type].append(handler)

    def subscribe_async(self, event_type: type[Event], handler: Callable[[Event], Coroutine[Any, Any, None]]) -> None:
        """Subscribe an async handler to an event type."""
        self._async_handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type[Event], handler: Callable[[Event], Any]) -> bool:
        """Unsubscribe a handler."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        if handler in self._async_handlers[event_type]:
            self._async_handlers[event_type].remove(handler)
            return True
        return False

    def emit(self, event: Event) -> None:
        """Emit event synchronously (fire and forget for async handlers)."""
        # Call sync handlers
        for handler in self._handlers[type(event)]:
            try:
                handler(event)
            except Exception:
                # Log but don't propagate - event bus must not crash
                pass

        # Schedule async handlers
        for handler in self._async_handlers[type(event)]:
            try:
                asyncio.create_task(handler(event))
            except Exception:
                pass

    async def emit_async(self, event: Event) -> None:
        """Emit event and await all async handlers."""
        # Call sync handlers
        for handler in self._handlers[type(event)]:
            try:
                handler(event)
            except Exception:
                pass

        # Call async handlers and await
        await asyncio.gather(
            *(handler(event) for handler in self._async_handlers[type(event)]),
            return_exceptions=True,
        )

    def clear(self) -> None:
        """Clear all handlers."""
        self._handlers.clear()
        self._async_handlers.clear()


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def set_event_bus(bus: EventBus) -> None:
    """Set global event bus (for testing)."""
    global _event_bus
    _event_bus = bus
