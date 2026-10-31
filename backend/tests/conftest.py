"""Shared fixtures for the BannerHound test suite."""
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from fastapi.testclient import TestClient

import main
import scanner


@pytest.fixture(autouse=True)
def private_scans_only(monkeypatch):
    """Make every test independent of the ALLOW_PUBLIC_SCAN environment variable."""
    monkeypatch.setattr(scanner, "ALLOW_PUBLIC_SCAN", False)


@pytest.fixture
def reports_dir(tmp_path, monkeypatch):
    """Send CSV reports to a temporary folder instead of backend/data."""
    path = tmp_path / "reports"
    path.mkdir()
    monkeypatch.setattr(main, "REPORTS_DIR", path)
    return path


@pytest.fixture
def client(reports_dir):
    """API client whose reports are stored in a temporary folder."""
    return TestClient(main.app)


@pytest.fixture
def tcp_server():
    """Start a fake TCP service that sends a payload to its first client."""
    listeners = []

    def start(payload: bytes) -> int:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        listener.settimeout(5)
        listeners.append(listener)

        def serve():
            try:
                conn, _ = listener.accept()
            except OSError:
                return
            with conn:
                conn.settimeout(2)
                try:
                    conn.sendall(payload)
                    conn.recv(4096)  # wait until the client answers or disconnects
                except OSError:
                    pass

        threading.Thread(target=serve, daemon=True).start()
        return listener.getsockname()[1]

    yield start

    for listener in listeners:
        listener.close()


@pytest.fixture
def http_server():
    """Start a fake web server that answers every HEAD request."""
    servers = []

    def start(status: int = 200, server_name: str = "TestServer/1.0") -> int:
        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self):
                self.send_response(status)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def version_string(self):
                # Value of the "Server" response header
                return server_name

            def log_message(self, *args):
                pass  # keep the test output clean

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        return server.server_address[1]

    yield start

    for server in servers:
        server.shutdown()
        server.server_close()