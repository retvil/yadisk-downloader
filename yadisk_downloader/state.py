"""Download state tracking for resume support with crash resilience."""

import json
import time
import hashlib
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from yadisk_downloader.config.schema import get_settings


@dataclass
class FileState:
    """State of a single file download."""
    path: str
    name: str
    size: int
    downloaded: int
    checksum: Optional[str] = None
    status: str = "pending"  # pending, downloading, done, failed
    timestamp: float = 0.0


@dataclass
class DownloadState:
    """Overall download session state."""
    url: str
    files: dict[str, FileState] = None
    last_updated: float = 0.0
    _flush_interval: int = 1024 * 1024  # 1MB
    _bytes_since_flush: int = 0
    _dirty_files: set[str] = None

    def __post_init__(self):
        if self.files is None:
            self.files = {}
        if self._dirty_files is None:
            self._dirty_files = set()

    @property
    def state_dir(self) -> Path:
        """Get state directory from settings."""
        return get_settings().get_state_dir()

    def _get_state_file(self) -> Path:
        """Get state file path for this URL."""
        url_hash = hashlib.md5(self.url.encode()).hexdigest()[:12]
        return self.state_dir / f"state_{url_hash}.json"

    def save(self, path: Optional[Path] = None):
        """Save state to file atomically."""
        path = path or self._get_state_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.last_updated = time.time()
        data = {
            "url": self.url,
            "files": {k: asdict(v) for k, v in self.files.items()},
            "last_updated": self.last_updated,
        }
        # Atomic write: tmp -> rename
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)
        self._bytes_since_flush = 0
        self._dirty_files.clear()

    @classmethod
    def load(cls, path: Optional[Path] = None, url: Optional[str] = None) -> Optional["DownloadState"]:
        """Load state from file. Returns None if not found or corrupt."""
        if path is None:
            if url is None:
                return None
            state_dir = get_settings().get_state_dir()
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            path = state_dir / f"state_{url_hash}.json"
        if not path.exists():
            return None
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            files = {
                k: FileState(**v)
                for k, v in data.get("files", {}).items()
            }
            return cls(
                url=data["url"],
                files=files,
                last_updated=data.get("last_updated", 0),
            )
        except Exception:
            return None

    def get_file(self, file_path: str) -> Optional[FileState]:
        """Get state for a specific file."""
        return self.files.get(file_path)

    def update_file(self, file_path: str, downloaded_delta: int = 0, **kwargs):
        """Update state for a specific file with periodic flush."""
        if file_path not in self.files:
            self.files[file_path] = FileState(path=file_path, name="", size=0, downloaded=0)
        state = self.files[file_path]
        for key, value in kwargs.items():
            setattr(state, key, value)
        if downloaded_delta:
            state.downloaded += downloaded_delta
            self._bytes_since_flush += downloaded_delta
        state.timestamp = time.time()
        self._dirty_files.add(file_path)

        # Periodic flush
        if self._bytes_since_flush >= self._flush_interval:
            self.flush()

    def flush(self):
        """Flush dirty files to disk."""
        if self._dirty_files:
            self.save()
            self._bytes_since_flush = 0

    def clear(self, path: Optional[Path] = None):
        """Clear state file."""
        path = path or self._get_state_file()
        if path.exists():
            path.unlink(missing_ok=True)
        if path.with_suffix(".tmp").exists():
            path.with_suffix(".tmp").unlink(missing_ok=True)

    @contextmanager
    def transaction(self):
        """Context manager for atomic state updates. Flushes on exit."""
        try:
            yield self
        finally:
            self.flush()


def get_state_file(url: str) -> Path:
    """Get state file path for a URL."""
    return DownloadState(url=url)._get_state_file()