"""Configuration file management for yadisk-downloader."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

CONFIG_DIR = Path.home() / ".yadisk-downloader"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "resolution": "720p",
    "output_dir": "./downloads",
    "proxy": None,
    "notify": False,
    "workers": 4,
    "preset": None,
    "delete_original": False,
}


@dataclass
class Config:
    """Application configuration."""
    resolution: str = "720p"
    output_dir: str = "./downloads"
    proxy: str | None = None
    notify: bool = False
    workers: int = 4
    preset: str | None = None
    delete_original: bool = False

    def save(self, path: Path | None = None):
        """Save config to file."""
        path = path or CONFIG_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """Load config from file. Returns defaults if file doesn't exist."""
        path = path or CONFIG_FILE
        if not path.exists():
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return cls()


def get_config_path() -> Path:
    """Get the default config file path."""
    return CONFIG_FILE
