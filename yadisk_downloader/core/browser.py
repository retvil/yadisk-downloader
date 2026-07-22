"""Playwright browser — HLS m3u8 URL interception and file downloads for Yandex Disk."""

import re
import time


def close_all_dialogs(page) -> None:
    """Aggressively close any open dialogs/panels/overlays."""
    for _ in range(5):
        try:
            page.keyboard.press("Escape")
            time.sleep(0.3)
        except Exception:
            pass
    for sel in [
        "button[aria-label='Закрыть']",
        "[aria-modal='true'] button",
        ".slider button",
    ]:
        try:
            page.locator(sel).first.click(timeout=500)
            time.sleep(0.2)
        except Exception:
            pass
    time.sleep(0.3)


def collect_m3u8_urls(
    public_key: str,
    files: list[dict],
    resolution: str = "720p",
    progress_callback=None,
) -> dict[str, str | None]:
    """Collect m3u8 URLs for all files using Playwright.

    Args:
        public_key: Yandex Disk public link.
        files: List of file dicts from api.list_files().
        resolution: Target resolution (e.g. "720p").
        progress_callback: Optional callable(current, total, filename).

    Returns:
        Dict mapping file path to m3u8 URL (or None if not found).
    """
    from playwright.sync_api import sync_playwright

    m3u8_map = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # Group files by folder
        folders: dict[str, list[dict]] = {}
        for f in files:
            folder = f["folder"]
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(f)

        file_idx = 0
        total_files = len(files)

        for folder_name, folder_files in folders.items():
            # Navigate to root
            page.goto(public_key, wait_until="load", timeout=45000)
            time.sleep(3)
            try:
                page.locator("button:has-text('Разрешить все')").click(timeout=2000)
                time.sleep(1)
            except Exception:
                pass

            # Navigate into folder
            if folder_name:
                try:
                    page.locator(f"text='{folder_name}'").first.dblclick()
                    time.sleep(3)
                    close_all_dialogs(page)
                except Exception:
                    continue

            for f in folder_files:
                file_idx += 1
                if progress_callback:
                    progress_callback(file_idx, total_files, f["name"])

                # Skip if already downloaded
                m3u8_urls = []

                def on_response(response):
                    if ".m3u8" in response.url:
                        m3u8_urls.append(response.url)

                page.on("response", on_response)

                try:
                    close_all_dialogs(page)
                    page.locator(f"text='{f['name']}'").first.dblclick()
                    time.sleep(6)

                    # Try to play video
                    videos = page.query_selector_all("video")
                    if videos:
                        try:
                            videos[0].evaluate("el => el.play()")
                            time.sleep(4)
                        except Exception:
                            pass
                        try:
                            box = videos[0].bounding_box()
                            if box:
                                page.mouse.click(
                                    box["x"] + box["width"] / 2,
                                    box["y"] + box["height"] / 2,
                                )
                                time.sleep(4)
                        except Exception:
                            pass

                    # Check page source for m3u8
                    if not m3u8_urls:
                        content = page.content()
                        found = re.findall(
                            r'https?://streaming\.disk\.yandex\.net/hls/[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                            content,
                        )
                        m3u8_urls.extend(found)

                    best = _select_resolution(m3u8_urls, resolution)
                    m3u8_map[f["path"]] = best

                except Exception:
                    m3u8_map[f["path"]] = None
                finally:
                    page.remove_listener("response", on_response)
                    close_all_dialogs(page)

        browser.close()

    return m3u8_map


def _select_resolution(urls: list[str], target: str) -> str | None:
    """Select best m3u8 URL matching target resolution.

    Fallback logic:
    1. Exact match (e.g. "720p")
    2. 720p fallback
    3. Highest available
    """
    if not urls:
        return None

    # Try exact match
    for url in urls:
        if target in url:
            return url

    # Fallback to 720p
    for url in urls:
        if "720p" in url:
            return url

    # Use first available (highest quality usually listed first)
    return urls[0] if urls else None
