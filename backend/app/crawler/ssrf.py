import socket
import ipaddress
import urllib.parse
from typing import Tuple, List, Optional
from app.config import settings

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network
    ipaddress.ip_network("10.0.0.0/8"),          # Private RFC1918
    ipaddress.ip_network("100.64.0.0/10"),       # Shared address space
    ipaddress.ip_network("127.0.0.0/8"),         # Loopback
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local / Cloud metadata (AWS, GCP, Azure, etc.)
    ipaddress.ip_network("172.16.0.0/12"),        # Private RFC1918
    ipaddress.ip_network("192.0.0.0/24"),         # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),         # TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"),       # Private RFC1918
    ipaddress.ip_network("198.18.0.0/15"),        # Benchmark testing
    ipaddress.ip_network("198.51.100.0/24"),      # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),       # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),          # Multicast
    ipaddress.ip_network("240.0.0.0/4"),          # Reserved
    ipaddress.ip_network("255.255.255.255/32"),   # Broadcast
    # IPv6
    ipaddress.ip_network("::1/128"),              # Loopback
    ipaddress.ip_network("::/128"),               # Unspecified
    ipaddress.ip_network("fc00::/7"),             # Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),            # Link-local unicast
    ipaddress.ip_network("ff00::/8"),             # Multicast
]

PROHIBITED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "instance-data",
    "169.254.169.254"
}

def is_ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address belongs to any blocked/private/link-local/loopback network."""
    # Check if IPv6 mapped IPv4 address (e.g. ::ffff:127.0.0.1)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True

    for net in BLOCKED_IP_NETWORKS:
        if ip in net:
            return True

    return False

def is_safe_url(url: str) -> Tuple[bool, str]:
    """
    Validates URL safety against Server-Side Request Forgery (SSRF).
    Returns (is_safe: bool, reason: str).
    """
    if not url or not isinstance(url, str):
        return False, "URL is empty or not a valid string."

    url = url.strip()
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        return False, f"Malformed URL syntax: {str(e)}"

    # 1. Scheme check
    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        return False, f"Unsupported URL scheme '{scheme}'. Only HTTP and HTTPS are permitted."

    # Validate port safely (parsed.port raises ValueError on invalid port numbers like 99999)
    try:
        port = parsed.port
        if port is not None and not (1 <= port <= 65535):
            return False, f"Port '{port}' is outside the valid range (1-65535)."
    except ValueError as e:
        return False, f"Invalid port in URL: {str(e)}"

    hostname = parsed.hostname
    if not hostname:
        return False, "URL missing valid hostname or netloc."

    # Strip enclosing brackets from IPv6 hostnames
    cleaned_hostname = hostname.strip("[]").lower()

    # Reject null bytes or control characters in hostname
    if any(ord(c) < 32 or ord(c) == 127 for c in cleaned_hostname):
        return False, "Hostname contains invalid control characters."

    # Allow demo.local bypass for testing when configured
    if settings.SSRF_ALLOW_DEMO and cleaned_hostname in ("demo.local", "demo"):
        return True, "Demo target allowed."

    # 2. Check prohibited hostnames
    if cleaned_hostname in PROHIBITED_HOSTNAMES or cleaned_hostname.endswith(".local") or cleaned_hostname.endswith(".internal"):
        return False, f"Access to restricted hostname '{hostname}' is blocked."

    # 3. Direct IP address check
    try:
        ip = ipaddress.ip_address(cleaned_hostname)
        if is_ip_blocked(ip):
            return False, f"Access to IP address '{ip}' is blocked (private/loopback/cloud-metadata)."
        return True, "Safe IP target."
    except ValueError:
        # Hostname is a domain name, proceed to DNS resolution check
        pass

    # 4. Resolve DNS and verify all returned IP addresses
    resolved_port = port or (443 if scheme == "https" else 80)
    try:
        addr_info = socket.getaddrinfo(cleaned_hostname, resolved_port, proto=socket.IPPROTO_TCP)
        if not addr_info:
            return False, f"Could not resolve domain name '{cleaned_hostname}'."

        for entry in addr_info:
            ip_str = entry[4][0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if is_ip_blocked(ip_obj):
                    return False, f"Domain '{cleaned_hostname}' resolved to blocked IP '{ip_str}'."
            except ValueError:
                return False, f"Invalid IP address resolution for domain '{cleaned_hostname}'."

    except socket.gaierror:
        return False, f"DNS resolution failed for hostname '{cleaned_hostname}'."
    except Exception as e:
        return False, f"Network validation failed: {str(e)}"

    return True, "URL validated as safe."
