from net_apps import net_apps, load_ipam_file
import os
import glob
from netmiko import ConnectHandler
import subprocess
                
# Helper function: Get device information from IPAM
def get_device_info(search_ip, ipam_data):
    for device_name, device_info in ipam_data.items():
        username = device_info['username']
        password = device_info['password']
        mgmt_ip = device_info['interfaces']['Management0']['ipv4'].split('/')[0]
        interfaces = device_info.get('interfaces', {})
        for interface, details in interfaces.items():
            ipv4 = details.get('ipv4', '').split('/')[0]
            if ipv4 == search_ip:
                return device_name, username, password, mgmt_ip
    return None, None, None, None

# Helper function: Perform traceroute
def perform_traceroute(destination_ip):
    try:
        result = subprocess.run(
            ["traceroute", destination_ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Traceroute to {destination_ip}:\n{result.stdout}")
            hops = [
                line.split()[1] for line in result.stdout.splitlines() if line.strip() and line[0].isdigit()
            ]
            return hops
        else:
            print(f"Traceroute failed:\n{result.stderr}")
            return []
    except Exception as e:
        print(f"Error during traceroute: {e}")
        return []
    
# Helper function: Revert device to golden state
def revert_to_golden_state(device_name, device_info):
    golden_config_dir = os.path.join("..", "golden_configs")
    config_file_pattern = os.path.join(golden_config_dir, f"{device_name}_*.txt")
    config_files = sorted(glob.glob(config_file_pattern), reverse=True)

    if config_files:
        latest_golden_config_file = config_files[0]
        print(f"Using golden config: {latest_golden_config_file}")
        
        net_connect = ConnectHandler(**device_info)
        net_connect.enable()
        output = net_connect.send_config_from_file(latest_golden_config_file)
        net_connect.save_config()
        net_connect.disconnect()
        
        print(output)
        print(f"Successfully reverted {device_name} to golden state.")
    else:
        print(f"No golden config found for {device_name}.")
        return False
    return True


def tshoot(ip):
    ipam_data = load_ipam_file()
    device_name, username, password, mgmt_ip = get_device_info(ip,ipam_data)
    device_info = {
        'device_type': 'arista_eos',  
        'host': mgmt_ip,
        'username': username,
        'password': password,
    }

    result = net_apps(device_name,"configComparison")

    if result != None:
        revert_to_golden_state(device_name, device_info)

# tshoot('10.0.60.3')


# Main troubleshooting function
def tshoot(ip):
    ipam_data = load_ipam_file()
    hops = []
    
    while True:
        device_name, username, password, mgmt_ip = get_device_info(ip, ipam_data)
        if not device_name:
            print(f"Device for IP {ip} not found in IPAM.")
            return

        # Device info for Netmiko
        device_info = {
            'device_type': 'arista_eos',
            'host': mgmt_ip,
            'username': username,
            'password': password,
        }

        # Compare and revert configuration if needed
        result = net_apps(device_name, "configComparison")
        if result is not None:
            print(f"Configuration mismatch found on {device_name}. Reverting...")
            revert_to_golden_state(device_name, device_info)

        # Perform traceroute
        hops = perform_traceroute(ip)
        if not hops or hops[-1] == ip:
            print(f"Traceroute successful to {ip}.")
            break
        
        # Use the last reachable hop as the new target for troubleshooting
        last_hop = hops[-1]
        print(f"Last reachable hop: {last_hop}. Moving to next device...")
        ip = last_hop


perform_traceroute('10.0.50.7')
