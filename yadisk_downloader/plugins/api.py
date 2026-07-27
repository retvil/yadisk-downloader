"""Direct API download strategy with connection pooling, retry, and resume."""

import os
import time
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from yadisk_downloader.plugins.base import (
    DownloadStrategy,
    FileInfo,
    DownloadContext,
    DownloadResult,
)
from yadisk_downloader.core.safety import sanitize_url_for_log, build_proxy_dict
from yadisk_downloader.events import get_event_bus, DownloadProgress, DownloadCompleted, DownloadFailed


class APIFileStrategy:
    """Download via direct API URL with resume support and connection pooling."""

    name = "api_file"
    priority = 50  # Medium - good for most files

    def can_handle(self, file_info: FileInfo) -> bool:
        return file_info.download_url is not None

    def download(
        self,
        file_info: FileInfo,
        dest: Path,
        context: DownloadContext,
    ) -> DownloadResult:
        event_bus = get_event_bus()
        url = file_info.download_url or ""
        proxy_dict = context.proxy_dict

        def progress_cb(downloaded: int, total: int):
            speed = downloaded / (total / 1024 / 1024) if total > 0 else 0
            event_bus.emit(DownloadProgress(
                url=url,
                file_path=str(dest),
                downloaded=downloaded,
                total=total,
                speed=speed,
            ))

        dest.parent.mkdir(parents=True, exist_ok=True)

        # Use requests for connection pooling
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=context.settings.download.max_retries,
            backoff_factor=context.settings.download.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(
            pool_connections=context.settings.download.pool_size,
            pool_maxsize=context.settings.download.pool_size,
            max_retries=retry_strategy,
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Configure proxy
        if proxy_dict:
            session.proxies = proxy_dict

        # SSL verification disabled for Yandex
        session.verify = False

        # Check for partial download
        downloaded = 0
        if context.settings.download.resume and dest.exists():
            downloaded = dest.stat().st_size

        for attempt in range(3):
            try:
                headers = {}
                if downloaded > 0:
                    headers["Range"] = f"bytes={downloaded}-"

                resp = session.get(url, headers=headers, stream=True, timeout=600)

                # Check if server supports range requests
                status_code = resp.status_code
                if status_code == 206:
                    # Partial content - resume
                    pass
                elif status_code == 200:
                    # Full content - start from beginning
                    downloaded = 0
                elif status_code == 416:
                    # Range not satisfiable - file already complete
                    return DownloadResult(
                        success=True,
                        path=dest,
                        size=dest.stat().st_size,
                        strategy_used=self.name,
                    )
                else:
                    resp.raise_for_status()

                total_size = int(resp.headers.get("Content-Length", 0))
                if status_code == 200:
                    total_size = total_size  # Full size
                elif status_code == 206:
                    total_size = downloaded + total_size  # Remaining + already downloaded

                mode = "ab" if downloaded > 0 and status_code == 206 else "wb"
                with dest.open(mode) as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if context.progress_callback:
                            progress_cb(downloaded, total_size)

                if dest.exists():
                    return DownloadResult(
                        success=True,
                        path=dest,
                        size=dest.stat().st_size,
                        strategy_used=self.name,
                    )
                return DownloadResult(
                    success=False,
                    error="API download failed",
                    strategy_used=self.name,
                )

            except requests.exceptions.RequestException:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                else:
                    return DownloadResult(
                        success=False,
                        error="API download failed after retries",
                        strategy_used=self.name,
                    )

        return DownloadResult(
            success=False,
            error="Max retries exceeded",
            strategy_used=self.name,
        )

    def get_default_options(self) -> dict:
        return {"pool_size": 10, "max_retries": 3, "retry_backoff": 1.0}