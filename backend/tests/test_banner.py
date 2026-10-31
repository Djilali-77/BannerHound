import pytest

import banner


# ------------------------------------------------------------------------ HTTP
def test_http_banner_reads_the_server_header(http_server):
    port = http_server()
    assert banner.get_http_banner(f"127.0.0.1:{port}") == "HTTP: TestServer/1.0"


@pytest.mark.parametrize("status", [301, 401, 403, 404, 405, 500])
def test_http_banner_keeps_the_server_header_on_error_statuses(http_server, status):
    # Regression test: these responses used to return None
    port = http_server(status=status)
    assert banner.get_http_banner(f"127.0.0.1:{port}") == "HTTP: TestServer/1.0"


def test_http_banner_without_server_header(http_server):
    port = http_server(server_name="")
    assert banner.get_http_banner(f"127.0.0.1:{port}") == "HTTP: Unknown Web Server"


def test_http_banner_returns_none_when_nothing_listens():
    assert banner.get_http_banner("127.0.0.1:1") is None


# ---------------------------------------------------------------------- Telnet
def test_telnet_banner_strips_negotiation_bytes(tcp_server):
    port = tcp_server(b"\xff\xfd\x18Cisco IOS ready\r\n")
    assert banner.get_telnet_banner("127.0.0.1", port) == "Telnet: Cisco IOS ready"


def test_telnet_banner_is_truncated_to_50_characters(tcp_server):
    port = tcp_server(b"A" * 100)
    assert banner.get_telnet_banner("127.0.0.1", port) == "Telnet: " + "A" * 50


def test_telnet_banner_returns_none_when_nothing_listens():
    assert banner.get_telnet_banner("127.0.0.1", port=1) is None


# ------------------------------------------------------------------------- SSH
def test_ssh_banner_reads_the_identification_string(tcp_server):
    port = tcp_server(b"SSH-2.0-OpenSSH_9.6\r\n")
    assert banner.get_ssh_banner("127.0.0.1", port) == "SSH-2.0-OpenSSH_9.6"


def test_ssh_banner_returns_none_when_nothing_listens():
    assert banner.get_ssh_banner("127.0.0.1", port=1) is None


# ------------------------------------------------------------ get_device_banner
def fake_grabber(calls, name, result):
    def grabber(ip):
        calls.append(name)
        return result

    return grabber


def test_device_banner_skips_closed_ports(monkeypatch):
    calls = []
    monkeypatch.setattr(
        banner,
        "_GRABBERS",
        [
            (22, fake_grabber(calls, "ssh", "SSH-2.0-Test")),
            (80, fake_grabber(calls, "http", "HTTP: test")),
        ],
    )
    assert banner.get_device_banner("10.0.0.1", [80]) == "HTTP: test"
    assert calls == ["http"]


def test_device_banner_prefers_ssh_over_http(monkeypatch):
    calls = []
    monkeypatch.setattr(
        banner,
        "_GRABBERS",
        [
            (22, fake_grabber(calls, "ssh", "SSH-2.0-Test")),
            (80, fake_grabber(calls, "http", "HTTP: test")),
        ],
    )
    assert banner.get_device_banner("10.0.0.1", [22, 80]) == "SSH-2.0-Test"
    assert calls == ["ssh"]


def test_device_banner_tries_the_next_service_when_one_fails(monkeypatch):
    calls = []
    monkeypatch.setattr(
        banner,
        "_GRABBERS",
        [
            (22, fake_grabber(calls, "ssh", None)),
            (80, fake_grabber(calls, "http", "HTTP: test")),
        ],
    )
    assert banner.get_device_banner("10.0.0.1") == "HTTP: test"
    assert calls == ["ssh", "http"]