"""Yandex Disk API — file discovery and download for public links."""

import json
import os
import ssl
import time
import urllib.parse
import urllib.request

from .file_types import get_file_type, matches_filter


def list_files(
    public_key: str,
    include_types: list[str] | None = None,
    exclude_types: list[str] | None = None,
) -> list[dict]:
    """List all files in a public Yandex Disk folder.

    Args:
        public_key: Yandex Disk public link.
        include_types: If provided, only include these file types.
        exclude_types: If provided, exclude these file types.

    Returns list of dicts: {name, path, size, folder, file_type}
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    def _list_dir(path: str = "/") -> list[dict]:
        for attempt in range(3):
            try:
                params = urllib.parse.urlencode({
                    "public_key": public_key,
                    "path": path,
                    "limit": 1000,
                })
                url = f"https://cloud-api.yandex.net/v1/disk/public/resources?{params}"
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    return data.get("_embedded", {}).get("items", [])
            except Exception:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                else:
                    raise

    folders = []
    files = []

    for item in _list_dir("/"):
        if item["type"] == "dir":
            folders.append(item["name"])
        elif item["type"] == "file":
            name = item["name"]
            if matches_filter(name, include_types, exclude_types):
                files.append({
                    "name": name,
                    "path": item["path"],
                    "size": item.get("size", 0),
                    "folder": "",
                    "file_type": get_file_type(name),
                })

    for folder in folders:
        for item in _list_dir(f"/{folder}"):
            if item["type"] == "file":
                name = item["name"]
                if matches_filter(name, include_types, exclude_types):
                    files.append({
                        "name": name,
                        "path": item["path"],
                        "size": item.get("size", 0),
                        "folder": folder,
                        "file_type": get_file_type(name),
                    })

    return files


def get_download_url(public_key: str, file_path: str) -> str | None:
    """Get direct download URL for a file via Yandex Disk API.

    Args:
        public_key: Yandex Disk public link.
        file_path: Path to the file on Yandex Disk.

    Returns:
        Download URL string, or None if failed.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    params = urllib.parse.urlencode({
        "public_key": public_key,
        "path": file_path,
    })
    url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?{params}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data.get("href")
        except Exception:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None


def list_folders(public_key: str) -> list[str]:
    """List all subfolder names in a public Yandex Disk folder."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    params = urllib.parse.urlencode({"public_key": public_key, "path": "/", "limit": 1000})
    url = f"https://cloud-api.yandex.net/v1/disk/public/resources?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    return [
        item["name"]
        for item in data.get("_embedded", {}).get("items", [])
        if item["type"] == "dir"
    ]
