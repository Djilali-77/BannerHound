import paramiko

def get_ssh_banner(ip):
    try :

        transport = paramiko.Transport((ip, 22))
        transport.start_client()
        banner = transport.remote_version
        transport.close()

        return banner

    except Exception as e :
        return None
