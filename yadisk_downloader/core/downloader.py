"""File downloaders — HLS, API, and browser-based with resume and checksum."""

import hashlib
import os
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import ssl


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


def download_hls(
    ffmpeg_path: str,
    m3u8_url: str,
    output_path: str,
    proxy: str | None = None,
) -> tuple[bool, int]:
    """Download HLS stream to file using ffmpeg.

    Args:
        ffmpeg_path: Path to ffmpeg binary.
        m3u8_url: HLS m3u8 playlist URL.
        output_path: Destination file path.
        proxy: Optional proxy URL.

    Returns:
        Tuple of (success, file_size_bytes).
    """
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


def download_from_api(
    download_url: str,
    output_path: str,
    proxy: str | None = None,
    progress_callback=None,
    resume: bool = True,
) -> tuple[bool, int]:
    """Download file from a direct URL via HTTP with resume support.

    Args:
        download_url: Direct download URL.
        output_path: Destination file path.
        proxy: Optional proxy URL (e.g. "http://proxy:8080").
        progress_callback: Optional callable(bytes_downloaded, total_size).
        resume: If True, resume from where we left off.

    Returns:
        Tuple of (success, file_size_bytes).
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Setup proxy
    handlers = [ssl.HTTPSHandler(context=ctx)]
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({
            "http": proxy,
            "https": proxy,
        })
        handlers.append(proxy_handler)

    opener = urllib.request.build_opener(*handlers)

    # Check for partial download
    downloaded = 0
    if resume and os.path.exists(output_path):
        downloaded = os.path.getsize(output_path)

    for attempt in range(3):
        try:
            req = urllib.request.Request(download_url)

            # Add Range header for resume
            if downloaded > 0:
                req.add_header("Range", f"bytes={downloaded}-")

            with opener.open(req, timeout=600) as resp:
                # Check if server supports range requests
                status_code = resp.getcode()
                if status_code == 206:
                    # Partial content - resume
                    pass
                elif status_code == 200:
                    # Full content - start from beginning
                    downloaded = 0

                total_size = int(resp.headers.get("Content-Length", 0))
                if status_code == 200:
                    total_size = total_size  # Full size
                elif status_code == 206:
                    total_size = downloaded + total_size  # Remaining + already downloaded

                mode = "ab" if downloaded > 0 and status_code == 206 else "wb"
                with open(output_path, mode) as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            if os.path.exists(output_path):
                return True, os.path.getsize(output_path)
            return False, 0
        except Exception:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return False, 0


def download_via_docviewer(
    page,
    public_key: str,
    file_path: str,
    output_path: str,
    timeout: int = 60,
) -> tuple[bool, int]:
    """Download a document (PDF, etc.) via Yandex docviewer rendering.

    Opens the file in docviewer, waits for it to render, then uses
    page.pdf() to save the rendered content as a valid PDF file.

    Args:
        page: Playwright page object (must already be on a page or new page).
        public_key: Yandex Disk public folder URL.
        file_path: Path to file on Yandex Disk (e.g. "/file.pdf").
        output_path: Destination file path.
        timeout: Max seconds to wait for rendering.

    Returns:
        Tuple of (success, file_size_bytes).
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    try:
        # Step 1: Load the folder page to get store-prefetch data
        page.goto(public_key, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Step 2: Extract dvSearch URL for the target file
        dv_search = page.evaluate("""(filePath) => {
            const script = document.getElementById('store-prefetch');
            if (!script) return null;
            const data = JSON.parse(script.textContent);
            const resources = data.resources || {};
            const root = resources[data.rootResourceId];
            if (!root) return null;
            for (const childId of (root.children || [])) {
                const child = resources[childId];
                if (child && child.path && child.path.includes(filePath)) {
                    return child.dvSearch || null;
                }
            }
            return null;
        }""", file_path)

        if not dv_search:
            return False, 0

        # Step 3: Navigate to docviewer
        dv_url = f"https://docviewer.yandex.ru{dv_search}"
        page.goto(dv_url, wait_until="domcontentloaded", timeout=30000)

        # Step 4: Wait for rendering — check for htmlimage (docviewer renders pages as PNGs)
        deadline = time.time() + timeout
        while time.time() < deadline:
            has_image = page.evaluate("""() => {
                return document.querySelectorAll('img[src*="htmlimage"]').length > 0;
            }""")
            if has_image:
                time.sleep(2)  # Extra time for full render
                break
            time.sleep(1)

        # Step 5: Save as PDF via page.pdf()
        page.pdf(path=output_path, print_background=True)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return True, os.path.getsize(output_path)
        return False, 0

    except Exception:
        return False, 0


def download_via_browser(
    page,
    file_url: str,
    output_path: str,
    timeout: int = 300,
) -> tuple[bool, int]:
    """Download file using Playwright browser download.

    Args:
        page: Playwright page object.
        file_url: URL to navigate to for download.
        output_path: Destination file path.
        timeout: Download timeout in seconds.

    Returns:
        Tuple of (success, file_size_bytes).
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    try:
        with page.expect_download(timeout=timeout * 1000) as download_info:
            page.goto(file_url, wait_until="load", timeout=30000)
            time.sleep(2)

            # Try to find and click download button
            download_selectors = [
                "button:has-text('Скачать')",
                "button:has-text('Download')",
                "[data-t='download-button']",
                "a[download]",
                ".download-button",
            ]
            for sel in download_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=1000):
                        btn.click()
                        break
                except Exception:
                    continue

        download = download_info.value
        download.save_as(output_path)

        if os.path.exists(output_path):
            return True, os.path.getsize(output_path)
        return False, 0

    except Exception:
        return False, 0
