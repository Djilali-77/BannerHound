import paramiko
import urllib.request
import socket
import ssl

def get_ssh_banner(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        sock.connect((ip, 22))
        transport = paramiko.Transport(sock)
        transport.start_client()
        banner = transport.remote_version
        transport.close()
        return banner
    except Exception:
        return None

def get_http_banner(ip):
    try:
        req = urllib.request.Request(f"http://{ip}", method="HEAD")
        with urllib.request.urlopen(req, timeout=1.5) as response:
            server = response.headers.get('Server')
            if server:
                return f"HTTP: {server}"
            return "HTTP: Unknown Web Server"
    except Exception:
        return None

def get_https_banner(ip):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(f"https://{ip}", method="HEAD")
        with urllib.request.urlopen(req, timeout=1.5, context=ctx) as response:
            server = response.headers.get('Server')
            if server:
                return f"HTTPS: {server}"
            return "HTTPS: Unknown Secure Web Server"
    except Exception:
        return None

def get_telnet_banner(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        sock.connect((ip, 23))
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        if banner:
            return f"Telnet: {banner[:50]}"
        return "Telnet: Open"
    except Exception:
        return None

def get_device_banner(ip):
    banner = get_ssh_banner(ip)
    if banner: return banner
    
    banner = get_http_banner(ip)
    if banner: return banner
    
    banner = get_https_banner(ip)
    if banner: return banner
    
    return get_telnet_banner(ip)