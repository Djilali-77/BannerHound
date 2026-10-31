"""Fake legacy Cisco device for the BannerHound lab.

It listens on Telnet port 23 and sends a banner to every client.
It never accepts a login, it only exists so the scanner has a High risk
target to find.
"""
import socket
import threading

HOST = "0.0.0.0"
PORT = 23
BANNER = b"\r\nCisco IOS Software - Authorized access only\r\n"


def handle_client(conn: socket.socket) -> None:
    """Send the banner, wait a moment, then close the connection."""
    with conn:
        conn.settimeout(3)
        try:
            conn.sendall(BANNER)
            conn.recv(1024)
        except OSError:
            pass


def main() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(16)
    print(f"Fake Telnet device listening on {HOST}:{PORT}", flush=True)

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()