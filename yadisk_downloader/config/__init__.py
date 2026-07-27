"""Configuration module exports."""

from .schema import (
    Settings,
    DownloadSettings,
    ProxySettings,
    NotificationSettings,
    SchedulerSettings,
    get_settings,
    get_config,
    reload_settings,
)

# Alias for backward compatibility
Config = Settings
get_config_path = get_settings

__all__ = [
    "Config",
    "Settings",
    "DownloadSettings",
    "ProxySettings",
    "NotificationSettings",
    "SchedulerSettings",
    "get_settings",
    "get_config",
    "get_config_path",
    "reload_settings",
]