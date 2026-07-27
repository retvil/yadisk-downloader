"""Parallel HLS segment downloader with ThreadPoolExecutor."""

import os
import tempfile
import time
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .m3u8_parser import parse_m3u8


def download_hls_parallel(
    m3u8_url: str,
    output_path: Path,
    workers: int = 4,
    headers: dict | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> Path:
    """
    Download HLS segments in parallel using ThreadPoolExecutor.

    Args:
        m3u8_url: URL of the m3u8 playlist.
        output_path: Path to write the final concatenated file.
        workers: Number of parallel download workers (default: 4, max: 16).
        headers: Optional HTTP headers for requests.
        progress_callback: Optional callable(completed, total) called after each segment.

    Returns:
        Path to the downloaded file.

    Raises:
        ValueError: If workers is out of range or m3u8 parsing fails.
        RuntimeError: If download fails after retries.
    """
    if not 1 <= workers <= 16:
        raise ValueError(f"workers must be 1-16, got {workers}")

    # Parse m3u8 playlist
    try:
        playlist = parse_m3u8(m3u8_url, headers)
    except Exception as e:
        raise ValueError(f"Failed to parse m3u8: {e}") from e

    segments = playlist.get("segments", [])
    if not segments:
        raise ValueError("No segments found in m3u8 playlist")

    segment_urls = [seg.get("uri") for seg in segments if seg.get("uri")]
    if not segment_urls:
        raise ValueError("No valid segment URIs in m3u8 playlist")

    total_segments = len(segment_urls)
    completed = 0

    def download_segment(idx: int, url: str) -> bytes:
        """Download a single segment with retry logic."""
        nonlocal completed
        last_error = None

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=headers or {})
                with urllib.request.urlopen(req, timeout=30) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = response.headers.get("Retry-After")
                        wait_time = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                        time.sleep(wait_time)
                        continue

                    data = response.read()
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_segments)
                    return data

            except urllib.error.HTTPError as e:
                last_error = e
                if e.code == 429:
                    retry_after = e.headers.get("Retry-After")
                    wait_time = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                    time.sleep(wait_time)
                    continue
                if e.code >= 500:
                    time.sleep(2 ** attempt)
                    continue
                raise

            except Exception as e:
                last_error = e
                time.sleep(2 ** attempt)

        raise RuntimeError(f"Failed to download segment {idx} ({url}) after 3 attempts: {last_error}")

    # Download all segments in parallel
    segment_data = [None] * total_segments

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_idx = {
            executor.submit(download_segment, idx, url): idx
            for idx, url in enumerate(segment_urls)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                segment_data[idx] = future.result()
            except Exception as e:
                raise RuntimeError(f"Segment {idx} failed: {e}") from e

    # Write concatenated result atomically
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=output_path.parent,
        delete=False,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    ) as tmp:
        tmp_path = Path(tmp.name)
        for data in segment_data:
            if data is None:
                raise RuntimeError("Missing segment data")
            tmp.write(data)

    # Atomic rename
    os.replace(tmp_path, output_path)

    return output_path


def download_hls_parallel_sync(
    m3u8_url: str,
    output_path: Path,
    workers: int = 4,
    headers: dict | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> Path:
    """
    Synchronous wrapper for download_hls_parallel (same function, explicit name).

    Args:
        m3u8_url: URL of the m3u8 playlist.
        output_path: Path to write the final concatenated file.
        workers: Number of parallel download workers (default: 4, max: 16).
        headers: Optional HTTP headers for requests.
        progress_callback: Optional callable(completed, total) called after each segment.

    Returns:
        Path to the downloaded file.
    """
    return download_hls_parallel(
        m3u8_url=m3u8_url,
        output_path=output_path,
        workers=workers,
        headers=headers,
        progress_callback=progress_callback,
    )
