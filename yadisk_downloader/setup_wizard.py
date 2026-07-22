"""First-run setup wizard for downloading Chromium browser."""

import os
import subprocess
import sys
from pathlib import Path


def is_chromium_installed() -> bool:
    """Check if Playwright Chromium is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def download_chromium(progress_callback=None) -> bool:
    """Download Playwright Chromium browser.

    Args:
        progress_callback: Optional callable(message, progress_percent).

    Returns:
        True if successful.
    """
    try:
        if progress_callback:
            progress_callback("Downloading Chromium browser...", 0)

        process = subprocess.Popen(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            line = line.strip()
            if line and progress_callback:
                progress_callback(line, -1)  # Indeterminate progress

        process.wait()

        if process.returncode == 0:
            if progress_callback:
                progress_callback("Chromium installed successfully!", 100)
            return True
        else:
            if progress_callback:
                progress_callback(f"Failed to install Chromium (exit code: {process.returncode})", 0)
            return False

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error: {e}", 0)
        return False


def run_setup_if_needed(progress_callback=None) -> bool:
    """Run setup wizard if Chromium is not installed.

    Args:
        progress_callback: Optional callable(message, progress_percent).

    Returns:
        True if Chromium is ready (installed or already present).
    """
    if is_chromium_installed():
        return True

    print("Chromium browser is not installed.")
    print("It's required for downloading files from Yandex Disk.")
    print()

    response = input("Download Chromium now? (y/n): ").strip().lower()
    if response != "y":
        print("Setup cancelled. Some features may not work.")
        return False

    return download_chromium(progress_callback)
