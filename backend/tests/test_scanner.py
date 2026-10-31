import socket

import pytest

import scanner


def free_port() -> int:
    """Return a port that is (almost certainly) closed on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def open_port():
    """A real listening port on localhost."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(5)
    yield listener.getsockname()[1]
    listener.close()


# ---------------------------------------------------------------- parse_subnet
def test_parse_subnet_returns_all_hosts_of_a_slash_24():
    hosts = scanner.parse_subnet("192.168.1.0/24")
    assert len(hosts) == 254
    assert hosts[0] == "192.168.1.1"
    assert hosts[-1] == "192.168.1.254"


def test_parse_subnet_accepts_host_bits_and_whitespace():
    assert len(scanner.parse_subnet("  192.168.1.77/24 ")) == 254


def test_parse_subnet_accepts_a_single_host():
    assert scanner.parse_subnet("10.0.0.5/32") == ["10.0.0.5"]


def test_parse_subnet_accepts_the_size_limit():
    assert len(scanner.parse_subnet("10.0.0.0/22")) == 1022


def test_parse_subnet_rejects_garbage():
    with pytest.raises(ValueError, match="Invalid subnet"):
        scanner.parse_subnet("not-a-subnet")


def test_parse_subnet_rejects_ipv6():
    with pytest.raises(ValueError, match="IPv4"):
        scanner.parse_subnet("fe80::/64")


@pytest.mark.parametrize("subnet", ["0.0.0.0/0", "10.0.0.0/8", "10.0.0.0/21"])
def test_parse_subnet_rejects_huge_subnets(subnet):
    with pytest.raises(ValueError, match="too large"):
        scanner.parse_subnet(subnet)


def test_parse_subnet_blocks_public_ranges_by_default():
    with pytest.raises(ValueError, match="Public"):
        scanner.parse_subnet("8.8.8.0/24")


def test_parse_subnet_allows_public_ranges_when_enabled(monkeypatch):
    monkeypatch.setattr(scanner, "ALLOW_PUBLIC_SCAN", True)
    assert len(scanner.parse_subnet("8.8.8.0/30")) == 2


# ------------------------------------------------------------------ check_port
def test_check_port_detects_an_open_port(open_port):
    assert scanner.check_port("127.0.0.1", open_port) is True


def test_check_port_detects_a_closed_port():
    assert scanner.check_port("127.0.0.1", free_port()) is False


# ------------------------------------------------------------- discover_hosts
def test_discover_hosts_reports_only_the_open_ports(monkeypatch, open_port):
    monkeypatch.setattr(scanner, "PORTS", [open_port, free_port()])
    assert scanner.discover_hosts("127.0.0.1/32") == {"127.0.0.1": [open_port]}


def test_discover_hosts_ignores_hosts_without_open_ports(monkeypatch):
    # Regression test: the first version marked every IP as open
    monkeypatch.setattr(scanner, "PORTS", [free_port()])
    assert scanner.discover_hosts("127.0.0.1/32") == {}


def test_scan_network_returns_a_sorted_list_of_ips(monkeypatch, open_port):
    monkeypatch.setattr(scanner, "PORTS", [open_port])
    assert scanner.scan_network("127.0.0.1/32") == ["127.0.0.1"]