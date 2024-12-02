from net_apps import net_apps, load_ipam_file
import os
import glob
from netmiko import ConnectHandler
import subprocess
import ipaddress


# Create or overwrite the log file at the beginning of the script
with open("troubleshooting_log.txt", "w") as log_file:
    log_file.write("Troubleshooting Log\n")
    log_file.write("===================\n\n")

# Helper function: Write logs to a file
def write_log(message):
    with open("troubleshooting_log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

# Helper function: Get device information from IPAM
def get_device_info(search_ip, ipam_data):
    write_log(f"Searching for device with IP {search_ip} in IPAM data.")
    for device_name, device_info in ipam_data.items():
        username = device_info['username']
        password = device_info['password']
        mgmt_ip = device_info['interfaces']['Management0']['ipv4'].split('/')[0]
        interfaces = device_info.get('interfaces', {})
        for interface, details in interfaces.items():
            ipv4 = details.get('ipv4', '').split('/')[0]
            if ipv4 == search_ip:
                write_log(f"Found device: {device_name} for IP {search_ip}.")
                return device_name, username, password, mgmt_ip
    write_log(f"No device found for IP {search_ip} in IPAM.")
    return None, None, None, None

# Helper function: Perform traceroute
def perform_traceroute(destination_ip):
    write_log(f"Starting traceroute to {destination_ip}.")
    try:
        result = subprocess.run(
            ["traceroute", destination_ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            write_log(f"Traceroute output:\n{result.stdout}")
            hops = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if parts and parts[0].isdigit():  # Ensure the line starts with a number (hop count)
                    try:
                        # Validate if the second column is a valid IP address
                        ip = parts[1]
                        ipaddress.ip_address(ip)
                        hops.append(ip)
                    except ValueError:
                        # Skip non-IP address entries
                        continue
            write_log(f"Traceroute hops: {hops}")
            return hops
        else:
            write_log(f"Traceroute failed:\n{result.stderr}")
            return []
    except Exception as e:
        write_log(f"Error during traceroute: {e}")
        return []

# Helper function: Revert device to golden state
def revert_to_golden_state(device_name, device_info):
    write_log(f"Attempting to revert {device_name} to its golden state.")
    golden_config_dir = os.path.join("..", "golden_configs")
    config_file_pattern = os.path.join(golden_config_dir, f"{device_name}_*.txt")
    config_files = sorted(glob.glob(config_file_pattern), reverse=True)

    if config_files:
        latest_golden_config_file = config_files[0]
        write_log(f"Using golden config: {latest_golden_config_file}")

        with open(latest_golden_config_file, 'r') as file:
            config_lines = file.readlines()
        
        updated_config = []
        for line in config_lines:
            updated_config.append(line.strip())
            if line.strip().startswith("interface "):
                updated_config.append(" no shutdown")

        try:
            net_connect = ConnectHandler(**device_info)
            net_connect.enable()
            output = net_connect.send_config_set(updated_config)
            net_connect.save_config()
            net_connect.disconnect()
            write_log(f"Successfully reverted {device_name} to golden state.\n{output}")
        except Exception as e:
            write_log(f"Failed to revert {device_name} to golden state: {e}")
            return False
    else:
        write_log(f"No golden config found for {device_name}.")
        return False
    return True

# Main troubleshooting function
def tshoot(ip):
    write_log(f"Starting troubleshooting process for IP: {ip}")
    ipam_data = load_ipam_file()
    hops = []
    target_ip = ip
    troubleshooted_devices = set()
    
    while True:
        # Get device info from IPAM data
        device_name, username, password, mgmt_ip = get_device_info(ip, ipam_data)
        
        if not device_name:
            write_log(f"Device for IP {ip} not found in IPAM.")
            return
        
        if device_name in troubleshooted_devices:
            send_email()
            
        troubleshooted_devices.add(device_name)

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
            write_log(f"Configuration mismatch found on {device_name}. Reverting...")
            reverted = revert_to_golden_state(device_name, device_info)
            if not reverted:
                write_log(f"Failed to revert {device_name} to golden state.")
                return
        else:
            write_log(f"No configuration mismatch detected on {device_name}.")

        # Perform traceroute
        hops = perform_traceroute(target_ip)
        if not hops:
            write_log(f"Traceroute to {target_ip} failed. Exiting troubleshooting.")
            break
        elif hops[-1] == target_ip:
            write_log(f"Traceroute successful to {target_ip}.")
            break
        
        # Use the last reachable hop as the new target for troubleshooting
        last_hop = hops[-1]
        write_log(f"Last reachable hop: {last_hop}. Moving to next device for troubleshooting...")
        ip = last_hop
