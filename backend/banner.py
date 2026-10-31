"""Banner grabbing helpers.

Each function connects to ONE service, reads the identification string
the server volunteers, and disconnects immediately ("hit and run").
No authentication is ever attempted.
"""
import socket
import ssl
import urllib.error
import urllib.request

import paramiko

# Seconds to wait for each network operation
TIMEOUT = 1.5


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow redirects, so we only ever talk to the target IP."""

    def redirect_request(self, *args, **kwargs):
        return None


# TLS certificate checks are disabled on purpose: we only read the
# Server header, and most LAN devices use self-signed certificates.
_INSECURE_CTX = ssl.create_default_context()
_INSECURE_CTX.check_hostname = False
_INSECURE_CTX.verify_mode = ssl.CERT_NONE

_OPENER = urllib.request.build_opener(
    _NoRedirect,
    urllib.request.HTTPSHandler(context=_INSECURE_CTX),
)


def get_ssh_banner(ip: str, port: int = 22) -> str | None:
    """Return the SSH identification string, e.g. 'SSH-2.0-OpenSSH_9.6'."""
    sock = None
    transport = None
    try:
        sock = socket.create_connection((ip, port), timeout=TIMEOUT)
        transport = paramiko.Transport(sock)
        try:
            transport.start_client(timeout=TIMEOUT)
        except Exception:
            # The version string is exchanged before the key exchange,
            # so it can still be available even if the handshake fails.
            pass
        return transport.remote_version or None
    except Exception:
        return None
    finally:
        if transport is not None:
            transport.close()
        if sock is not None:
            sock.close()


def _http_banner(ip: str, scheme: str) -> str | None:
    """Send a HEAD request and return '<SCHEME>: <Server header>'."""
    label = scheme.upper()
    request = urllib.request.Request(f"{scheme}://{ip}", method="HEAD")
    try:
        with _OPENER.open(request, timeout=TIMEOUT) as response:
            headers = response.headers
    except urllib.error.HTTPError as err:
        # 301, 401, 403, 405... still carry a valid Server header
        headers = err.headers
    except Exception:
        return None

    server = headers.get("Server")
    return f"{label}: {server}" if server else f"{label}: Unknown Web Server"


def get_http_banner(ip: str) -> str | None:
    return _http_banner(ip, "http")


def get_https_banner(ip: str) -> str | None:
    return _http_banner(ip, "https")


def get_telnet_banner(ip: str, port: int = 23) -> str | None:
    """Return the first bytes sent by a Telnet service."""
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT) as sock:
            try:
                raw = sock.recv(1024)
            except socket.timeout:
                raw = b""
    except OSError:
        return None

    text = raw.decode("utf-8", errors="ignore")
    # Drop Telnet negotiation bytes and other non-printable characters
    text = "".join(ch for ch in text if ch.isprintable()).strip()
    return f"Telnet: {text[:50]}" if text else "Telnet: Open"


# Probe order: the most informative services first
_GRABBERS = [
    (22, get_ssh_banner),
    (80, get_http_banner),
    (443, get_https_banner),
    (23, get_telnet_banner),
]


def get_device_banner(ip: str, open_ports: list[int] | None = None) -> str | None:
    """Return the best banner available for a host.

    If open_ports is given (from the port scan), closed services are
    skipped, which avoids wasting time on useless connection attempts.
    """
    for port, grabber in _GRABBERS:
        if open_ports is not None and port not in open_ports:
            continue
        banner = grabber(ip)
        if banner:
            return banner
    return None