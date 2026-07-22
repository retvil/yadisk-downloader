#!/usr/bin/env python3
"""
Build script for yadisk-downloader.
Creates distributable packages for Windows, macOS, and Linux.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Paths
ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
RELEASES = ROOT / "releases"
VERSION = "1.0.0"


def clean():
    """Clean build directories."""
    print("Cleaning build directories...")
    for d in [DIST, BUILD, RELEASES]:
        if d.exists():
            shutil.rmtree(d)
    print("Done.")


def install_build_deps():
    """Install build dependencies."""
    print("Installing build dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "imageio-ffmpeg"], check=True)
    print("Done.")


def build_windows():
    """Build Windows executable."""
    print("\n" + "=" * 60)
    print("Building for Windows...")
    print("=" * 60)

    # Create release directory
    release_dir = RELEASES / "windows"
    release_dir.mkdir(parents=True, exist_ok=True)

    # Build with PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=yadisk-downloader",
        "--windowed",  # No console window
        "--onedir",  # Create a folder
        "--icon=NONE",  # Add icon later
        f"--distpath={DIST / 'windows'}",
        f"--workpath={BUILD / 'windows'}",
        f"--specpath={ROOT}",
        "--hidden-import=customtkinter",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--hidden-import=yadisk_downloader",
        "--collect-all=customtkinter",
        "--collect-all=imageio_ffmpeg",
        str(ROOT / "yadisk_downloader" / "__main__.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    # Copy to releases
    exe_dir = DIST / "windows" / "yadisk-downloader"
    if exe_dir.exists():
        shutil.copytree(exe_dir, release_dir / "yadisk-downloader-portable")

    print(f"Windows build complete: {release_dir}")


def build_macos():
    """Build macOS application."""
    print("\n" + "=" * 60)
    print("Building for macOS...")
    print("=" * 60)

    release_dir = RELEASES / "macos"
    release_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=yadisk-downloader",
        "--windowed",
        "--onedir",
        f"--distpath={DIST / 'macos'}",
        f"--workpath={BUILD / 'macos'}",
        f"--specpath={ROOT}",
        "--hidden-import=customtkinter",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--collect-all=customtkinter",
        "--collect-all=imageio_ffmpeg",
        str(ROOT / "yadisk_downloader" / "__main__.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    # Copy to releases
    app_dir = DIST / "macos" / "yadisk-downloader.app"
    if app_dir.exists():
        shutil.copytree(app_dir, release_dir / "yadisk-downloader.app")

    print(f"macOS build complete: {release_dir}")


def build_linux():
    """Build Linux binary."""
    print("\n" + "=" * 60)
    print("Building for Linux...")
    print("=" * 60)

    release_dir = RELEASES / "linux"
    release_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=yadisk-downloader",
        "--onedir",
        f"--distpath={DIST / 'linux'}",
        f"--workpath={BUILD / 'linux'}",
        f"--specpath={ROOT}",
        "--hidden-import=customtkinter",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--collect-all=customtkinter",
        "--collect-all=imageio_ffmpeg",
        str(ROOT / "yadisk_downloader" / "__main__.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    # Copy to releases
    bin_dir = DIST / "linux" / "yadisk-downloader"
    if bin_dir.exists():
        shutil.copytree(bin_dir, release_dir / "yadisk-downloader-portable")

    print(f"Linux build complete: {release_dir}")


def create_zip(platform_name):
    """Create zip archive of the build."""
    release_dir = RELEASES / platform_name
    if not release_dir.exists():
        return

    zip_name = f"yadisk-downloader-{VERSION}-{platform_name}"
    print(f"\nCreating zip: {zip_name}.zip")
    shutil.make_archive(
        RELEASES / zip_name,
        "zip",
        release_dir,
    )


def main():
    """Main build function."""
    import argparse

    parser = argparse.ArgumentParser(description="Build yadisk-downloader")
    parser.add_argument("--platform", choices=["windows", "macos", "linux", "all"], default="all")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--skip-deps", action="store_true")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    if not args.skip_deps:
        install_build_deps()

    system = args.platform
    if system == "all":
        current = platform.system().lower()
        if current == "windows":
            system = "windows"
        elif current == "darwin":
            system = "macos"
        else:
            system = "linux"

    if system == "windows":
        build_windows()
        create_zip("windows")
    elif system == "macos":
        build_macos()
        create_zip("macos")
    elif system == "linux":
        build_linux()
        create_zip("linux")

    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"Release files: {RELEASES}")
    print("=" * 60)


if __name__ == "__main__":
    main()
