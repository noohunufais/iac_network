import json
from netmiko import ConnectHandler
from datetime import datetime
from threading import Thread

# Placeholder for the file names generated
file_names = []

# Function to connect to the device and retrieve the configuration
def conf(ip, device_type, username, password):
    device = {
        'device_type': device_type, 
        'username': username, 
        'password': password,
        'secret': password  # Assuming the enable secret is the same as the login password
    }

    # Connect to the device using Netmiko
    net_connect = ConnectHandler(**device, ip=ip)
    net_connect.enable()
    
    # Get hostname
    hostname_output = net_connect.send_command("show hostname")
    hostname = ''
    for line in hostname_output.splitlines():
        if line.startswith("Hostname:"):
            hostname = line.split(":")[1].strip()

    # Get the running configuration
    output = net_connect.send_command("show running-config")

    # Format the file name with timestamp
    current_utc_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    file_name = f"{hostname}_{current_utc_time}.txt"
    
    # Save the running-config to a file
    file_path = f"/home/student/iac_network/golden_configs/{file_name}"
    with open(file_path, "w") as file:
        file.write(output)
    
    file_names.append(file_name)

# Function to extract data from the JSON file and initiate configuration collection
def get_golden_config():
    # Read the JSON file
    with open('ipam.json', 'r') as json_file:
        ipam_data = json.load(json_file)

    threads = []

    # Loop through the devices in the JSON
    for device, details in ipam_data.items():
        username = details.get('username')
        password = details.get('password')
        interfaces = details.get('interfaces')

        # Check if Management0 interface exists and has an IP, then use it
        if 'Management0' in interfaces and interfaces['Management0']['ipv4']:
            ip = interfaces['Management0']['ipv4'].split('/')[0]  # Extract the IP address
            # Start the thread to collect the configuration
            thread = Thread(target=conf, args=(ip, 'arista_eos', username, password))
            thread.start()
            threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return file_names

if __name__ == "__main__":
    # Start the process of getting golden configurations
    collected_files = get_golden_config()
    print(f"Collected configuration files: {collected_files}")
