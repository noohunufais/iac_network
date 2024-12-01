from net_apps import net_apps, load_ipam_file

def get_device_name(search_ip):
    ipam_data = load_ipam_file()

    for device_name, device_info in ipam_data.items():
            interfaces = device_info.get('interfaces', {})
            for interface, details in interfaces.items():
                # Check if the IPv4 matches (ignoring /subnet)
                ipv4 = details.get('ipv4', '').split('/')[0]
                if ipv4 == search_ip:
                    return device_name
        


def tshoot(ip):
    device = get_device_name(ip)

    result = net_apps(device,"configComparison")

tshoot('10.0.60.1')