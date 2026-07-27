"""Input sanitization and validation utilities."""

import re
import urllib.parse
from pathlib import Path


def sanitize_url_for_log(url: str) -> str:
    """
    Strip credentials from URL for safe logging.

    Args:
        url: URL potentially containing user:pass@host

    Returns:
        URL with credentials removed.

    Examples:
        >>> sanitize_url_for_log("http://user:pass@host/path?q=1")
        'http://host/path?q=1'
        >>> sanitize_url_for_log("https://host/path")
        'https://host/path'
    """
    try:
        parsed = urllib.parse.urlparse(url)
        # Rebuild without credentials
        netloc = parsed.hostname or ""
        if parsed.port:
            netloc += f":{parsed.port}"
        return urllib.parse.urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ))
    except Exception:
        # Fallback: basic regex strip
        return re.sub(r'://[^:@]+:[^@]+@', '://', url)


def validate_output_path(base: Path, user_path: Path) -> Path:
    """
    Validate that user_path stays within base directory.

    Args:
        base: Allowed base directory.
        user_path: User-provided path (relative or absolute).

    Returns:
        Resolved absolute path within base.

    Raises:
        ValueError: If resolved path escapes base directory.
    """
    base_resolved = base.resolve()
    target_resolved = (base / user_path).resolve()

    if not target_resolved.is_relative_to(base_resolved):
        raise ValueError(
            f"Path {user_path} escapes base directory {base}"
        )

    return target_resolved


def parse_proxy_url(proxy: str) -> dict:
    """
    Parse proxy URL into components.

    Args:
        proxy: URL like http://user:pass@host:port or socks5://host:port

    Returns:
        Dict with keys: scheme, host, port, username, password.
    """
    parsed = urllib.parse.urlparse(proxy)

    if not parsed.scheme or not parsed.hostname:
        raise ValueError(f"Invalid proxy URL: {proxy}")

    result = {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "username": parsed.username,
        "password": parsed.password,
    }

    if result["port"] is None:
        # Default ports
        defaults = {"http": 8080, "https": 8080, "socks5": 1080, "socks4": 1080}
        result["port"] = defaults.get(parsed.scheme, 8080)

    return result


def sanitize_proxy_for_log(proxy: str) -> str:
    """
    Strip credentials from proxy URL for safe logging.

    Args:
        proxy: Proxy URL.

    Returns:
        Sanitized proxy URL.
    """
    return sanitize_url_for_log(proxy)


def build_proxy_dict(proxy: str) -> dict:
    """
    Build requests-compatible proxy dict from URL.

    Args:
        proxy: Proxy URL.

    Returns:
        Dict like {"http": "http://host:port", "https": "http://host:port"}.
    """
    parts = parse_proxy_url(proxy)
    auth = ""
    if parts["username"] and parts["password"]:
        auth = f"{parts['username']}:{parts['password']}@"
    elif parts["username"]:
        auth = f"{parts['username']}@"

    proxy_url = f"{parts['scheme']}://{auth}{parts['host']}:{parts['port']}"
    return {"http": proxy_url, "https": proxy_url}
