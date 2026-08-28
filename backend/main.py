from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from scanner import scan_network
from banner import get_device_banner
from analyzer import analyze_banner
import csv
import time
import os
import json
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def export_to_csv(data, filename="report.csv"):
    headers = ['IP', 'Status', 'Banner', 'Device Type']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        writer.writeheader()
        writer.writerows(data)


@app.get("/api/scan")
def scan_endpoint(subnet: str):
    print(f"[*] Starting scan for: {subnet}")
    
    if subnet == "test":
        time.sleep(1.5) 
        return {
            "status": "success",
            "results": [
                {"IP": "192.168.1.1", "Status": "Open", "Device Type": "Cisco Router/Switch", "Banner": "SSH-2.0-Cisco-1.25"},
                {"IP": "192.168.1.10", "Status": "Open", "Device Type": "Linux Server (Ubuntu)", "Banner": "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"},
                {"IP": "192.168.1.25", "Status": "Open", "Device Type": "MikroTik Router", "Banner": "SSH-2.0-ROSSH"},
                {"IP": "192.168.1.100", "Status": "Open", "Device Type": "Unknown or Offline", "Banner": "SSH-2.0-Custom-Server"}
            ]
        }

    ips = scan_network(subnet)
    final_report = []

    for ip in ips:
        banner = get_device_banner(ip)
        result = analyze_banner(banner)

        dic = {
            'IP': ip,
            'Status': 'Open',
            'Banner': banner if banner else "No Banner",
            'Device Type': result
        }
        final_report.append(dic)

    export_to_csv(final_report)

    return {"status": "success", "results": final_report}


@app.get("/api/download-report")
def download_report():
    file_path = "report.csv"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename="network_audit_report.csv", media_type='text/csv')
    return {"error": "Report not found. Please run a scan first."}

@app.get("/api/scan/stream")
async def stream_scan_endpoint(subnet: str):
    async def event_generator():
        print(f"[*] Starting LIVE scan for: {subnet}")
        
        ips = await asyncio.to_thread(scan_network, subnet)
        final_report = []

        for ip in ips:
            banner = await asyncio.to_thread(get_device_banner, ip)
            result = analyze_banner(banner)

            dic = {
                'IP': ip,
                'Status': 'Open',
                'Banner': banner if banner else "No Banner",
                'Device Type': result
            }
            final_report.append(dic)

            yield f"data: {json.dumps(dic)}\n\n"
        
        export_to_csv(final_report)
        
        yield "event: close\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")