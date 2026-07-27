"""Core modules for yadisk-downloader."""

from .api import get_download_url, list_files, list_folders
from .browser import collect_m3u8_urls
from .cache import M3U8_CACHE, Cache
from .converter import PRESETS, convert, get_output_path, list_presets
from .downloader import (
    compute_checksum,
    download_from_api,
    download_hls,
    download_via_docviewer,
    verify_checksum,
)
from .file_types import list_types
from .m3u8_parser import parse_m3u8
from .parallel_hls import download_hls_parallel, download_hls_parallel_sync
from .safety import (
    build_proxy_dict,
    parse_proxy_url,
    sanitize_proxy_for_log,
    sanitize_url_for_log,
    validate_output_path,
)

__all__ = [
    # api
    "get_download_url",
    "list_files",
    "list_folders",
    # browser
    "collect_m3u8_urls",
    # converter
    "PRESETS",
    "convert",
    "get_output_path",
    "list_presets",
    # downloader
    "download_from_api",
    "download_hls",
    "download_via_docviewer",
    "compute_checksum",
    "verify_checksum",
    # file_types
    "list_types",
    # m3u8_parser
    "parse_m3u8",
    # parallel_hls
    "download_hls_parallel",
    "download_hls_parallel_sync",
    # cache
    "Cache",
    "M3U8_CACHE",
    # safety
    "sanitize_url_for_log",
    "validate_output_path",
    "parse_proxy_url",
    "sanitize_proxy_for_log",
    "build_proxy_dict",
]
