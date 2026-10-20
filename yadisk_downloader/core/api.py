"""Yandex Disk API — file discovery and download for public links."""

import json
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

    Recursively walks all subfolders and handles pagination (>1000 items).

    Args:
        public_key: Yandex Disk public link.
        include_types: If provided, only include these file types.
        exclude_types: If provided, exclude these file types.

    Returns list of dicts: {name, path, size, folder, file_type}
    where ``folder`` is the relative path inside the public folder
    ("" for root files, "Sub" or "Sub/Nested" otherwise).
    """
    def _fetch_page(path: str, offset: int) -> dict:
        for attempt in range(3):
            try:
                params = urllib.parse.urlencode({
                    "public_key": public_key,
                    "path": path,
                    "limit": 1000,
                    "offset": offset,
                })
                url = f"https://cloud-api.yandex.net/v1/disk/public/resources?{params}"
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            except Exception:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                else:
                    raise

    def _list_dir(path: str = "/") -> list[dict]:
        """List all items in a directory, following pagination."""
        items: list[dict] = []
        offset = 0
        while True:
            embedded = _fetch_page(path, offset).get("_embedded", {})
            batch = embedded.get("items", [])
            items.extend(batch)
            total = embedded.get("total")
            offset += len(batch)
            if not batch or (total is not None and offset >= total):
                break
        return items

    files: list[dict] = []

    def _walk(dir_path: str, folder_label: str) -> None:
        for item in _list_dir(dir_path):
            if item["type"] == "dir":
                sub_label = f"{folder_label}/{item['name']}" if folder_label else item["name"]
                _walk(f"/{sub_label}", sub_label)
            elif item["type"] == "file":
                name = item["name"]
                if matches_filter(name, include_types, exclude_types):
                    files.append({
                        "name": name,
                        "path": item["path"],
                        "size": item.get("size", 0),
                        "folder": folder_label,
                        "file_type": get_file_type(name),
                    })

    _walk("/", "")
    return files


def get_download_url(public_key: str, file_path: str) -> str | None:
    """Get direct download URL for a file via Yandex Disk API.

    Args:
        public_key: Yandex Disk public link.
        file_path: Path to the file on Yandex Disk.

    Returns:
        Download URL string, or None if failed.
    """
    params = urllib.parse.urlencode({
        "public_key": public_key,
        "path": file_path,
    })
    url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?{params}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data.get("href")
        except Exception:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                return None


def list_folders(public_key: str) -> list[str]:
    """List all subfolder names in a public Yandex Disk folder."""
    params = urllib.parse.urlencode({"public_key": public_key, "path": "/", "limit": 1000})
    url = f"https://cloud-api.yandex.net/v1/disk/public/resources?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    return [
        item["name"]
        for item in data.get("_embedded", {}).get("items", [])
        if item["type"] == "dir"
    ]
