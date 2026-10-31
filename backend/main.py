"""BannerHound API.

Endpoints:
    GET /api/health            liveness check
    GET /api/scan              blocking scan, returns all results at once
    GET /api/scan/stream       live scan using Server-Sent Events (SSE)
    GET /api/download-report   download a CSV report
"""
import asyncio
import csv
import ipaddress
import json
import logging
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from analyzer import analyze_banner, assess_risk
from banner import get_device_banner
from scanner import discover_hosts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("bannerhound")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", BASE_DIR / "data" / "reports"))
MAX_REPORTS = 20       # older CSV reports are deleted automatically
BANNER_WORKERS = 30    # parallel banner grabbing threads
TELNET_PORT = 23

# Only these frontends may call the API from a browser
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

CSV_HEADERS = ["IP", "Status", "Open Ports", "Device Type", "Risk", "Risk Reason", "Banner"]
SCAN_ID_RE = re.compile(r"[0-9a-f]{32}")

# Fake hosts returned when the subnet is "test" (demo mode, no network needed)
DEMO_HOSTS = [
    ("192.168.1.1", [22, 80], "SSH-2.0-Cisco-1.25"),
    ("192.168.1.10", [22, 80, 443], "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"),
    ("192.168.1.25", [22], "SSH-2.0-ROSSSH"),
    ("192.168.1.40", [23], "Telnet: Open"),
    ("192.168.1.100", [22], "SSH-2.0-Custom-Server"),
]

app = FastAPI(
    title="BannerHound API",
    description="Credential-less network scanner and OS fingerprinter.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_demo(subnet: str) -> bool:
    return subnet.strip().lower() == "test"


def build_result(ip: str, open_ports: list[int], banner: str | None) -> dict:
    """Combine a banner and the open ports into one result row."""
    risk, reason = assess_risk(banner)

    # A Telnet port is dangerous even if another service answered first
    if TELNET_PORT in open_ports and risk != "High":
        risk = "High"
        reason = "Telnet (port 23) is open: it sends credentials in clear text"

    return {
        "IP": ip,
        "Status": "Open",
        "Open Ports": open_ports,
        "Device Type": analyze_banner(banner),
        "Risk": risk,
        "Risk Reason": reason,
        "Banner": banner if banner else "No Banner",
    }


def fingerprint_host(ip: str, open_ports: list[int]) -> dict:
    """Grab the banner of one host (runs inside a worker thread)."""
    banner = get_device_banner(ip, open_ports)
    return build_result(ip, open_ports, banner)


def sort_by_ip(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: ipaddress.IPv4Address(row["IP"]))


def sse(data: dict, event: str | None = None) -> str:
    """Format one Server-Sent Event message."""
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# CSV reports (one file per scan, so concurrent users never overwrite
# each other)
# ---------------------------------------------------------------------------
def _csv_safe(value) -> str:
    """Neutralize CSV injection.

    Banners come from remote devices we do not control. A banner starting
    with '=' could run as a formula when the CSV is opened in Excel.
    """
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def _to_csv_row(row: dict) -> dict:
    flat = {**row, "Open Ports": ", ".join(str(p) for p in row["Open Ports"])}
    return {key: _csv_safe(flat[key]) for key in CSV_HEADERS}


def _prune_reports() -> None:
    """Keep only the newest MAX_REPORTS files."""
    files = sorted(
        REPORTS_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for old_file in files[MAX_REPORTS:]:
        old_file.unlink(missing_ok=True)


def save_report(rows: list[dict], scan_id: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{scan_id}.csv"

    with open(path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(_to_csv_row(row) for row in rows)

    _prune_reports()
    return path


def report_path(scan_id: str) -> Path:
    # Strict format check: also blocks path traversal like "../../etc/passwd"
    if not SCAN_ID_RE.fullmatch(scan_id):
        raise HTTPException(status_code=400, detail="Invalid scan_id.")
    return REPORTS_DIR / f"{scan_id}.csv"


def latest_report() -> Path | None:
    return max(
        REPORTS_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, default=None
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/scan")
def scan_endpoint(subnet: str):
    """Run a full scan and return every result in one response."""
    logger.info("Starting scan for: %s", subnet)

    if is_demo(subnet):
        rows = [build_result(*host) for host in DEMO_HOSTS]
    else:
        try:
            hosts = discover_hosts(subnet)
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))

        # Grab banners of all live hosts in parallel
        with ThreadPoolExecutor(max_workers=BANNER_WORKERS) as executor:
            rows = list(executor.map(lambda item: fingerprint_host(*item), hosts.items()))

    rows = sort_by_ip(rows)
    scan_id = uuid.uuid4().hex
    save_report(rows, scan_id)
    logger.info("Scan %s finished: %d host(s)", scan_id, len(rows))

    return {"status": "success", "scan_id": scan_id, "results": rows}


@app.get("/api/scan/stream")
async def stream_scan_endpoint(subnet: str):
    """Run a scan and push every host to the client as soon as it is ready.

    SSE events:
        start       {"scan_id": "..."}              scan accepted
        hosts       {"total": N}                    live hosts found
        (default)   one result row per host
        scan_error  {"message": "..."}              something went wrong
        close       {"scan_id": "...", "total": N}  scan finished
    """

    async def event_generator():
        scan_id = uuid.uuid4().hex
        rows: list[dict] = []
        tasks: list[asyncio.Task] = []
        logger.info("Starting LIVE scan %s for: %s", scan_id, subnet)

        yield sse({"scan_id": scan_id}, "start")

        try:
            if is_demo(subnet):
                yield sse({"total": len(DEMO_HOSTS)}, "hosts")
                for host in DEMO_HOSTS:
                    await asyncio.sleep(0.6)  # simulate a real scan
                    row = build_result(*host)
                    rows.append(row)
                    yield sse(row)
            else:
                # Phase 1: find live hosts (blocking code, so run in a thread)
                hosts = await asyncio.to_thread(discover_hosts, subnet)
                yield sse({"total": len(hosts)}, "hosts")

                # Phase 2: grab all banners in parallel and stream each
                # result the moment it finishes (not in IP order)
                tasks = [
                    asyncio.create_task(asyncio.to_thread(fingerprint_host, ip, ports))
                    for ip, ports in hosts.items()
                ]
                for finished in asyncio.as_completed(tasks):
                    row = await finished
                    rows.append(row)
                    yield sse(row)

            rows = sort_by_ip(rows)
            await asyncio.to_thread(save_report, rows, scan_id)
            logger.info("Scan %s finished: %d host(s)", scan_id, len(rows))
            yield sse({"scan_id": scan_id, "total": len(rows)}, "close")

        except ValueError as err:
            # Invalid or forbidden subnet
            yield sse({"message": str(err)}, "scan_error")
            yield sse({}, "close")
        except Exception:
            logger.exception("Scan %s crashed", scan_id)
            yield sse({"message": "Internal error during the scan."}, "scan_error")
            yield sse({}, "close")
        finally:
            # If the client disconnected, stop the work that has not started yet
            for task in tasks:
                task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/download-report")
def download_report(scan_id: str | None = None):
    """Download a CSV report. Without scan_id, the latest report is returned."""
    path = report_path(scan_id) if scan_id else latest_report()

    if path is None or not path.exists():
        raise HTTPException(
            status_code=404, detail="Report not found. Please run a scan first."
        )

    return FileResponse(
        path=path, filename="network_audit_report.csv", media_type="text/csv"
    )