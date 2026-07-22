"""Download queue management for multiple URLs."""

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


QUEUE_DIR = Path.home() / ".yadisk-downloader"
QUEUE_FILE = QUEUE_DIR / "queue.json"


@dataclass
class QueueItem:
    """A single item in the download queue."""
    url: str
    status: str = "pending"  # pending, downloading, done, failed
    folder: str | None = None
    preset: str | None = None
    error: str | None = None
    timestamp: float = 0.0


@dataclass
class DownloadQueue:
    """Download queue for multiple URLs."""
    items: list[QueueItem] = field(default_factory=list)

    def add(self, url: str, folder: str | None = None, preset: str | None = None):
        """Add a URL to the queue."""
        # Check for duplicates
        for item in self.items:
            if item.url == url and item.status in ("pending", "downloading"):
                return False
        self.items.append(QueueItem(url=url, folder=folder, preset=preset))
        return True

    def remove(self, url: str):
        """Remove a URL from the queue."""
        self.items = [i for i in self.items if i.url != url]

    def get_pending(self) -> list[QueueItem]:
        """Get all pending items."""
        return [i for i in self.items if i.status == "pending"]

    def update(self, url: str, status: str, error: str | None = None):
        """Update status of a queue item."""
        for item in self.items:
            if item.url == url:
                item.status = status
                item.error = error
                item.timestamp = time.time()
                break

    def save(self, path: Path | None = None):
        """Save queue to file."""
        path = path or QUEUE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "items": [asdict(i) for i in self.items],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path | None = None) -> "DownloadQueue":
        """Load queue from file."""
        path = path or QUEUE_FILE
        if not path.exists():
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = [QueueItem(**item) for item in data.get("items", [])]
            return cls(items=items)
        except Exception:
            return cls()

    def clear(self, path: Path | None = None):
        """Clear queue file."""
        path = path or QUEUE_FILE
        if path.exists():
            path.unlink()

    def show(self):
        """Print queue status."""
        if not self.items:
            print("Queue is empty")
            return

        status_icons = {
            "pending": "[ ]",
            "downloading": "[>]",
            "done": "[v]",
            "failed": "[x]",
        }

        print(f"Download queue ({len(self.items)} items):\n")
        for i, item in enumerate(self.items, 1):
            icon = status_icons.get(item.status, "[?]")
            folder = f" [{item.folder}]" if item.folder else ""
            error = f" - {item.error}" if item.error else ""
            print(f"  {i}. {icon} {item.url[:60]}...{folder}{error}")
