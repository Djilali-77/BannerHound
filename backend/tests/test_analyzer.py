import pytest

from analyzer import analyze_banner, assess_risk


@pytest.mark.parametrize(
    ("banner", "expected"),
    [
        ("SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5", "Linux Server (Ubuntu)"),
        ("SSH-2.0-OpenSSH_9.2p1 Debian-2+deb12u10", "Linux Server (Debian)"),
        ("SSH-2.0-Cisco-1.25", "Cisco Router/Switch"),
        ("SSH-2.0-ROSSSH", "MikroTik Router"),
        ("SSH-2.0-dropbear_2020.81", "Embedded Linux (Dropbear SSH)"),
        ("SSH-2.0-OpenSSH_for_Windows_8.1", "Windows Host (OpenSSH)"),
        ("SSH-2.0-OpenSSH_9.6", "SSH Server (OpenSSH 9.6)"),
        ("SSH-2.0-Custom-Server", "SSH Server (Custom-Server)"),
        ("HTTP: Apache/2.4.41 (Ubuntu)", "Web Server (Apache)"),
        ("HTTPS: nginx/1.18.0", "Web Server (Nginx)"),
        ("HTTP: SimpleHTTP/0.6 Python/3.14.0", "Dev Web Server (Python http.server)"),
        ("HTTP: lighttpd/1.4.59", "Router / Embedded Device"),
        ("HTTP: Unknown Web Server", "Web Device (HTTP Open)"),
        ("HTTPS: Unknown Secure Web Server", "Secure Web Server (HTTPS)"),
        ("Telnet: Open", "Legacy Device (Telnet Open)"),
        ("Telnet: Cisco IOS Software", "Legacy Cisco/Router (Telnet)"),
        (None, "Unknown or Offline"),
        ("", "Unknown or Offline"),
        ("something strange", "Unknown Device"),
    ],
)
def test_analyze_banner(banner, expected):
    assert analyze_banner(banner) == expected


@pytest.mark.parametrize(
    ("banner", "expected_level"),
    [
        ("Telnet: Open", "High"),
        ("SSH-1.5-Ancient", "High"),
        ("SSH-1.99-OpenSSH_9.6", "Low"),
        ("SSH-2.0-OpenSSH_7.4", "Medium"),
        ("SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.18", "Low"),
        ("SSH-2.0-OpenSSH_10.0", "Low"),
        ("HTTP: nginx/1.24.0", "Medium"),
        ("HTTPS: nginx/1.24.0", "Low"),
        (None, "Info"),
        ("something strange", "Info"),
    ],
)
def test_assess_risk_level(banner, expected_level):
    level, reason = assess_risk(banner)
    assert level == expected_level
    assert reason


def test_outdated_openssh_reason_mentions_the_version():
    _, reason = assess_risk("SSH-2.0-OpenSSH_7.4")
    assert "7.4" in reason