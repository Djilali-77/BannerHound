def analyze_banner(banner):
    
    if not banner:
        return "Unknown or Offline"
    elif 'Ubuntu' in banner:
        return "Linux Server (Ubuntu)"
    elif 'Cisco' in banner:
        return "Cisco Router/Switch"
    elif 'Debian' in banner:
        return "Linux Server (Debian)"
    elif 'MikroTik' in banner:
        return "MikroTik Router"
    else:
        return banner