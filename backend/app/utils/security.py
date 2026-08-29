"""Security utilities for SSRF protection and URL validation."""

import re
from urllib.parse import urlparse
from typing import Optional

import netaddr


# Private/reserved IP ranges that should never be accessed
PRIVATE_RANGES = [
    netaddr.IPNetwork("10.0.0.0/8"),
    netaddr.IPNetwork("172.16.0.0/12"),
    netaddr.IPNetwork("192.168.0.0/16"),
    netaddr.IPNetwork("127.0.0.0/8"),
    netaddr.IPNetwork("169.254.0.0/16"),
    netaddr.IPNetwork("0.0.0.0/8"),
    netaddr.IPNetwork("100.64.0.0/10"),
]

# Cloud metadata endpoints
CLOUD_METADATA_PATTERNS = [
    r"169\.254\.169\.254",  # AWS
    r"metadata\.google\.internal",
    r"100\.100\.100\.200",  # Azure
    r"100\.\[0-9a-f\]{1,4}:100:7000",  # OCI
]


def is_safe_url(url: str) -> bool:
    """Validate URL is safe to fetch (no SSRF).

    Checks:
    - Scheme is http or https
    - Host resolves to a public IP
    - Host is not a private/reserved range
    - Host is not a cloud metadata endpoint
    """
    parsed = urlparse(url)

    # Only allow http and https
    if parsed.scheme not in ("http", "https"):
        return False

    host = parsed.hostname
    if not host:
        return False

    # Block localhost variants
    if host in ("localhost", "0.0.0.0", "::1"):
        return False

    # Check against cloud metadata patterns
    for pattern in CLOUD_METADATA_PATTERNS:
        if re.search(pattern, host, re.I):
            return False

    # Try to resolve and check IP ranges
    try:
        ip = netaddr.IPAddress(host)
        for private_range in PRIVATE_RANGES:
            if ip in private_range:
                return False
    except netaddr.AddrFormatError:
        # Could not parse as IP — might be a valid hostname
        # Do a DNS lookup to check
        try:
            import socket
            addr_info = socket.getaddrinfo(host, None, socket.AF_INET)
            for info in addr_info:
                ip_str = info[4][0]
                try:
                    ip = netaddr.IPAddress(ip_str)
                    for private_range in PRIVATE_RANGES:
                        if ip in private_range:
                            return False
                except netaddr.AddrFormatError:
                    continue
        except socket.gaierror:
            # DNS resolution failed — allow it (might be a valid private hostname)
            pass

    return True


def validate_url(url: str) -> str:
    """Validate and normalize a URL for crawling.

    Raises ValueError if the URL is invalid or unsafe.
    Returns the normalized URL.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    # Strip whitespace
    url = url.strip()

    # Validate existing scheme before injecting one
    parsed = urlparse(url)
    if parsed.scheme:
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid scheme: {parsed.scheme}. Only http and https are allowed.")
    else:
        url = "https://" + url

    parsed = urlparse(url)

    # Validate scheme
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid scheme: {parsed.scheme}. Only http and https are allowed.")

    # Validate hostname
    if not parsed.hostname:
        raise ValueError("Invalid URL: no hostname")

    # SSRF protection
    if not is_safe_url(url):
        raise ValueError("URL points to a private or reserved address. Access denied.")

    return url
