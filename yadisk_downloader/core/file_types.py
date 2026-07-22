"""File type definitions and filtering for yadisk-downloader."""

import os


FILE_TYPES: dict[str, list[str]] = {
    "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".tif"],
    "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".rtf", ".odt"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"],
    "executable": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".apk"],
}

# Reverse lookup: extension -> type
_EXT_TO_TYPE: dict[str, str] = {}
for _type, _exts in FILE_TYPES.items():
    for _ext in _exts:
        _EXT_TO_TYPE[_ext] = _type


def get_file_type(filename: str) -> str:
    """Return file type category for a filename.

    Returns: "video", "audio", "image", "document", "archive", "executable", or "other"
    """
    ext = os.path.splitext(filename)[1].lower()
    return _EXT_TO_TYPE.get(ext, "other")


def matches_filter(
    filename: str,
    include_types: list[str] | None = None,
    exclude_types: list[str] | None = None,
) -> bool:
    """Check if a filename matches the type filter.

    Args:
        filename: The file name to check.
        include_types: If provided, only these types are included.
        exclude_types: If provided, these types are excluded.

    Returns:
        True if the file should be downloaded.
    """
    file_type = get_file_type(filename)

    if exclude_types and file_type in exclude_types:
        return False

    if include_types and file_type not in include_types:
        return False

    return True


def list_types() -> str:
    """Return formatted string of all available file types."""
    lines = ["Available file types:\n"]
    for type_name, extensions in FILE_TYPES.items():
        exts = ", ".join(extensions[:5])
        if len(extensions) > 5:
            exts += ", ..."
        lines.append(f"  {type_name:12s} — {exts}")
    lines.append(f"  {'other':12s} — any other extension")
    return "\n".join(lines)
