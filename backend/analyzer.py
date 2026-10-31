"""Turn raw service banners into a device type and a risk assessment."""
import re

# Rules are checked in order, the first match wins.
# Keywords are lowercase because banners are lowercased before matching.
SSH_RULES = [
    ("cisco", "Cisco Router/Switch"),
    ("rosssh", "MikroTik Router"),
    ("rossh", "MikroTik Router"),
    ("mikrotik", "MikroTik Router"),
    ("ubuntu", "Linux Server (Ubuntu)"),
    ("debian", "Linux Server (Debian)"),
    ("raspbian", "Raspberry Pi (Raspbian)"),
    ("freebsd", "FreeBSD Server"),
    ("for_windows", "Windows Host (OpenSSH)"),
    ("dropbear", "Embedded Linux (Dropbear SSH)"),
]

WEB_RULES = [
    ("simplehttp", "Dev Web Server (Python http.server)"),
    ("apache", "Web Server (Apache)"),
    ("nginx", "Web Server (Nginx)"),
    ("microsoft-iis", "Web Server (IIS)"),
    ("microhttpd", "Router / Embedded Device"),
    ("lighttpd", "Router / Embedded Device"),
]

SSH_BANNER_RE = re.compile(r"^SSH-(\d+\.\d+)-(\S+)")
OPENSSH_VERSION_RE = re.compile(r"openssh[_-](\d+)\.(\d+)", re.IGNORECASE)


def _first_match(text: str, rules: list[tuple[str, str]]) -> str | None:
    """Return the device type of the first rule whose keyword is in text."""
    for keyword, device_type in rules:
        if keyword in text:
            return device_type
    return None


def _generic_ssh_name(banner: str) -> str:
    """Build a readable name from an unknown SSH banner."""
    match = SSH_BANNER_RE.match(banner)
    if not match:
        return "SSH Server"
    software = match.group(2).replace("_", " ")  # OpenSSH_9.6 -> OpenSSH 9.6
    return f"SSH Server ({software})"


def analyze_banner(banner: str | None) -> str:
    """Guess the device type from a banner."""
    if not banner:
        return "Unknown or Offline"

    lowered = banner.lower()

    if banner.startswith("SSH-"):
        return _first_match(lowered, SSH_RULES) or _generic_ssh_name(banner)

    if lowered.startswith(("http:", "https:")):
        match = _first_match(lowered, WEB_RULES)
        if match:
            return match
        if lowered.startswith("https:"):
            return "Secure Web Server (HTTPS)"
        return "Web Device (HTTP Open)"

    if lowered.startswith("telnet:"):
        if "cisco" in lowered or "router" in lowered:
            return "Legacy Cisco/Router (Telnet)"
        return "Legacy Device (Telnet Open)"

    return "Unknown Device"


def assess_risk(banner: str | None) -> tuple[str, str]:
    """Return (risk_level, reason) for a banner.

    Levels: High, Medium, Low, Info. This is a simple heuristic based on
    the protocol and version only, it is NOT a full vulnerability scan.
    """
    if not banner:
        return "Info", "No banner could be read"

    lowered = banner.lower()

    if lowered.startswith("telnet:"):
        return "High", "Telnet sends everything, including passwords, in clear text"

    if banner.startswith("SSH-"):
        proto = SSH_BANNER_RE.match(banner)
        if proto:
            version = proto.group(1)
            # 1.99 means "supports both 1.x and 2.0", so it is not flagged
            if version.startswith("1.") and version != "1.99":
                return "High", "SSH protocol 1 is obsolete and insecure"

        openssh = OPENSSH_VERSION_RE.search(banner)
        if openssh and int(openssh.group(1)) < 8:
            return "Medium", (
                f"Outdated OpenSSH {openssh.group(1)}.{openssh.group(2)} "
                "(versions before 8.0)"
            )
        return "Low", "SSH traffic is encrypted"

    if lowered.startswith("https:"):
        return "Low", "Traffic is encrypted with TLS"

    if lowered.startswith("http:"):
        return "Medium", "Plain HTTP: traffic is not encrypted"

    return "Info", "Unrecognized service"