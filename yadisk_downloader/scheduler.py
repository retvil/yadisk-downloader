"""Scheduled download support using cron-like expressions."""

import json
import os
import signal
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path


SCHEDULER_DIR = Path.home() / ".yadisk-downloader"
SCHEDULE_FILE = SCHEDULER_DIR / "schedule.json"
PID_FILE = SCHEDULER_DIR / "scheduler.pid"


@dataclass
class ScheduleEntry:
    """A scheduled download task."""
    url: str
    cron: str  # "minute hour day month weekday"
    folder: str | None = None
    preset: str | None = None
    resolution: str = "720p"
    output: str = "./downloads"
    active: bool = True
    last_run: float = 0.0
    next_run: float = 0.0


@dataclass
class ScheduleConfig:
    """Scheduler configuration."""
    entries: list[ScheduleEntry] = None

    def __post_init__(self):
        if self.entries is None:
            self.entries = []

    def add(self, url: str, cron: str, **kwargs):
        """Add a schedule entry."""
        entry = ScheduleEntry(url=url, cron=cron, **kwargs)
        entry.next_run = self._parse_cron(cron)
        self.entries.append(entry)
        return entry

    def remove(self, url: str):
        """Remove a schedule entry by URL."""
        self.entries = [e for e in self.entries if e.url != url]

    def _parse_cron(self, cron: str) -> float:
        """Parse cron expression and return next execution time.

        Simplified cron: "minute hour day month weekday"
        Supports: * (any), numbers, */N (every N)
        """
        parts = cron.split()
        if len(parts) != 5:
            return time.time() + 3600  # Default: 1 hour from now

        now = time.localtime()
        minute = self._parse_field(parts[0], now.tm_min, 0, 59)
        hour = self._parse_field(parts[1], now.tm_hour, 0, 23)

        # Simple: just compute next matching time
        # For full cron we'd need more logic, but this covers common cases
        target = time.mktime((
            now.tm_year, now.tm_mon, now.tm_mday,
            hour, minute, 0, 0, 0, -1
        ))

        if target <= time.time():
            target += 86400  # Next day if time already passed

        return target

    def _parse_field(self, field: str, current: int, min_val: int, max_val: int) -> int:
        """Parse a single cron field."""
        if field == "*":
            return current
        if field.startswith("*/"):
            interval = int(field[2:])
            return (current // interval + 1) * interval % (max_val + 1)
        return int(field)

    def get_due(self) -> list[ScheduleEntry]:
        """Get entries that are due for execution."""
        now = time.time()
        return [e for e in self.entries if e.active and e.next_run <= now]

    def save(self, path: Path | None = None):
        """Save schedule to file."""
        path = path or SCHEDULE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "entries": [asdict(e) for e in self.entries],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path | None = None) -> "ScheduleConfig":
        """Load schedule from file."""
        path = path or SCHEDULE_FILE
        if not path.exists():
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries = [ScheduleEntry(**e) for e in data.get("entries", [])]
            return cls(entries=entries)
        except Exception:
            return cls()

    def show(self):
        """Print schedule status."""
        if not self.entries:
            print("No scheduled downloads")
            return

        print(f"Scheduled downloads ({len(self.entries)} entries):\n")
        for i, entry in enumerate(self.entries, 1):
            status = "active" if entry.active else "paused"
            next_run = time.strftime("%Y-%m-%d %H:%M", time.localtime(entry.next_run))
            print(f"  {i}. [{status}] {entry.url[:50]}...")
            print(f"     Cron: {entry.cron} | Next: {next_run}")


def is_running() -> bool:
    """Check if scheduler is already running."""
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)  # Check if process exists
        return True
    except (ProcessLookupError, ValueError):
        PID_FILE.unlink(missing_ok=True)
        return False


def save_pid():
    """Save current process PID."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))


def remove_pid():
    """Remove PID file."""
    PID_FILE.unlink(missing_ok=True)
