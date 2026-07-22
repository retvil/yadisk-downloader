"""Download state tracking for resume support."""

import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path


STATE_DIR = Path.home() / ".yadisk-downloader"
STATE_FILE = STATE_DIR / "state.json"


@dataclass
class FileState:
    """State of a single file download."""
    path: str
    name: str
    size: int
    downloaded: int
    checksum: str | None = None
    status: str = "pending"  # pending, downloading, done, failed
    timestamp: float = 0.0


@dataclass
class DownloadState:
    """Overall download session state."""
    url: str
    files: dict[str, FileState] = None
    last_updated: float = 0.0

    def __post_init__(self):
        if self.files is None:
            self.files = {}

    def save(self, path: Path | None = None):
        """Save state to file."""
        path = path or STATE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        self.last_updated = time.time()
        data = {
            "url": self.url,
            "files": {k: asdict(v) for k, v in self.files.items()},
            "last_updated": self.last_updated,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path | None = None) -> "DownloadState | None":
        """Load state from file. Returns None if not found."""
        path = path or STATE_FILE
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
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

    def get_file(self, file_path: str) -> FileState | None:
        """Get state for a specific file."""
        return self.files.get(file_path)

    def update_file(self, file_path: str, **kwargs):
        """Update state for a specific file."""
        if file_path not in self.files:
            self.files[file_path] = FileState(path=file_path, name="", size=0, downloaded=0)
        for key, value in kwargs.items():
            setattr(self.files[file_path], key, value)
        self.files[file_path].timestamp = time.time()

    def clear(self, path: Path | None = None):
        """Clear state file."""
        path = path or STATE_FILE
        if path.exists():
            path.unlink()


def get_state_file(url: str) -> Path:
    """Get state file path for a URL."""
    # Use URL hash as filename
    import hashlib
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return STATE_DIR / f"state_{url_hash}.json"
