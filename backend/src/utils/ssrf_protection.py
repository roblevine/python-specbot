"""
SSRF Protection Utilities

Prevents Server-Side Request Forgery (SSRF) attacks by blocking requests
to private IP ranges, localhost, and cloud metadata endpoints.

Feature: Security Hardening
"""

import ipaddress
import socket
from typing import Tuple
from urllib.parse import urlparse


class SSRFProtectionError(Exception):
    """Raised when a URL fails SSRF protection checks."""
    pass


# Private IP ranges to block (RFC 1918 + others)
BLOCKED_IP_RANGES = [
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("10.0.0.0/8"),       # Private network
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / AWS metadata
    ipaddress.ip_network("172.16.0.0/12"),    # Private network
    ipaddress.ip_network("192.168.0.0/16"),   # Private network
    ipaddress.ip_network("224.0.0.0/4"),      # Multicast
    ipaddress.ip_network("240.0.0.0/4"),      # Reserved
    # IPv6 ranges
    ipaddress.ip_network("::1/128"),          # Loopback
    ipaddress.ip_network("fe80::/10"),        # Link-local
    ipaddress.ip_network("fc00::/7"),         # Private
]


def is_ip_blocked(ip: str) -> bool:
    """
    Check if an IP address is in a blocked range.
    
    Args:
        ip: IP address string
        
    Returns:
        True if IP is blocked, False otherwise
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        for blocked_range in BLOCKED_IP_RANGES:
            if ip_obj in blocked_range:
                return True
        return False
    except ValueError:
        # Invalid IP address
        return True


def resolve_hostname(hostname: str) -> Tuple[str, str]:
    """
    Resolve hostname to IP address.
    
    Args:
        hostname: Hostname to resolve
        
    Returns:
        Tuple of (hostname, resolved_ip)
        
    Raises:
        SSRFProtectionError: If hostname cannot be resolved
    """
    try:
        resolved_ip = socket.gethostbyname(hostname)
        return hostname, resolved_ip
    except socket.gaierror as e:
        raise SSRFProtectionError(f"Cannot resolve hostname: {hostname}") from e


def validate_url_for_ssrf(url: str) -> Tuple[str, str]:
    """
    Validate a URL for SSRF protection.
    
    Checks:
    1. URL scheme is http or https
    2. Hostname resolves to a public IP (not private/local)
    3. IP is not in blocked ranges
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (hostname, resolved_ip)
        
    Raises:
        SSRFProtectionError: If URL fails validation
    """
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise SSRFProtectionError(f"Invalid URL format: {url}") from e
    
    # Validate scheme
    if parsed.scheme not in ("http", "https"):
        raise SSRFProtectionError(
            f"Invalid URL scheme: {parsed.scheme}. Only http and https are allowed."
        )
    
    hostname = parsed.hostname
    if not hostname:
        raise SSRFProtectionError("URL must have a hostname")
    
    # Check if hostname is already an IP address
    try:
        ip_obj = ipaddress.ip_address(hostname)
        # Hostname is an IP address
        if is_ip_blocked(str(ip_obj)):
            raise SSRFProtectionError(
                f"Access to IP address {hostname} is blocked (private/internal network)"
            )
        return hostname, str(ip_obj)
    except ValueError:
        # Hostname is not an IP, needs DNS resolution
        pass
    
    # Resolve hostname to IP
    hostname, resolved_ip = resolve_hostname(hostname)
    
    # Check if resolved IP is blocked
    if is_ip_blocked(resolved_ip):
        raise SSRFProtectionError(
            f"Access to {hostname} ({resolved_ip}) is blocked (private/internal network)"
        )
    
    return hostname, resolved_ip
