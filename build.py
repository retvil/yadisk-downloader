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
VERSION = "1.3.0"
ICON = ROOT / "yadisk_downloader" / "assets" / "icon.ico"

# Modules excluded from the bundle: not imported by yadisk_downloader, but
# present in the build environment (transitive deps of other packages).
# PyInstaller excludes are authoritative — nothing listed here gets collected.
# NOTE: PIL/pillow must NOT be excluded (ttkbootstrap depends on it).
EXCLUDED_MODULES = [
    # ML / DL frameworks
    "torch", "torchvision", "torchaudio", "tensorflow", "keras",
    "paddle", "paddleocr", "catboost", "xgboost", "lightgbm",
    "onnx", "onnxruntime", "bitsandbytes", "transformers", "diffusers",
    "safetensors", "huggingface_hub", "triton", "sympy", "networkx",
    # GPU / numeric
    "cupy", "cupyx", "fastrlock", "llvmlite", "numba",
    "numpy", "scipy", "sklearn", "pandas", "polars", "pyarrow",
    "matplotlib", "cv2", "opencv", "openvino",
    # unrelated heavy deps found in the environment
    "yt_dlp", "curl_cffi", "websockets", "mutagen", "brotli",
    "secretstorage", "patchright", "Cryptodome", "pycryptodome",
    "IPython", "jupyter",
    # NLP (spacy hook crashes PyInstaller child process with 0xC0000005)
    "spacy", "thinc", "srsly", "catalogue", "weasel",
    "en_core_web_sm", "en_core_web_md", "en_core_web_lg", "en_core_web_trf",
    # geo / vector / misc heavy packages present in the environment
    "psycopg2", "faiss", "faiss_cpu", "shapely", "pyproj", "pyogrio",
    "geopandas", "fiona", "ctranslate2", "llama_cpp", "decord", "av",
]


# Packages removed from the bundle after PyInstaller finishes. None of them is
# imported by yadisk_downloader (verified by grep); they get collected anyway
# because third-party PyInstaller hooks (e.g. patchright masquerading as
# playwright hooks) and binary dependency analysis pull them in.
PRUNED_PACKAGES = [
    "patchright", "bokeh", "litellm", "botocore", "selenium",
    "plotly", "pymupdf", "granian", "grpc",
]


def prune_bundle(bundle_dir: Path):
    """Remove known-unused packages from a PyInstaller onedir bundle."""
    internal = bundle_dir / "_internal"
    if not internal.exists():
        return
    for name in PRUNED_PACKAGES:
        target = internal / name
        if target.exists():
            shutil.rmtree(target)
            print(f"Pruned {name} from bundle")


ISCC_CANDIDATES = [
    Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Inno Setup 6" / "ISCC.exe",
    Path(os.environ.get("PROGRAMFILES", "")) / "Inno Setup 6" / "ISCC.exe",
    Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe",
]


def find_iscc() -> Path:
    """Locate the Inno Setup command-line compiler."""
    for candidate in ISCC_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "ISCC.exe not found. Install Inno Setup 6: https://jrsoftware.org/isdl.php"
    )


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
        f"--icon={ICON}",
        f"--distpath={DIST / 'windows'}",
        f"--workpath={BUILD / 'windows'}",
        f"--specpath={ROOT}",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--hidden-import=yadisk_downloader",
        "--collect-all=ttkbootstrap",
        "--collect-all=imageio_ffmpeg",
        "--exclude-module=PyQt6",
        "--exclude-module=PySide6",
        *[f"--exclude-module={m}" for m in EXCLUDED_MODULES],
        "--noconfirm",
        str(ROOT / "run.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    # Remove packages that hooks/binary analysis pulled in but the app never imports
    prune_bundle(DIST / "windows" / "yadisk-downloader")

    # Copy to releases
    exe_dir = DIST / "windows" / "yadisk-downloader"
    if exe_dir.exists():
        shutil.copytree(exe_dir, release_dir / "yadisk-downloader-portable", dirs_exist_ok=True)

    print(f"Windows build complete: {release_dir}")


def build_windows_onefile():
    """Build a single-file Windows executable (self-extracting, no _internal)."""
    print("\n" + "=" * 60)
    print("Building Windows onefile...")
    print("=" * 60)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=yadisk-downloader",
        "--windowed",  # No console window
        "--onefile",  # Single self-extracting exe
        f"--icon={ICON}",
        f"--distpath={DIST / 'windows-onefile'}",
        f"--workpath={BUILD / 'windows-onefile'}",
        f"--specpath={ROOT}",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--hidden-import=yadisk_downloader",
        "--collect-all=ttkbootstrap",
        "--collect-all=imageio_ffmpeg",
        "--exclude-module=PyQt6",
        "--exclude-module=PySide6",
        # onefile has no _internal dir, so prune_bundle() cannot run — the
        # hook/binary-analysis junk must be excluded at collection time instead.
        *[f"--exclude-module={m}" for m in EXCLUDED_MODULES + PRUNED_PACKAGES],
        "--noconfirm",
        str(ROOT / "run.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    exe = DIST / "windows-onefile" / "yadisk-downloader.exe"
    if exe.exists():
        target = RELEASES / f"yadisk-downloader-{VERSION}-windows-onefile.exe"
        shutil.copy2(exe, target)
        print(f"Onefile build complete: {target}")


def build_installer():
    """Compile the Windows installer with Inno Setup (requires onedir build)."""
    bundle = DIST / "windows" / "yadisk-downloader"
    if not bundle.exists():
        raise FileNotFoundError(
            f"{bundle} not found — run the Windows onedir build first"
        )

    print("\n" + "=" * 60)
    print("Building Windows installer...")
    print("=" * 60)

    iscc = find_iscc()
    subprocess.run(
        [str(iscc), f"/DBundleDir={bundle}", f"/DMyAppVersion={VERSION}",
         str(ROOT / "installer.iss")],
        check=True,
    )
    print(f"Installer build complete: {RELEASES}")


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
        f"--icon={ICON.with_suffix('.icns')}",
        f"--distpath={DIST / 'macos'}",
        f"--workpath={BUILD / 'macos'}",
        f"--specpath={ROOT}",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--collect-all=ttkbootstrap",
        "--collect-all=imageio_ffmpeg",
        "--exclude-module=PyQt6",
        "--exclude-module=PySide6",
        *[f"--exclude-module={m}" for m in EXCLUDED_MODULES],
        "--noconfirm",
        str(ROOT / "run.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    # Copy to releases
    app_dir = DIST / "macos" / "yadisk-downloader.app"
    if app_dir.exists():
        shutil.copytree(app_dir, release_dir / "yadisk-downloader.app", dirs_exist_ok=True)

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
        "--hidden-import=ttkbootstrap",
        "--hidden-import=requests",
        "--hidden-import=playwright",
        "--collect-all=ttkbootstrap",
        "--collect-all=imageio_ffmpeg",
        "--exclude-module=PyQt6",
        "--exclude-module=PySide6",
        *[f"--exclude-module={m}" for m in EXCLUDED_MODULES],
        "--noconfirm",
        str(ROOT / "run.py"),
    ]

    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)

    # Remove packages that hooks/binary analysis pulled in but the app never imports
    prune_bundle(DIST / "linux" / "yadisk-downloader")

    # Copy to releases
    bin_dir = DIST / "linux" / "yadisk-downloader"
    if bin_dir.exists():
        shutil.copytree(bin_dir, release_dir / "yadisk-downloader-portable", dirs_exist_ok=True)

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
    parser.add_argument("--onefile", action="store_true",
                        help="Also build a single-file Windows exe")
    parser.add_argument("--installer", action="store_true",
                        help="Also build the Windows installer (Inno Setup)")
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
        if args.onefile:
            build_windows_onefile()
        if args.installer:
            build_installer()
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
