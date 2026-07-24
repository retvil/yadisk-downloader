"""Pure Python M3U8 HLS playlist parser and downloader.

Alternative to ffmpeg for downloading HLS streams. Parses M3U8 playlists,
selects resolution, downloads .ts segments, and merges them into a single file.
"""

import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_m3u8(content: str, base_url: str) -> dict:
    """Parse M3U8 playlist content.

    Args:
        content: Raw M3U8 text content.
        base_url: Base URL for resolving relative paths.

    Returns:
        Dict with keys:
            - type: "master" or "media"
            - version: protocol version
            - target_duration: target segment duration
            - segments: list of segment dicts (for media playlists)
            - variants: list of variant dicts (for master playlists)
    """
    result = {
        "type": "media",
        "version": None,
        "target_duration": None,
        "segments": [],
        "variants": [],
    }

    lines = content.strip().splitlines()
    current_tags = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("#EXT"):
            # Parse tag — match full tag name including hyphens
            tag_match = re.match(r"#(EXT[^:,]+):?(.*)", line)
            if tag_match:
                tag_name = tag_match.group(1).strip()
                tag_value = tag_match.group(2).strip()

                if tag_name == "M3U":
                    continue
                elif tag_name == "VERSION":
                    result["version"] = int(tag_value) if tag_value else None
                elif tag_name == "TARGETDURATION":
                    result["target_duration"] = int(tag_value) if tag_value else None
                elif tag_name == "EXT-X-STREAM-INF":
                    result["type"] = "master"
                    attrs = _parse_attrs(tag_value)
                    current_tags = attrs
                elif tag_name == "EXT-X-MEDIA":
                    pass
        else:
            # This is a URL line
            url = _resolve_url(line, base_url)

            if result["type"] == "master" and current_tags:
                variant = {
                    "url": url,
                    "bandwidth": current_tags.get("BANDWIDTH", 0),
                    "resolution": current_tags.get("RESOLUTION", ""),
                    "codecs": current_tags.get("CODECS", ""),
                    "name": current_tags.get("NAME", ""),
                }
                result["variants"].append(variant)
                current_tags = {}
            elif result["type"] == "media" or result["segments"]:
                result["type"] = "media"
                segment = {"url": url, "duration": 0}
                result["segments"].append(segment)

    # Fix: if we found variants but type was set to media, fix it
    if result["variants"] and result["type"] == "media":
        result["type"] = "master"

    return result


def _parse_attrs(value: str) -> dict:
    """Parse EXT-X-STREAM-INF attributes."""
    attrs = {}
    # Split by comma but not within quotes
    parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', value)
    for part in parts:
        part = part.strip()
        if "=" in part:
            key, val = part.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"')
            if key == "BANDWIDTH":
                try:
                    attrs[key] = int(val)
                except ValueError:
                    attrs[key] = 0
            else:
                attrs[key] = val
    return attrs


def _resolve_url(url: str, base_url: str) -> str:
    """Resolve relative URL against base URL."""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    # Resolve relative to base URL
    parsed = urllib.parse.urlparse(base_url)
    base_dir = parsed.path.rsplit("/", 1)[0] + "/"
    resolved = urllib.parse.urljoin(parsed.scheme + "://" + parsed.netloc + base_dir, url)
    return resolved


def _parse_resolution(resolution: str) -> tuple[int, int]:
    """Parse resolution string like '1920x1080' to (width, height)."""
    if not resolution:
        return (0, 0)
    parts = resolution.split("x")
    if len(parts) == 2:
        try:
            return (int(parts[0]), int(parts[1]))
        except ValueError:
            pass
    return (0, 0)


def select_best_variant(variants: list[dict], target_height: int = 720) -> dict | None:
    """Select best variant matching target resolution.

    Args:
        variants: List of variant dicts from parse_m3u8().
        target_height: Target height in pixels (default 720 for 720p).

    Returns:
        Best matching variant, or highest available if no match.
    """
    if not variants:
        return None

    # Parse resolutions
    for v in variants:
        w, h = _parse_resolution(v.get("resolution", ""))
        v["_height"] = h

    # Try exact match
    for v in variants:
        if v["_height"] == target_height:
            return v

    # Try closest below
    candidates = [v for v in variants if v["_height"] <= target_height]
    if candidates:
        return max(candidates, key=lambda v: v["_height"])

    # Use lowest available (most conservative)
    return min(variants, key=lambda v: v["_height"] if v["_height"] > 0 else float("inf"))


def fetch_url(url: str, timeout: int = 30) -> bytes:
    """Fetch URL content."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
    })

    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return resp.read()


def download_segment(url: str, output_path: str, timeout: int = 30) -> bool:
    """Download a single .ts segment."""
    try:
        data = fetch_url(url, timeout)
        with open(output_path, "ab") as f:
            f.write(data)
        return True
    except Exception:
        return False


def download_hls_python(
    m3u8_url: str,
    output_path: str,
    proxy: str | None = None,
    workers: int = 8,
    progress_callback=None,
) -> tuple[bool, int]:
    """Download HLS stream using pure Python (no ffmpeg).

    Args:
        m3u8_url: HLS m3u8 playlist URL.
        output_path: Destination file path.
        proxy: Optional proxy URL (not yet supported for Python downloader).
        workers: Number of parallel download workers.
        progress_callback: Optional callable(downloaded, total).

    Returns:
        Tuple of (success, file_size_bytes).
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    try:
        # Step 1: Fetch master playlist
        content = fetch_url(m3u8_url).decode("utf-8", errors="replace")
        playlist = parse_m3u8(content, m3u8_url)

        # Step 2: If master playlist, select best variant and fetch media playlist
        if playlist["type"] == "master" and playlist["variants"]:
            variant = select_best_variant(playlist["variants"])
            if not variant:
                return False, 0

            media_content = fetch_url(variant["url"]).decode("utf-8", errors="replace")
            playlist = parse_m3u8(media_content, variant["url"])

        # Step 3: Check if segments are encrypted
        # For now, only handle unencrypted streams
        if not playlist["segments"]:
            return False, 0

        # Step 4: Download all segments
        total = len(playlist["segments"])
        downloaded = 0

        # Clean output file
        if os.path.exists(output_path):
            os.remove(output_path)

        # Download segments in parallel
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {}
            for i, segment in enumerate(playlist["segments"]):
                future = executor.submit(
                    _download_segment_to_temp,
                    segment["url"],
                    output_path,
                    i,
                )
                futures[future] = i

            # Collect results in order
            segment_data = [None] * total
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    data = future.result()
                    segment_data[idx] = data
                except Exception:
                    pass
                downloaded += 1
                if progress_callback:
                    progress_callback(downloaded, total)

        # Step 5: Merge segments in order
        with open(output_path, "wb") as f:
            for data in segment_data:
                if data:
                    f.write(data)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True, os.path.getsize(output_path)
        return False, 0

    except Exception:
        return False, 0


def _download_segment_to_temp(url: str, output_path: str, index: int) -> bytes:
    """Download a segment and return its data."""
    try:
        return fetch_url(url)
    except Exception:
        return b""


def get_m3u8_info(m3u8_url: str) -> dict:
    """Get info about an M3U8 playlist without downloading.

    Returns:
        Dict with type, variants/segments count, total duration, etc.
    """
    try:
        content = fetch_url(m3u8_url).decode("utf-8", errors="replace")
        playlist = parse_m3u8(content, m3u8_url)

        info = {
            "type": playlist["type"],
            "version": playlist["version"],
            "target_duration": playlist["target_duration"],
        }

        if playlist["type"] == "master":
            info["variants"] = len(playlist["variants"])
            for v in playlist["variants"]:
                w, h = _parse_resolution(v.get("resolution", ""))
                v["height"] = h
            info["resolutions"] = [
                f"{v.get('resolution', '?')} ({v.get('bandwidth', 0)} bps)"
                for v in sorted(playlist["variants"], key=lambda x: x.get("bandwidth", 0), reverse=True)
            ]
        else:
            info["segments"] = len(playlist["segments"])
            total_duration = sum(s.get("duration", 0) for s in playlist["segments"])
            info["total_duration"] = total_duration

        return info
    except Exception as e:
        return {"error": str(e)}
