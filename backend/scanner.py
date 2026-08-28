import socket
import concurrent.futures
import ipaddress

PORT = 22

def scan_port(ip):

    #--------------------------IPv4-------------TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

        client_socket.settimeout(1)    
        result = client_socket.connect_ex((ip, PORT))
        return result == 0

def scan_network(subnet):

    ips = list(ipaddress.IPv4Network(subnet, strict=False).hosts())
    string_ips = [str(ip) for ip in ips]

    ipsList = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:

        results = executor.map(scan_port, string_ips)
        if results:
            for ip, is_open in zip(string_ips, results):
                if is_open:
                    ipsList.append(ip)
    return ipsList
