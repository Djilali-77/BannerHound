"""Fast multi-threaded TCP scanner used for host discovery.

A host is considered "alive" when at least one of the probed ports
(SSH, Telnet, HTTP, HTTPS) accepts a TCP connection.
"""
import concurrent.futures
import ipaddress
import os
import socket

# Ports probed on every host: SSH, Telnet, HTTP, HTTPS
PORTS = [22, 23, 80, 443]

# Tunable limits
CONNECT_TIMEOUT = 0.8  # seconds to wait for each TCP connection
MAX_WORKERS = 100      # number of concurrent threads
MAX_HOSTS = 1024       # refuse subnets bigger than a /22

# Scanning public ranges is disabled by default (authorized auditing only).
# Set ALLOW_PUBLIC_SCAN=true in the environment to override.
ALLOW_PUBLIC_SCAN = os.getenv("ALLOW_PUBLIC_SCAN", "false").lower() == "true"


def parse_subnet(subnet: str) -> list[str]:
    """Validate a subnet string and return the list of host IPs.

    Raises:
        ValueError: if the subnet is invalid, too large, or not private.
    """
    try:
        network = ipaddress.ip_network(subnet.strip(), strict=False)
    except ValueError:
        raise ValueError(f"Invalid subnet: '{subnet}'. Example: 192.168.1.0/24")

    if network.version != 4:
        raise ValueError("Only IPv4 subnets are supported.")

    if network.num_addresses > MAX_HOSTS:
        raise ValueError(
            f"Subnet too large ({network.num_addresses} addresses). "
            f"Maximum allowed is {MAX_HOSTS} (/22)."
        )

    if not network.is_private and not ALLOW_PUBLIC_SCAN:
        raise ValueError(
            "Public IP ranges are blocked. Only scan networks you are "
            "authorized to audit."
        )

    return [str(ip) for ip in network.hosts()]


def check_port(ip: str, port: int) -> bool:
    """Return True if a TCP connection to ip:port succeeds."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(CONNECT_TIMEOUT)
            return sock.connect_ex((ip, port)) == 0
    except OSError:
        return False


def discover_hosts(subnet: str) -> dict[str, list[int]]:
    """Scan a subnet and return {ip: [open_ports]} for every live host."""
    ips = parse_subnet(subnet)
    open_ports: dict[str, list[int]] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # One task per (ip, port) pair, so all probes run in parallel
        futures = {
            executor.submit(check_port, ip, port): (ip, port)
            for ip in ips
            for port in PORTS
        }
        for future in concurrent.futures.as_completed(futures):
            ip, port = futures[future]
            if future.result():
                open_ports.setdefault(ip, []).append(port)

    # Sort ports for each host so the output is stable
    return {ip: sorted(ports) for ip, ports in open_ports.items()}


def scan_network(subnet: str) -> list[str]:
    """Return the sorted list of live IPs (kept for backward compatibility)."""
    hosts = discover_hosts(subnet)
    return sorted(hosts, key=ipaddress.IPv4Address)