"""CLI interface for yadisk-downloader."""

import argparse
import os
import sys
import time
from pathlib import Path

from .config import Config, get_config_path
from .core.api import get_download_url, list_files
from .core.browser import collect_m3u8_urls
from .core.converter import PRESETS, convert, get_output_path, list_presets
from .core.downloader import download_from_api, download_hls, compute_checksum, verify_checksum
from .core.file_types import list_types
from .notify import notify_download_complete
from .queue import DownloadQueue
from .scheduler import ScheduleConfig, is_running, save_pid, remove_pid
from .state import DownloadState, get_state_file
from .utils import find_ffmpeg, format_size


def _print_preset_list():
    print(list_presets())


def _print_type_list():
    print(list_types())


def _print_config():
    config = Config.load()
    print(f"Config file: {get_config_path()}")
    print(f"  Resolution:    {config.resolution}")
    print(f"  Output dir:    {config.output_dir}")
    print(f"  Proxy:         {config.proxy or '(none)'}")
    print(f"  Notify:        {config.notify}")
    print(f"  Workers:       {config.workers}")
    print(f"  Preset:        {config.preset or '(none)'}")
    print(f"  Delete original: {config.delete_original}")


def _queue_add(args):
    """Add URL to download queue."""
    queue = DownloadQueue.load()
    folder = args.folder
    preset = args.preset
    if queue.add(args.queue_url, folder, preset):
        queue.save()
        print(f"Added to queue: {args.queue_url[:60]}...")
    else:
        print(f"URL already in queue: {args.queue_url[:60]}...")


def _queue_remove(args):
    """Remove URL from download queue."""
    queue = DownloadQueue.load()
    queue.remove(args.queue_url)
    queue.save()
    print(f"Removed from queue: {args.queue_url[:60]}...")


def _queue_show():
    """Show download queue."""
    queue = DownloadQueue.load()
    queue.show()


def _queue_clear():
    """Clear download queue."""
    queue = DownloadQueue.load()
    queue.clear()
    print("Queue cleared")


def _queue_process(args, config: Config):
    """Process all items in the download queue."""
    queue = DownloadQueue.load()
    pending = queue.get_pending()

    if not pending:
        print("No pending items in queue")
        return

    print(f"Processing {len(pending)} items in queue...\n")

    for i, item in enumerate(pending, 1):
        print(f"\n{'='*60}")
        print(f"Queue item {i}/{len(pending)}: {item.url[:60]}...")
        print(f"{'='*60}")

        queue.update(item.url, "downloading")
        queue.save()

        # Create args-like object for _run_download
        class QueueArgs:
            url = item.url
            folder = item.folder
            preset = item.preset or args.preset
            resolution = args.resolution
            output = args.output
            type = args.type
            exclude = args.exclude
            proxy = args.proxy
            notify = args.notify
            no_resume = args.no_resume
            checksum = args.checksum
            delete_original = args.delete_original
            list = False
            workers = args.workers

        try:
            _run_download(QueueArgs(), config)
            queue.update(item.url, "done")
        except Exception as e:
            queue.update(item.url, "failed", str(e))
            print(f"Failed: {e}")

        queue.save()


def _schedule_add(args):
    """Add scheduled download."""
    schedule = ScheduleConfig.load()
    entry = schedule.add(
        url=args.schedule_url,
        cron=args.cron,
        folder=args.folder,
        preset=args.preset,
        resolution=args.resolution,
        output=args.output,
    )
    schedule.save()
    print(f"Scheduled: {args.schedule_url[:60]}...")
    print(f"  Cron: {args.cron}")


def _schedule_remove(args):
    """Remove scheduled download."""
    schedule = ScheduleConfig.load()
    schedule.remove(args.schedule_url)
    schedule.save()
    print(f"Removed schedule for: {args.schedule_url[:60]}...")


def _schedule_show():
    """Show scheduled downloads."""
    schedule = ScheduleConfig.load()
    schedule.show()


def _schedule_run(args, config: Config):
    """Run scheduler (processes due downloads)."""
    if is_running():
        print("Scheduler is already running")
        return

    save_pid()
    print("Scheduler started. Press Ctrl+C to stop.")

    try:
        while True:
            schedule = ScheduleConfig.load()
            due = schedule.get_due()

            for entry in due:
                print(f"\nRunning scheduled download: {entry.url[:60]}...")

                class ScheduleArgs:
                    url = entry.url
                    folder = entry.folder
                    preset = entry.preset
                    resolution = entry.resolution
                    output = entry.output
                    type = None
                    exclude = None
                    proxy = args.proxy
                    notify = True
                    no_resume = False
                    checksum = False
                    delete_original = False
                    list = False
                    workers = args.workers

                try:
                    _run_download(ScheduleArgs(), config)
                    entry.last_run = time.time()
                except Exception as e:
                    print(f"Failed: {e}")

            # Update next_run times
            for entry in schedule.entries:
                if entry.next_run <= time.time():
                    entry.next_run = schedule._parse_cron(entry.cron)
            schedule.save()

            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\nScheduler stopped")
    finally:
        remove_pid()


def _run_download(args, config: Config):
    # Parse type filters
    include_types = None
    exclude_types = None

    if args.type:
        include_types = [t.strip() for t in args.type.split(",")]
    elif config.preset:
        pass  # Config preset doesn't affect type filtering

    if args.exclude:
        exclude_types = [t.strip() for t in args.exclude.split(",")]

    # Resolve output directory
    output = args.output or config.output_dir

    # Resolve resolution
    resolution = args.resolution or config.resolution

    # Resolve proxy
    proxy = args.proxy or config.proxy

    # Resolve preset
    preset = args.preset or config.preset

    # Resolve notify
    notify = args.notify or config.notify

    # Resolve resume and checksum flags
    resume = not args.no_resume
    checksum = args.checksum

    # Load or create download state
    state_file = get_state_file(args.url)
    state = DownloadState.load(state_file) or DownloadState(url=args.url)

    # Scan files
    print(f"Scanning {args.url} ...")
    try:
        files = list_files(args.url, include_types, exclude_types)
    except Exception as e:
        print(f"ERROR: Failed to list files: {e}")
        sys.exit(1)

    # Filter by folder
    if args.folder:
        files = [f for f in files if f["folder"] == args.folder]
        if not files:
            print(f"No files found in folder '{args.folder}'")
            sys.exit(1)

    total_size = sum(f["size"] for f in files)
    print(f"Found {len(files)} files, {format_size(total_size)}")

    # Show file type breakdown
    type_counts: dict[str, int] = {}
    for f in files:
        ft = f.get("file_type", "other")
        type_counts[ft] = type_counts.get(ft, 0) + 1
    if type_counts:
        breakdown = ", ".join(f"{k}: {v}" for k, v in sorted(type_counts.items()))
        print(f"  Types: {breakdown}")

    if proxy:
        print(f"  Proxy: {proxy}")
    if resume:
        print(f"  Resume: enabled")
    if checksum:
        print(f"  Checksum: enabled")

    # List mode
    if args.list:
        for i, f in enumerate(files, 1):
            size = format_size(f["size"]) if f["size"] else "?"
            folder = f"[{f['folder']}] " if f["folder"] else ""
            ft = f.get("file_type", "other")
            print(f"  {i:3d}. {folder}{f['name']} ({size}) [{ft}]")
        return

    # Filter pending files (skip existing or completed)
    pending = []
    for f in files:
        dest = os.path.join(output, f["folder"], f["name"]) if f["folder"] else os.path.join(output, f["name"])

        # Check if already completed in state
        file_state = state.get_file(f["path"])
        if file_state and file_state.status == "done":
            # Verify checksum if enabled
            if checksum and file_state.checksum:
                if os.path.exists(dest) and verify_checksum(dest, file_state.checksum):
                    print(f"  SKIP (verified): {f['name']}")
                    continue
            elif os.path.exists(dest) and os.path.getsize(dest) > 100_000:
                print(f"  SKIP: {f['name']}")
                continue

        if os.path.exists(dest) and os.path.getsize(dest) > 100_000:
            print(f"  SKIP: {f['name']}")
        else:
            pending.append(f)

    if not pending:
        print("\nAll files already downloaded!")
        return

    print(f"\nDownloading {len(pending)} files...")
    success = 0
    failed = 0
    start_time = time.time()

    ffmpeg = find_ffmpeg()

    for i, f in enumerate(pending, 1):
        dest = os.path.join(output, f["folder"], f["name"]) if f["folder"] else os.path.join(output, f["name"])
        ft = f.get("file_type", "other")
        file_start = time.time()

        print(f"\n  [{i}/{len(pending)}] {f['name'][:60]} ({format_size(f['size'])}) [{ft}]")

        # Update state
        state.update_file(f["path"], name=f["name"], size=f["size"], status="downloading")
        state.save(state_file)

        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        ok_dl = False
        size = 0

        # Progress callback for API downloads
        def progress(downloaded, total):
            if total > 0:
                pct = downloaded / total * 100
                speed = downloaded / (time.time() - file_start + 0.001) / 1024 / 1024
                print(f"\r    {pct:5.1f}%  {format_size(downloaded)}/{format_size(total)}  {speed:.1f} MB/s", end="", flush=True)

        # Strategy: API first, then fallback
        if ft == "video" and ffmpeg:
            # For video: try HLS first (best quality)
            print(f"    Trying HLS stream...")
            try:
                m3u8_map = collect_m3u8_urls(args.url, [f], resolution)
                m3u8 = m3u8_map.get(f["path"])
                if m3u8:
                    ok_dl, size = download_hls(ffmpeg, m3u8, dest, proxy)
            except Exception:
                pass

            # Fallback to API
            if not ok_dl:
                print(f"    HLS failed, trying API...")
                download_url = get_download_url(args.url, f["path"])
                if download_url:
                    ok_dl, size = download_from_api(download_url, dest, proxy, progress, resume)
                    print()  # New line after progress

        else:
            # For non-video: API first
            print(f"    Downloading via API...")
            download_url = get_download_url(args.url, f["path"])
            if download_url:
                ok_dl, size = download_from_api(download_url, dest, proxy, progress, resume)
                print()  # New line after progress

        if ok_dl:
            elapsed = time.time() - file_start
            speed = size / elapsed / 1024 / 1024 if elapsed > 0 else 0
            print(f"    OK: {format_size(size)} in {elapsed:.1f}s ({speed:.1f} MB/s)")

            # Compute checksum
            file_checksum = None
            if checksum:
                print(f"    Computing checksum...")
                file_checksum = compute_checksum(dest)
                print(f"    MD5: {file_checksum}")

            # Update state
            state.update_file(f["path"], downloaded=size, status="done", checksum=file_checksum)
            state.save(state_file)

            success += 1

            # Convert if preset specified (video only)
            if preset and ft == "video" and ffmpeg:
                conv_out = get_output_path(dest, preset)
                print(f"    Converting ({preset})...")
                ok_conv, conv_size = convert(ffmpeg, dest, conv_out, preset)
                if ok_conv:
                    print(f"    Converted: {format_size(conv_size)}")
                    if args.delete_original or config.delete_original:
                        os.remove(dest)
                        print(f"    Deleted original")
                else:
                    print(f"    Conversion failed")
        else:
            # Update state
            state.update_file(f["path"], status="failed")
            state.save(state_file)
            print(f"    FAILED")
            failed += 1

    total_elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Done in {total_elapsed:.0f}s! Success: {success}, Failed: {failed}")
    print("=" * 60)

    # Send notification
    if notify:
        notify_download_complete(len(pending), success, failed)


def main():
    parser = argparse.ArgumentParser(
        prog="yadisk-downloader",
        description="Yandex Disk Downloader with CLI and GUI",
    )
    parser.add_argument("url", nargs="?", help="Yandex Disk public link")
    parser.add_argument("-r", "--resolution", default=None,
                        choices=["240p", "360p", "480p", "720p", "1080p"],
                        help="Video download resolution (default: 720p)")
    parser.add_argument("-f", "--folder", help="Download specific folder only")
    parser.add_argument("-o", "--output", default=None,
                        help="Output directory (default: ./downloads)")
    parser.add_argument("-w", "--workers", type=int, default=None,
                        help="Parallel download workers (default: 4)")
    parser.add_argument("-t", "--type",
                        help="File types to download (comma-separated): video,audio,image,document,archive,executable")
    parser.add_argument("--exclude",
                        help="File types to exclude (comma-separated)")
    parser.add_argument("--proxy",
                        help="Proxy URL (e.g. http://proxy:8080)")
    parser.add_argument("--notify", action="store_true",
                        help="Send system notification on completion")
    parser.add_argument("--config",
                        help="Path to config file (default: ~/.yadisk-downloader/config.json)")
    parser.add_argument("--list", action="store_true",
                        help="List files without downloading")
    parser.add_argument("--gui", action="store_true",
                        help="Launch GUI mode")
    parser.add_argument("--preset", choices=list(PRESETS.keys()),
                        help="Conversion preset for video (applied after download)")
    parser.add_argument("--preset-list", action="store_true",
                        help="Show available conversion presets")
    parser.add_argument("--type-list", action="store_true",
                        help="Show available file types")
    parser.add_argument("--show-config", action="store_true",
                        help="Show current configuration")
    parser.add_argument("--save-config", action="store_true",
                        help="Save current CLI arguments as default config")
    parser.add_argument("--delete-original", action="store_true",
                        help="Delete original video file after conversion")
    parser.add_argument("--no-resume", action="store_true",
                        help="Disable resume support (re-download from scratch)")
    parser.add_argument("--checksum", action="store_true",
                        help="Compute and verify MD5 checksum after download")
    parser.add_argument("--clear-state", action="store_true",
                        help="Clear download state and start fresh")

    # Queue arguments
    parser.add_argument("--queue-add", metavar="URL",
                        help="Add URL to download queue")
    parser.add_argument("--queue-remove", metavar="URL",
                        help="Remove URL from download queue")
    parser.add_argument("--queue-show", action="store_true",
                        help="Show download queue")
    parser.add_argument("--queue-clear", action="store_true",
                        help="Clear download queue")
    parser.add_argument("--queue-process", action="store_true",
                        help="Process all items in download queue")

    # Schedule arguments
    parser.add_argument("--schedule-add", metavar="URL",
                        help="Add scheduled download")
    parser.add_argument("--cron",
                        help="Cron expression for schedule (e.g. '0 9 * * *')")
    parser.add_argument("--schedule-remove", metavar="URL",
                        help="Remove scheduled download")
    parser.add_argument("--schedule-show", action="store_true",
                        help="Show scheduled downloads")
    parser.add_argument("--schedule-run", action="store_true",
                        help="Run scheduler (process due downloads)")

    args = parser.parse_args()

    # Load config
    config_path = Path(args.config) if args.config else None
    config = Config.load(config_path)

    if args.preset_list:
        _print_preset_list()
        return

    if args.type_list:
        _print_type_list()
        return

    if args.show_config:
        _print_config()
        return

    if args.save_config:
        # Save current settings to config
        if args.resolution:
            config.resolution = args.resolution
        if args.output:
            config.output_dir = args.output
        if args.proxy:
            config.proxy = args.proxy
        if args.workers:
            config.workers = args.workers
        if args.preset:
            config.preset = args.preset
        if args.notify:
            config.notify = True
        if args.delete_original:
            config.delete_original = True
        config.save(config_path)
        print(f"Config saved to {config_path or get_config_path()}")
        return

    if args.clear_state:
        if args.url:
            state_file = get_state_file(args.url)
            state = DownloadState.load(state_file)
            if state:
                state.clear(state_file)
                print(f"State cleared for {args.url}")
            else:
                print(f"No state found for {args.url}")
        else:
            # Clear all state files
            from .state import STATE_DIR
            if STATE_DIR.exists():
                for f in STATE_DIR.glob("state_*.json"):
                    f.unlink()
                print("All download states cleared")
        return

    # Queue commands
    if args.queue_add:
        args.queue_url = args.queue_add
        _queue_add(args)
        return

    if args.queue_remove:
        args.queue_url = args.queue_remove
        _queue_remove(args)
        return

    if args.queue_show:
        _queue_show()
        return

    if args.queue_clear:
        _queue_clear()
        return

    if args.queue_process:
        _queue_process(args, config)
        return

    # Schedule commands
    if args.schedule_add:
        if not args.cron:
            print("ERROR: --cron is required with --schedule-add")
            sys.exit(1)
        args.schedule_url = args.schedule_add
        _schedule_add(args)
        return

    if args.schedule_remove:
        args.schedule_url = args.schedule_remove
        _schedule_remove(args)
        return

    if args.schedule_show:
        _schedule_show()
        return

    if args.schedule_run:
        _schedule_run(args, config)
        return

    if args.gui:
        from .gui import run_gui
        run_gui()
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    _run_download(args, config)


if __name__ == "__main__":
    main()
