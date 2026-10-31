"""API tests. They use demo data or mocks, so no real network is needed."""
import ipaddress
import json

import pytest

import main

FAKE_HOSTS = {"10.0.0.2": [22], "10.0.0.1": [80, 23]}
FAKE_BANNERS = {"10.0.0.1": "HTTP: nginx/1.24.0", "10.0.0.2": "SSH-2.0-OpenSSH_9.6"}


def parse_sse(text):
    """Turn a raw SSE body into a list of (event_name, json_data) tuples."""
    events = []
    for block in text.strip().split("\n\n"):
        name, data = "message", None
        for line in block.splitlines():
            if line.startswith("event: "):
                name = line[len("event: "):]
            elif line.startswith("data: "):
                data = json.loads(line[len("data: "):])
        events.append((name, data))
    return events


@pytest.fixture
def fake_network(monkeypatch):
    """Pretend the scanner found two hosts, without touching the network."""
    monkeypatch.setattr(main, "discover_hosts", lambda subnet: FAKE_HOSTS)
    monkeypatch.setattr(
        main, "get_device_banner", lambda ip, open_ports=None: FAKE_BANNERS[ip]
    )


# ---------------------------------------------------------------- build_result
def test_build_result_flags_telnet_even_when_ssh_answers_first():
    row = main.build_result("10.0.0.9", [22, 23], "SSH-2.0-OpenSSH_9.6")
    assert row["Risk"] == "High"
    assert "Telnet" in row["Risk Reason"]


def test_build_result_without_a_banner():
    row = main.build_result("10.0.0.9", [80], None)
    assert row["Banner"] == "No Banner"
    assert row["Device Type"] == "Unknown or Offline"
    assert row["Risk"] == "Info"


# ------------------------------------------------------------------- CSV safety
def test_csv_safe_neutralizes_spreadsheet_formulas():
    assert main._csv_safe("=1+1") == "'=1+1"
    assert main._csv_safe("@SUM(A1)") == "'@SUM(A1)"
    assert main._csv_safe("SSH-2.0-OpenSSH_9.6") == "SSH-2.0-OpenSSH_9.6"


def test_only_the_newest_reports_are_kept(reports_dir):
    rows = [main.build_result("10.0.0.1", [22], "SSH-2.0-OpenSSH_9.6")]
    for number in range(main.MAX_REPORTS + 5):
        main.save_report(rows, f"{number:032x}")
    assert len(list(reports_dir.glob("*.csv"))) == main.MAX_REPORTS


# ----------------------------------------------------------------------- health
def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


# ------------------------------------------------------------------- /api/scan
def test_demo_scan_returns_sorted_results_with_risk(client):
    response = client.get("/api/scan", params={"subnet": "test"})
    assert response.status_code == 200

    body = response.json()
    rows = body["results"]
    ips = [row["IP"] for row in rows]

    assert len(rows) == 5
    assert ips == sorted(ips, key=ipaddress.IPv4Address)
    assert {row["Risk"] for row in rows} == {"Low", "High"}
    assert len(body["scan_id"]) == 32


def test_scan_sorts_results_and_flags_telnet(client, fake_network):
    rows = client.get("/api/scan", params={"subnet": "10.0.0.0/24"}).json()["results"]

    assert [row["IP"] for row in rows] == ["10.0.0.1", "10.0.0.2"]
    assert rows[0]["Risk"] == "High"  # port 23 is open
    assert rows[1]["Risk"] == "Low"


@pytest.mark.parametrize(
    ("subnet", "message"),
    [
        ("not-a-subnet", "Invalid subnet"),
        ("0.0.0.0/0", "too large"),
        ("8.8.8.0/24", "Public"),
    ],
)
def test_scan_rejects_bad_subnets(client, subnet, message):
    response = client.get("/api/scan", params={"subnet": subnet})
    assert response.status_code == 400
    assert message in response.json()["detail"]


# ----------------------------------------------------------- /api/scan/stream
def test_stream_sends_events_in_order(client, fake_network):
    response = client.get("/api/scan/stream", params={"subnet": "10.0.0.0/24"})
    events = parse_sse(response.text)

    assert [name for name, _ in events] == ["start", "hosts", "message", "message", "close"]

    start, hosts, close = events[0][1], events[1][1], events[-1][1]
    assert hosts == {"total": 2}
    assert close == {"scan_id": start["scan_id"], "total": 2}
    assert {data["IP"] for name, data in events if name == "message"} == set(FAKE_HOSTS)


def test_stream_saves_a_report_that_can_be_downloaded(client, fake_network):
    response = client.get("/api/scan/stream", params={"subnet": "10.0.0.0/24"})
    scan_id = parse_sse(response.text)[0][1]["scan_id"]

    report = client.get("/api/download-report", params={"scan_id": scan_id})
    assert report.status_code == 200


def test_stream_reports_invalid_subnets_as_an_event(client):
    response = client.get("/api/scan/stream", params={"subnet": "0.0.0.0/0"})
    events = parse_sse(response.text)

    assert [name for name, _ in events] == ["start", "scan_error", "close"]
    assert "too large" in events[1][1]["message"]


def test_stream_reports_scanner_failures_as_an_event(client, monkeypatch):
    def explode(subnet):
        raise ValueError("boom")

    monkeypatch.setattr(main, "discover_hosts", explode)

    events = parse_sse(client.get("/api/scan/stream", params={"subnet": "10.0.0.0/24"}).text)
    assert [name for name, _ in events] == ["start", "scan_error", "close"]
    assert events[1][1] == {"message": "boom"}


def test_stream_demo_mode(client, monkeypatch):
    # Two hosts only, so the test stays fast (the demo adds a delay per host)
    monkeypatch.setattr(main, "DEMO_HOSTS", main.DEMO_HOSTS[:2])

    events = parse_sse(client.get("/api/scan/stream", params={"subnet": "test"}).text)
    assert [name for name, _ in events] == ["start", "hosts", "message", "message", "close"]


# ------------------------------------------------------- /api/download-report
def test_download_report_by_scan_id(client):
    scan_id = client.get("/api/scan", params={"subnet": "test"}).json()["scan_id"]

    response = client.get("/api/download-report", params={"scan_id": scan_id})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")

    lines = response.text.splitlines()
    assert lines[0] == "IP,Status,Open Ports,Device Type,Risk,Risk Reason,Banner"
    assert len(lines) == 6  # header + 5 demo hosts


def test_download_latest_report_without_scan_id(client):
    client.get("/api/scan", params={"subnet": "test"})
    assert client.get("/api/download-report").status_code == 200


def test_download_report_before_any_scan(client):
    assert client.get("/api/download-report").status_code == 404


def test_download_report_with_an_unknown_scan_id(client):
    response = client.get("/api/download-report", params={"scan_id": "0" * 32})
    assert response.status_code == 404


def test_download_report_blocks_path_traversal(client):
    response = client.get("/api/download-report", params={"scan_id": "../../etc/passwd"})
    assert response.status_code == 400