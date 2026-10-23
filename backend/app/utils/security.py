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
    """Reject non-HTTP URLs, credentials, and non-public IPv4/IPv6 destinations."""
    import ipaddress
    import socket

    if not isinstance(url, str) or not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False
        if parsed.username or parsed.password:
            return False
        host = parsed.hostname
        port = parsed.port
        if host.lower() == "localhost" or any(re.search(pattern, host, re.I) for pattern in CLOUD_METADATA_PATTERNS):
            return False
        try:
            addresses = [ipaddress.ip_address(host)]
        except ValueError:
            addresses = [ipaddress.ip_address(info[4][0]) for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)]
        if not addresses:
            return False
        for address in addresses:
            if address.version == 6 and address.ipv4_mapped:
                address = address.ipv4_mapped
            if not address.is_global or address.is_multicast:
                return False
        return True
    except (ValueError, OSError):
        return False


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
