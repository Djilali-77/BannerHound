# 🕵️‍♂️ Net-Auditor: Stealth Network Scanner & OS Fingerprinter

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![Networking](https://img.shields.io/badge/Networking-Sockets%20%7C%20Paramiko-red)

## 📖 Overview
**Net-Auditor** is a full-stack, credential-less network scanning and OS fingerprinting tool. Imagine walking into a new corporate environment with hundreds of devices and zero documentation. This tool acts as your network reconnaissance agent, identifying Cisco routers, Linux servers, and firewalls across an entire subnet in seconds—**without needing any passwords**.

## ✨ Key Features
- **Credential-Less OS Fingerprinting:** Uses "Hit and Run" SSH Banner Grabbing to identify devices without authenticating.
- **High-Performance Multi-Threading:** Scans large subnets (e.g., a `/24` network) in mere seconds using Python's concurrent execution (`ThreadPoolExecutor`), bypassing the limitations of sequential scanning.
- **Full-Stack Architecture:** 
  - **Backend:** Python, FastAPI, Sockets, Paramiko.
  - **Frontend:** Modern UI (Vite) to visualize the network landscape.
- **CSV Reporting:** Built-in functionality to export scan results into clean, organized CSV reports for auditing purposes.
- **Dockerized:** Fully containerized with `docker-compose` for instant, isolated deployment.

## ⚙️ How It Works (Under the Hood)
1. **Rapid Port Scanning (Sockets):** The engine uses Python `sockets` combined with multi-threading to knock on port 22 (SSH) across up to 254 IPs concurrently.
2. **Banner Grabbing (Paramiko):** For every open port 22, it briefly connects to intercept the "Welcome Banner" sent by the server, then immediately drops the connection.
3. **Fingerprinting & Analysis:** The tool parses the grabbed banners (e.g., `Cisco` → Cisco Router/Switch, `Ubuntu` → Linux Server) using logic rules.
4. **Reporting:** Results are sent to the frontend via a REST API and can be exported to a `report.csv` file.

## 📂 Project Structure
```text
.
├── backend/
│   ├── main.py            # FastAPI application & CSV export logic
│   ├── scanner.py         # Multi-threaded socket scanning logic
│   ├── banner.py          # Paramiko hit-and-run logic
│   ├── analyzer.py        # Banner parsing and OS mapping
│   ├── Dockerfile         # Backend container specs
│   └── requirements.txt
├── frontend/
│   ├── src/               # React/Vue/Vite frontend source
│   ├── package.json
│   └── Dockerfile         # Frontend container specs
└── docker-compose.yml     # Orchestration
```

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose installed on your machine.

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/net-auditor.git
   cd net-auditor
   ```
2. Start the application using Docker Compose:
   ```bash
   docker compose up --build
   ```
3. Access the application:
   - **Frontend Dashboard:** `http://localhost:5173`
   - **Backend API Docs (Swagger):** `http://localhost:8000/docs`

## ⚠️ Disclaimer
This tool is designed for **authorized network auditing and educational purposes only**. Do not use it against networks you do not own or have explicit permission to scan.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
[MIT License](LICENSE)
