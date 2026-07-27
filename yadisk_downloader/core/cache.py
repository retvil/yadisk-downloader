"""Atomic JSON cache with TTL validation."""

import json
import time
from pathlib import Path
from typing import Any


class Cache:
    """Thread-safe atomic JSON cache with TTL."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 3600):
        """
        Args:
            cache_dir: Directory for cache files.
            ttl_seconds: Time-to-live in seconds (default: 1 hour).
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds

    def _cache_path(self, key: str) -> Path:
        """Generate cache file path from key."""
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"

    def save(self, key: str, data: Any) -> None:
        """
        Atomically save data to cache.

        Args:
            key: Cache key.
            data: Data to cache (must be JSON serializable).
        """
        cache_file = self._cache_path(key)
        payload = {
            "timestamp": time.time(),
            "data": data,
        }

        # Atomic write: tmp file → rename
        tmp_file = cache_file.with_suffix(".tmp")
        with tmp_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        tmp_file.replace(cache_file)

    def load(self, key: str, max_age: int | None = None) -> Any | None:
        """
        Load data from cache if not expired.

        Args:
            key: Cache key.
            max_age: Override TTL for this load (seconds).

        Returns:
            Cached data if valid, None if missing/expired/corrupt.
        """
        cache_file = self._cache_path(key)

        if not cache_file.exists():
            return None

        try:
            with cache_file.open("r", encoding="utf-8") as f:
                payload = json.load(f)

            timestamp = payload.get("timestamp", 0)
            data = payload.get("data")

            if not isinstance(timestamp, (int, float)):
                return None

            ttl = max_age if max_age is not None else self.ttl
            if time.time() - timestamp > ttl:
                return None

            return data

        except (json.JSONDecodeError, KeyError, OSError):
            # Corrupt cache — remove and return None
            try:
                cache_file.unlink(missing_ok=True)
            except OSError:
                pass
            return None

    def delete(self, key: str) -> bool:
        """Delete cache entry. Returns True if existed."""
        cache_file = self._cache_path(key)
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def clear(self) -> int:
        """Clear all cache entries. Returns count removed."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
            count += 1
        return count

    def clear_expired(self) -> int:
        """Remove expired cache entries. Returns count removed."""
        count = 0
        now = time.time()
        for f in self.cache_dir.glob("*.json"):
            try:
                with f.open("r", encoding="utf-8") as fp:
                    payload = json.load(fp)
                timestamp = payload.get("timestamp", 0)
                if isinstance(timestamp, (int, float)) and now - timestamp > self.ttl:
                    f.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Corrupt file — remove it
                try:
                    f.unlink()
                    count += 1
                except OSError:
                    pass
        return count


# Global cache instance for m3u8 playlists
M3U8_CACHE = Cache(Path.home() / ".yadisk-downloader" / "cache" / "m3u8", ttl_seconds=3600)
