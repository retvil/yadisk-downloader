"""Browser download strategy using Playwright with OAuth support."""

from pathlib import Path
from typing import Optional

from yadisk_downloader.plugins.base import (
    DownloadStrategy,
    FileInfo,
    DownloadContext,
    DownloadResult,
)
from yadisk_downloader.core.auth import get_api_headers, enhance_api_url
from yadisk_downloader.events import get_event_bus, DownloadProgress, DownloadCompleted, DownloadFailed
from yadisk_downloader.core.safety import sanitize_url_for_log


class BrowserStrategy:
    """Download via Playwright browser automation with OAuth support."""

    name = "browser"
    priority = 5  # Low - fallback after API

    def can_handle(self, file_info: FileInfo) -> bool:
        # Can handle any file type as fallback
        return True

    def download(
        self,
        file_info: FileInfo,
        dest: Path,
        context: DownloadContext,
    ) -> DownloadResult:
        """Browser download requires Playwright page - placeholder for direct use."""
        event_bus = get_event_bus()
        
        # Enhance URL with OAuth token
        enhanced_url = file_info.path
        if file_info.download_url:
            enhanced_url = enhance_api_url(file_info.download_url)
        elif file_info.path:
            enhanced_url = enhance_api_url(file_info.path)
        
        event_bus.emit(DownloadStarted(
            url=sanitize_url_for_log(enhanced_url),
            file_path=str(dest),
            file_size=file_info.size,
        ))
        
        event_bus.emit(DownloadFailed(
            url=sanitize_url_for_log(enhanced_url),
            file_path=str(dest),
            error="Browser strategy requires Playwright page context. Use download_via_browser() directly with a Playwright page.",
        ))
        return DownloadResult(
            success=False,
            error="Browser download requires Playwright page context. Use download_via_browser() directly with a Playwright page.",
            strategy_used=self.name,
        )

    def get_enhanced_url(self, file_info: FileInfo) -> str:
        """Get URL with OAuth token appended for browser context."""
        if file_info.download_url:
            return enhance_api_url(file_info.download_url)
        return enhance_api_url(file_info.path)
    
    def get_default_options(self) -> dict:
        return {}


def download_via_browser_with_oauth(
    page,
    file_info: FileInfo,
    dest: Path,
    progress_callback=None,
) -> tuple[bool, int]:
    """Download file using Playwright page with OAuth token in URL.
    
    Args:
        page: Playwright page object
        file_info: FileInfo with download_url or path
        dest: Destination path
        progress_callback: Optional callback(downloaded, total)
        
    Returns:
        Tuple of (success, size_bytes)
    """
    import os
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # Get enhanced URL with OAuth token
    url = file_info.download_url or file_info.path
    enhanced_url = enhance_api_url(url)
    
    event_bus = get_event_bus()
    sanitized_url = sanitize_url_for_log(enhanced_url)
    
    event_bus.emit(DownloadStarted(
        url=sanitized_url,
        file_path=str(dest),
        file_size=file_info.size,
    ))
    
    try:
        with page.expect_download(timeout=300000) as download_info:
            page.goto(enhanced_url, wait_until="load", timeout=60000)
        
        download = download_info.value
        download.save_as(str(dest))
        
        if dest.exists():
            size = dest.stat().st_size
            event_bus.emit(DownloadCompleted(
                url=sanitized_url,
                file_path=str(dest),
                size=size,
            ))
            return True, size
        
        event_bus.emit(DownloadFailed(
            url=sanitized_url,
            file_path=str(dest),
            error="Download completed but file not found",
        ))
        return False, 0
        
    except Exception as e:
        event_bus.emit(DownloadFailed(
            url=sanitized_url,
            file_path=str(dest),
            error=str(e),
        ))
        return False, 0


def download_via_docviewer_with_oauth(
    page,
    public_key: str,
    file_path: str,
    dest: Path,
    file_type: str = "document",
    timeout: int = 60,
) -> tuple[bool, int]:
    """Download via Yandex Docviewer with OAuth token support.
    
    Args:
        page: Playwright page object
        public_key: Yandex Disk public folder URL
        file_path: Path to file on Yandex Disk
        dest: Destination path
        file_type: File type (document, image, etc.)
        timeout: Max seconds to wait for rendering
        
    Returns:
        Tuple of (success, size_bytes)
    """
    import time
    import os
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # Enhance public key with OAuth token
    enhanced_public_key = enhance_api_url(public_key)
    
    event_bus = get_event_bus()
    
    event_bus.emit(DownloadStarted(
        url=enhanced_public_key,
        file_path=str(dest),
        file_size=0,
    ))
    
    try:
        # Step 1: Load the folder page to get store-prefetch data
        page.goto(enhanced_public_key, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Step 2: Extract dvSearch URL
        dv_search = page.evaluate("""(filePath) => {
            const script = document.getElementById('store-prefetch');
            if (!script) return null;
            const data = JSON.parse(script.textContent);
            const resources = data.resources || {};
            for (const [id, res] of Object.entries(resources)) {
                if (res.path && res.path.includes(filePath) && res.dvSearch) {
                    return res.dvSearch;
                }
            }
            return null;
        }""", file_path)

        if not dv_search:
            event_bus.emit(DownloadFailed(
                url=sanitize_url_for_log(enhanced_public_key),
                file_path=str(dest),
                error="Could not find docviewer URL for file",
            ))
            return False, 0

        # Step 3: Navigate to docviewer
        dv_url = f"https://docviewer.yandex.ru{dv_search}"
        page.goto(dv_url, wait_until="domcontentloaded", timeout=30000)

        # Step 4: Wait for rendering
        deadline = time.time() + timeout
        while time.time() < deadline:
            has_content = page.evaluate("""() => {
                const imgs = document.querySelectorAll('img[src*="htmlimage"]');
                if (imgs.length > 0) return 'htmlimage';
                const directImgs = document.querySelectorAll('img[src*="downloader.disk"], img[src*="preview"]');
                if (directImgs.length > 0) return 'direct_image';
                return null;
            }""")
            if has_content:
                time.sleep(2)
                break
            time.sleep(1)

        # Step 5: Save content based on type
        if file_type == "image":
            img_url = page.evaluate("""() => {
                const img = document.querySelector('img[src*="htmlimage"]');
                return img ? img.src : null;
            }""")
            if img_url:
                import urllib.request
                urllib.request.urlretrieve(img_url, str(dest))
                if dest.exists() and dest.stat().st_size > 100:
                    size = dest.stat().st_size
                    event_bus.emit(DownloadCompleted(
                        url=sanitize_url_for_log(enhanced_public_key),
                        file_path=str(dest),
                        size=size,
                    ))
                    return True, size
            # Fallback: screenshot
            page.screenshot(path=str(dest), full_page=True)
        else:
            # Documents and other types: save as PDF
            page.pdf(path=str(dest), print_background=True)

        if dest.exists() and dest.stat().st_size > 100:
            size = dest.stat().st_size
            event_bus.emit(DownloadCompleted(
                url=sanitize_url_for_log(enhanced_public_key),
                file_path=str(dest),
                size=size,
            ))
            return True, size

        event_bus.emit(DownloadFailed(
            url=sanitize_url_for_log(enhanced_public_key),
            file_path=str(dest),
            error="Docviewer download produced empty file",
        ))
        return False, 0

    except Exception as e:
        event_bus.emit(DownloadFailed(
            url=sanitize_url_for_log(enhanced_public_key),
            file_path=str(dest),
            error=str(e),
        ))
        return False, 0