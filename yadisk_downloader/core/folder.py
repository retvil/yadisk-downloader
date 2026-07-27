"""Parallel folder download with asyncio semaphore."""

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from yadisk_downloader.core.downloader import download_file
from yadisk_downloader.plugins.base import FileInfo, get_registry
from yadisk_downloader.config.schema import get_settings
from yadisk_downloader.events import get_event_bus, DownloadStarted, DownloadProgress, DownloadCompleted, DownloadFailed


@dataclass
class FolderDownloadResult:
    """Result of a folder download operation."""
    folder: str
    total_files: int
    success: int
    failed: int
    total_size: int


class FolderDownloader:
    """Download multiple folders in parallel with concurrency control."""

    def __init__(
        self,
        max_concurrent_folders: int = 4,
        max_concurrent_files: int = 4,
    ):
        """
        Args:
            max_concurrent_folders: Max folders to download simultaneously.
            max_concurrent_files: Max files per folder (passed to strategies).
        """
        self.max_concurrent_folders = max_concurrent_folders
        self.max_concurrent_files = max_concurrent_files
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def download_folders(
        self,
        folders: list[str],
        files_by_folder: dict[str, list[dict]],
        base_url: str,
        output_dir: Path,
        resolution: str = "720p",
        progress_callback: Optional[callable] = None,
    ) -> list[FolderDownloadResult]:
        """
        Download multiple folders in parallel.

        Args:
            folders: List of folder names to download.
            files_by_folder: Dict mapping folder name -> list of file dicts.
            base_url: Yandex Disk public URL.
            output_dir: Base output directory.
            resolution: Video resolution for HLS.
            progress_callback: Optional callback(total_folders, completed_folders, current_folder).

        Returns:
            List of FolderDownloadResult for each folder.
        """
        self._semaphore = asyncio.Semaphore(self.max_concurrent_folders)

        async def download_one_folder(folder: str) -> FolderDownloadResult:
            async with self._semaphore:
                return await self._download_folder(
                    folder=folder,
                    files=files_by_folder.get(folder, []),
                    base_url=base_url,
                    output_dir=output_dir,
                    resolution=resolution,
                    progress_callback=progress_callback,
                )

        tasks = [download_one_folder(f) for f in folders]
        return await asyncio.gather(*tasks)

    async def _download_folder(
        self,
        folder: str,
        files: list[dict],
        base_url: str,
        output_dir: Path,
        resolution: str,
        progress_callback: Optional[callable] = None,
    ) -> FolderDownloadResult:
        """Download all files in a single folder."""
        from yadisk_downloader.core.browser import collect_m3u8_urls
        from yadisk_downloader.core.api import get_download_url

        if not files:
            return FolderDownloadResult(folder, 0, 0, 0, 0)

        # Collect m3u8 URLs for videos
        m3u8_map = collect_m3u8_urls(base_url, files, resolution)

        settings = get_settings()
        registry = get_registry()
        event_bus = get_event_bus()

        folder_output = output_dir / folder
        folder_output.mkdir(parents=True, exist_ok=True)

        total_files = len(files)
        success = 0
        failed = 0
        total_size = 0

        for i, f in enumerate(files):
            ft = f.get("file_type", "other")
            dest = folder_output / f["name"]

            # Build FileInfo
            file_info = FileInfo(
                name=f["name"],
                path=f["path"],
                size=f["size"],
                file_type=ft,
                download_url=get_download_url(base_url, f["path"]),
                m3u8_url=m3u8_map.get(f["path"]) if ft == "video" else None,
            )

            # Progress callback for this file
            def make_progress_cb(file_idx: int, file_total: int):
                def progress_cb(downloaded: int, total: int):
                    if progress_callback:
                        progress_callback(
                            folder,
                            file_idx,
                            file_total,
                            f["name"],
                            downloaded,
                            total,
                        )
                return progress_cb

            try:
                ok, size = download_file(
                    file_info=file_info,
                    dest=dest,
                    progress_callback=make_progress_cb(i + 1, total_files),
                    resume=True,
                    workers=settings.download.workers,
                )
                if ok:
                    success += 1
                    total_size += size
                else:
                    failed += 1
            except Exception:
                failed += 1

            # Per-folder progress
            if progress_callback:
                progress_callback(folder, i + 1, total_files, f["name"], 0, 0)

        return FolderDownloadResult(
            folder=folder,
            total_files=total_files,
            success=success,
            failed=failed,
            total_size=total_size,
        )


async def download_folders_parallel(
    folders: list[str],
    files_by_folder: dict[str, list[dict]],
    base_url: str,
    output_dir: Path,
    resolution: str = "720p",
    max_concurrent_folders: int = 4,
    max_concurrent_files: int = 4,
    progress_callback: Optional[callable] = None,
) -> list[FolderDownloadResult]:
    """
    High-level function to download multiple folders in parallel.

    Args:
        folders: List of folder names.
        files_by_folder: Dict folder -> list of file dicts.
        base_url: Yandex Disk public URL.
        output_dir: Output directory.
        resolution: Video resolution.
        max_concurrent_folders: Max parallel folders.
        max_concurrent_files: Max parallel files per folder (via plugin workers).
        progress_callback: Optional callback(folder, file_idx, total_files, filename, downloaded, total).

    Returns:
        List of FolderDownloadResult.
    """
    downloader = FolderDownloader(
        max_concurrent_folders=max_concurrent_folders,
        max_concurrent_files=max_concurrent_files,
    )
    return await downloader.download_folders(
        folders=folders,
        files_by_folder=files_by_folder,
        base_url=base_url,
        output_dir=output_dir,
        resolution=resolution,
        progress_callback=progress_callback,
    )


# Synchronous wrapper for CLI/GUI
def download_folders_sync(
    folders: list[str],
    files_by_folder: dict[str, list[dict]],
    base_url: str,
    output_dir: Path,
    resolution: str = "720p",
    max_concurrent_folders: int = 4,
    max_concurrent_files: int = 4,
    progress_callback: Optional[callable] = None,
) -> list[FolderDownloadResult]:
    """Synchronous wrapper for download_folders_parallel."""
    return asyncio.run(download_folders_parallel(
        folders=folders,
        files_by_folder=files_by_folder,
        base_url=base_url,
        output_dir=output_dir,
        resolution=resolution,
        max_concurrent_folders=max_concurrent_folders,
        max_concurrent_files=max_concurrent_files,
        progress_callback=progress_callback,
    ))