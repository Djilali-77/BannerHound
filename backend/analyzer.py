def analyze_banner(banner):
    if not banner:
        return "Unknown or Offline"
    
    device_type = banner
    
    if 'Ubuntu' in banner:
        device_type = "Linux Server (Ubuntu)"
    elif 'Debian' in banner:
        device_type = "Linux Server (Debian)"
    elif 'Cisco' in banner:
        device_type = "Cisco Router/Switch"
    elif 'MikroTik' in banner:
        device_type = "MikroTik Router"
        
    elif 'HTTP: Apache' in banner:
        device_type = "Web Server (Apache)"
    elif 'nginx' in banner.lower():
        device_type = "Web Server (Nginx)"
    elif 'microhttpd' in banner.lower() or 'lighttpd' in banner.lower():
        device_type = "Router / Embedded Device"
    elif 'HTTP:' in banner:
        device_type = "Web Device (HTTP Open)"
    elif 'HTTPS:' in banner:
        device_type = "Secure Web Server (HTTPS)"
    elif 'Telnet:' in banner:
        if 'Cisco' in banner or 'Router' in banner:
            device_type = "Legacy Cisco/Router (Telnet)"
        else:
            device_type = "Legacy Device (Telnet Open)"

    return device_type