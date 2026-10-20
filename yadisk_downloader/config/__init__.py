"""Configuration module exports.

Two config systems live here:
- ``cli_config.Config`` — flat dataclass backed by ``~/.yadisk-downloader/config.json``,
  used by the CLI.
- ``schema.Settings`` — pydantic, env-based, used by plugins/core.
"""

from .cli_config import CONFIG_DIR, CONFIG_FILE, Config, get_config_path
from .schema import (
    DownloadSettings,
    NotificationSettings,
    ProxySettings,
    SchedulerSettings,
    Settings,
    get_config,
    get_settings,
    reload_settings,
)

__all__ = [
    "CONFIG_DIR",
    "CONFIG_FILE",
    "Config",
    "get_config_path",
    "Settings",
    "DownloadSettings",
    "ProxySettings",
    "NotificationSettings",
    "SchedulerSettings",
    "get_settings",
    "get_config",
    "reload_settings",
]
