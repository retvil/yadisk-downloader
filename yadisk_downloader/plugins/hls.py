"""HLS Video download strategy with ffmpeg + parallel fallback."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from yadisk_downloader.plugins.base import (
    DownloadStrategy,
    FileInfo,
    DownloadContext,
    DownloadResult,
)
from yadisk_downloader.core.parallel_hls import download_hls_parallel
from yadisk_downloader.core.safety import sanitize_url_for_log, build_proxy_dict
from yadisk_downloader.events import get_event_bus, DownloadProgress, DownloadCompleted, DownloadFailed


class HLSVideoStrategy:
    """Download video via HLS (m3u8) with ffmpeg + parallel fallback."""

    name = "hls_video"
    priority = 100  # Highest - best quality for video

    def can_handle(self, file_info: FileInfo) -> bool:
        return file_info.file_type == "video" and file_info.m3u8_url is not None

    def download(
        self,
        file_info: FileInfo,
        dest: Path,
        context: DownloadContext,
    ) -> DownloadResult:
        event_bus = get_event_bus()
        m3u8_url = file_info.m3u8_url
        # Get ffmpeg path from settings
        ffmpeg_path = getattr(context.settings, 'ffmpeg_path', None)

        def progress_cb(downloaded: int, total: int):
            speed = downloaded / (total / 1024 / 1024) if total > 0 else 0
            event_bus.emit(DownloadProgress(
                url=m3u8_url,
                file_path=str(dest),
                downloaded=downloaded,
                total=total,
                speed=speed,
            ))

        # Try ffmpeg first (best quality, handles encryption)
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            ok, size = self._download_hls_ffmpeg(ffmpeg_path, m3u8_url, str(dest), context.proxy_dict)
            if ok:
                return DownloadResult(
                    success=True,
                    path=dest,
                    size=size,
                    strategy_used=self.name,
                )

        # Fallback: pure Python parallel M3U8 downloader
        try:
            download_hls_parallel(
                m3u8_url=m3u8_url,
                output_path=dest,
                workers=min(max(context.settings.download.workers, 1), 16),
                headers=context.oauth_headers or {},
                progress_callback=progress_cb,
            )

            if dest.exists():
                size = dest.stat().st_size
                event_bus.emit(DownloadCompleted(
                    url=sanitize_url_for_log(m3u8_url),
                    file_path=str(dest),
                    size=size,
                ))
                return DownloadResult(
                    success=True,
                    path=dest,
                    size=size,
                    strategy_used=self.name,
                )

            return DownloadResult(
                success=False,
                error="HLS download completed but file not found",
                strategy_used=self.name,
            )

        except Exception as e:
            event_bus.emit(DownloadFailed(
                url=sanitize_url_for_log(m3u8_url),
                file_path=str(dest),
                error=str(e),
            ))
            return DownloadResult(
                success=False,
                error=str(e),
                strategy_used=self.name,
            )

    def _download_hls_ffmpeg(
        self,
        ffmpeg_path: str,
        m3u8_url: str,
        output_path: str,
        proxy_dict: Optional[dict] = None,
    ) -> tuple[bool, int]:
        """Download HLS stream using ffmpeg."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        cmd = [ffmpeg_path, "-i", m3u8_url, "-c", "copy", "-y", output_path]

        if proxy_dict and "http" in proxy_dict:
            cmd.extend(["-http_proxy", proxy_dict["http"]])

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=3600)
            if result.returncode == 0 and os.path.exists(output_path):
                return True, os.path.getsize(output_path)
            return False, 0
        except Exception:
            return False, 0

    def get_default_options(self) -> dict:
        return {"workers": 4, "max_workers": 16}