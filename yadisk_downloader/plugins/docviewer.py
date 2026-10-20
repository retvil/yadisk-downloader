"""Docviewer fallback strategy for blocked files with OAuth support."""

from pathlib import Path

from yadisk_downloader.core.auth import enhance_api_url
from yadisk_downloader.events import DownloadFailed, DownloadStarted, get_event_bus
from yadisk_downloader.plugins.base import (
    DownloadContext,
    DownloadResult,
    FileInfo,
)


class DocviewerStrategy:
    """Download via Yandex Docviewer (fallback for blocked files) with OAuth support."""

    name = "docviewer"
    priority = 10  # Lowest - fallback only

    def can_handle(self, file_info: FileInfo) -> bool:
        # Can handle any file type as last resort
        return True

    def download(
        self,
        file_info: FileInfo,
        dest: Path,
        context: DownloadContext,
    ) -> DownloadResult:
        """Docviewer requires Playwright page - this is a placeholder.

        Actual implementation should be called from GUI/CLI with browser context.
        This strategy just provides the enhanced URL with OAuth token.
        """
        event_bus = get_event_bus()

        # Enhance URL with OAuth token if available
        enhanced_url = file_info.path
        if file_info.download_url:
            enhanced_url = enhance_api_url(file_info.download_url)
        elif file_info.path:
            enhanced_url = enhance_api_url(file_info.path)

        # Emit started event with enhanced URL
        event_bus.emit(DownloadStarted(
            url=enhanced_url,
            file_path=str(dest),
            file_size=file_info.size,
        ))

        event_bus.emit(DownloadFailed(
            url=enhanced_url,
            file_path=str(dest),
            error="Docviewer strategy requires browser context (Playwright page). Use download_via_docviewer() directly with a Playwright page.",
        ))
        return DownloadResult(
            success=False,
            error="Docviewer requires browser context (Playwright). Use CLI/GUI which provides browser context.",
            strategy_used=self.name,
        )

    def get_enhanced_url(self, file_info: FileInfo) -> str:
        """Get URL with OAuth token appended for browser context."""
        if file_info.download_url:
            return enhance_api_url(file_info.download_url)
        return enhance_api_url(file_info.path)

    def get_default_options(self) -> dict:
        return {}
