"""File downloaders — HLS, API, and browser-based with resume, checksum, and plugin system."""

import hashlib
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .parallel_hls import download_hls_parallel
from .safety import build_proxy_dict
from .auth import get_api_headers

from yadisk_downloader.plugins.base import (
    get_registry,
    FileInfo,
    DownloadContext,
    DownloadResult,
)
from yadisk_downloader.events import (
    get_event_bus,
    DownloadStarted,
    DownloadProgress,
    DownloadCompleted,
    DownloadFailed,
)
from yadisk_downloader.config.schema import get_settings


def compute_checksum(file_path: str, algorithm: str = "md5") -> str:
    """Compute checksum for a file.

    Args:
        file_path: Path to file.
        algorithm: Hash algorithm (md5, sha1, sha256).

    Returns:
        Hex digest string.
    """
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(file_path: str, expected_checksum: str, algorithm: str = "md5") -> bool:
    """Verify file checksum.

    Args:
        file_path: Path to file.
        expected_checksum: Expected hex digest.
        algorithm: Hash algorithm.

    Returns:
        True if checksum matches.
    """
    actual = compute_checksum(file_path, algorithm)
    return actual == expected_checksum


def download_file(
    file_info: FileInfo,
    dest: Path,
    proxy: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    resume: bool = True,
    workers: int = 4,
    ffmpeg_path: Optional[str] = None,
    page=None,  # Playwright page for browser strategies
) -> tuple[bool, int]:
    """Download a file using the plugin system.

    Args:
        file_info: File information including URLs.
        dest: Destination file path.
        proxy: Optional proxy URL.
        progress_callback: Optional callable(downloaded, total).
        resume: Resume interrupted downloads.
        workers: Parallel HLS workers.
        ffmpeg_path: Path to ffmpeg binary.
        page: Playwright page for browser-based strategies.

    Returns:
        Tuple of (success, file_size_bytes).
    """
    settings = get_settings()
    registry = get_registry()
    event_bus = get_event_bus()

    strategy = registry.get_for_file(file_info)
    if not strategy:
        event_bus.emit(DownloadFailed(
            url=file_info.path or "",
            file_path=str(dest),
            error="No strategy available for file type",
        ))
        return False, 0

    # Build context for strategy
    context = DownloadContext(
        settings=settings,
        event_bus=event_bus,
        cache_dir=settings.get_cache_dir(),
        state_dir=settings.get_state_dir(),
        proxy_dict=build_proxy_dict(proxy) if proxy else None,
        oauth_headers=get_api_headers(),
        progress_callback=progress_callback,
    )

    # Emit started event
    event_bus.emit(DownloadStarted(
        url=file_info.download_url or file_info.m3u8_url or file_info.path or "",
        file_path=str(dest),
        file_size=file_info.size,
    ))

    # Try the strategy
    try:
        result: DownloadResult = strategy.download(file_info, dest, context)
        if result.success:
            event_bus.emit(DownloadCompleted(
                url=file_info.path or "",
                file_path=str(dest),
                size=result.size,
                checksum=result.checksum,
            ))
            return True, result.size
        else:
            # Strategy failed, emit failed event
            event_bus.emit(DownloadFailed(
                url=file_info.path or "",
                file_path=str(dest),
                error=result.error or "Unknown error",
            ))
            return False, 0
    except Exception as e:
        event_bus.emit(DownloadFailed(
            url=file_info.path or "",
            file_path=str(dest),
            error=str(e),
        ))
        return False, 0


# ===== Backward compatibility functions =====

def download_hls(
    ffmpeg_path: str | None,
    m3u8_url: str,
    output_path: str,
    proxy: str | None = None,
    workers: int = 4,
) -> tuple[bool, int]:
    """Download HLS stream to file (backward compat)."""
    file_info = FileInfo(
        name=Path(output_path).name,
        path=m3u8_url,
        size=0,
        file_type="video",
        m3u8_url=m3u8_url,
    )
    success, size = download_file(
        file_info=file_info,
        dest=Path(output_path),
        proxy=proxy,
        workers=workers,
        ffmpeg_path=ffmpeg_path,
    )
    return success, size


def download_from_api(
    download_url: str,
    output_path: str,
    proxy: str | None = None,
    progress_callback=None,
    resume: bool = True,
    pool_size: int = 10,
) -> tuple[bool, int]:
    """Download file from a direct URL via HTTP with resume support and connection pooling."""
    file_info = FileInfo(
        name=Path(output_path).name,
        path=download_url,
        size=0,
        file_type="document",
        download_url=download_url,
    )
    success, size = download_file(
        file_info=file_info,
        dest=Path(output_path),
        proxy=proxy,
        progress_callback=progress_callback,
        resume=resume,
    )
    return success, size


def download_via_docviewer(
    page,
    public_key: str,
    file_path: str,
    output_path: str,
    file_type: str = "document",
    timeout: int = 60,
) -> tuple[bool, int]:
    """Download any file via Yandex docviewer rendering (backward compat)."""
    # This requires Playwright page - use browser strategy
    file_info = FileInfo(
        name=Path(output_path).name,
        path=file_path,
        size=0,
        file_type=file_type,
    )
    success, size = download_file(
        file_info=file_info,
        dest=Path(output_path),
        page=page,
    )
    return success, size


def download_via_browser(
    page,
    file_url: str,
    output_path: str,
    timeout: int = 300,
) -> tuple[bool, int]:
    """Download file using Playwright browser download (backward compat)."""
    file_info = FileInfo(
        name=Path(output_path).name,
        path=file_url,
        size=0,
        file_type="document",
        download_url=file_url,
    )
    success, size = download_file(
        file_info=file_info,
        dest=Path(output_path),
        page=page,
    )
    return success, size


# ===== Internal helpers (kept for backward compat) =====

def _download_hls_ffmpeg(
    ffmpeg_path: str,
    m3u8_url: str,
    output_path: str,
    proxy: str | None = None,
) -> tuple[bool, int]:
    """Download HLS stream using ffmpeg."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    cmd = [ffmpeg_path, "-i", m3u8_url, "-c", "copy", "-y", output_path]

    if proxy:
        cmd.extend(["-http_proxy", proxy])

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=3600)
        if result.returncode == 0 and os.path.exists(output_path):
            return True, os.path.getsize(output_path)
        return False, 0
    except Exception:
        return False, 0


def _download_hls_python(
    m3u8_url: str,
    output_path: str,
    workers: int = 8,
) -> tuple[bool, int]:
    """Download HLS stream using pure Python M3U8 parser."""
    from .m3u8_parser import download_hls_python
    return download_hls_python(m3u8_url, output_path, workers=workers)


__all__ = [
    "compute_checksum",
    "verify_checksum",
    "download_file",
    "download_hls",
    "download_from_api",
    "download_via_docviewer",
    "download_via_browser",
    "_download_hls_ffmpeg",
    "_download_hls_python",
]