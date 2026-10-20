"""Dependency injection container for service management."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class Container:
    """Simple DI container with singleton and transient registrations."""

    def __init__(self):
        self._singletons: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}
        self._transients: dict[type, Callable[[], Any]] = {}

    def register_singleton(self, interface: type[T], instance: T) -> None:
        """Register a singleton instance."""
        self._singletons[interface] = instance

    def register_factory(self, interface: type[T], factory: Callable[[], T]) -> None:
        """Register a factory that creates a new instance each time."""
        self._factories[interface] = factory

    def register_transient(self, interface: type[T], factory: Callable[[], T]) -> None:
        """Register a transient (new instance per resolve)."""
        self._transients[interface] = factory

    def get(self, interface: type[T]) -> T:
        """Resolve a dependency."""
        # Check singleton first
        if interface in self._singletons:
            return self._singletons[interface]
        # Check factory
        if interface in self._factories:
            instance = self._factories[interface]()
            self._singletons[interface] = instance  # Cache as singleton
            return instance
        # Check transient
        if interface in self._transients:
            return self._transients[interface]()
        raise KeyError(f"No registration for {interface}")

    def resolve(self, cls: type[T], **kwargs) -> T:
        """Auto-wire and instantiate a class by resolving its constructor dependencies."""
        import inspect
        sig = inspect.signature(cls.__init__)
        params = {}
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if name in kwargs:
                params[name] = kwargs[name]
            elif param.annotation != inspect.Parameter.empty:
                try:
                    params[name] = self.get(param.annotation)
                except KeyError:
                    if param.default != inspect.Parameter.empty:
                        continue
                    raise
        return cls(**params)

    def clear(self) -> None:
        """Clear all registrations."""
        self._singletons.clear()
        self._factories.clear()
        self._transients.clear()


# Global container instance
_container: Container | None = None


def get_container() -> Container:
    """Get global container instance."""
    global _container
    if _container is None:
        _container = Container()
        _setup_default_services(_container)
    return _container


def set_container(container: Container) -> None:
    """Set global container (for testing)."""
    global _container
    _container = container


def _setup_default_services(container: Container) -> None:
    """Register default services."""
    from yadisk_downloader.config.schema import get_settings
    from yadisk_downloader.core.cache import M3U8_CACHE, Cache
    from yadisk_downloader.events.bus import EventBus, get_event_bus

    settings = get_settings()
    container.register_singleton(type(settings), settings)
    container.register_singleton(EventBus, get_event_bus())
    container.register_singleton(Cache, M3U8_CACHE)
    # HTTP client will be registered on first use
