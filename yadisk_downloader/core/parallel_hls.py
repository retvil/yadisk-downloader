"""Parallel HLS segment downloader with ThreadPoolExecutor."""

import os
import shutil
import tempfile
import time
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .m3u8_parser import fetch_url, parse_m3u8, select_best_variant


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

    # Fetch and parse m3u8 playlist (handle master playlists with variants)
    try:
        content = fetch_url(m3u8_url, headers=headers).decode("utf-8", errors="replace")
        playlist = parse_m3u8(content, m3u8_url)

        if playlist["type"] == "master" and playlist["variants"]:
            variant = select_best_variant(playlist["variants"])
            if not variant:
                raise ValueError("No suitable variant found in master playlist")
            media_content = fetch_url(variant["url"], headers=headers).decode("utf-8", errors="replace")
            playlist = parse_m3u8(media_content, variant["url"])
    except Exception as e:
        raise ValueError(f"Failed to fetch/parse m3u8: {e}") from e

    segments = playlist.get("segments", [])
    if not segments:
        raise ValueError("No segments found in m3u8 playlist")

    segment_urls = [seg.get("url") for seg in segments if seg.get("url")]
    if not segment_urls:
        raise ValueError("No valid segment URIs in m3u8 playlist")

    total_segments = len(segment_urls)
    completed = 0

    def download_segment(idx: int, url: str) -> Path:
        """Download a single segment to a part file with retry logic."""
        nonlocal completed
        last_error = None
        part_path = parts_dir / f"seg_{idx:06d}.ts"

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

                    # Stream to disk — segments must not accumulate in RAM
                    with open(part_path, "wb") as f:
                        shutil.copyfileobj(response, f)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_segments)
                    return part_path

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

    # Segments are written to part files next to the output — the whole video
    # must never be held in RAM (multi-GB streams would OOM)
    parts_dir = output_path.parent / f".{output_path.name}.hls_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Download all segments in parallel
        segment_paths: list[Path | None] = [None] * total_segments

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_idx = {
                executor.submit(download_segment, idx, url): idx
                for idx, url in enumerate(segment_urls)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    segment_paths[idx] = future.result()
                except Exception as e:
                    raise RuntimeError(f"Segment {idx} failed: {e}") from e

        # Write concatenated result atomically, streaming part files from disk
        output_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=output_path.parent,
                delete=False,
                prefix=f".{output_path.name}.",
                suffix=".tmp",
            ) as tmp:
                tmp_path = Path(tmp.name)
                for part in segment_paths:
                    if part is None:
                        raise RuntimeError("Missing segment data")
                    with open(part, "rb") as pf:
                        shutil.copyfileobj(pf, tmp)

            # Atomic rename
            os.replace(tmp_path, output_path)
        except Exception:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)
            raise
    finally:
        shutil.rmtree(parts_dir, ignore_errors=True)

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
