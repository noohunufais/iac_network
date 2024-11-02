import json
import subprocess
import glob
from netmiko import ConnectHandler
import os

# Step 1: Load the JSON file
def load_ipam_file(file_path='ipam.json'):
    with open(file_path, 'r') as file:
        ipam_data = json.load(file)
    return ipam_data

# Step 2: Get the device information from JSON
def get_device_info(device_name, ipam_data):
    device_info = ipam_data.get(device_name)
    if device_info:
        username = device_info['username']
        password = device_info['password']
        mgmt_ip = device_info['interfaces']['Management0']['ipv4'].split('/')[0]  # Get IP without the subnet mask
        return username, password, mgmt_ip
    else:
        print(f"Device {device_name} not found in the IPAM data.")
        return None, None, None

# Step 3: Connect to the device using Netmiko for route table, OSPF, BGP, and configuration commands
def connect_to_device(device_name, ipam_data):
    username, password, mgmt_ip = get_device_info(device_name, ipam_data)
    if username and password and mgmt_ip:
        device_params = {
            'device_type': 'arista_eos',  # Modify device type if needed
            'host': mgmt_ip,
            'username': username,
            'password': password,
        }
        try:
            connection = ConnectHandler(**device_params)
            print(f"Successfully connected to {device_name} ({mgmt_ip})")
            return connection
        except Exception as e:
            print(f"Failed to connect to {device_name}: {e}")
            return None
    else:
        print("Missing device connection details.")
        return None


def execute_command(connection, command_choice, device_name, mgmt_ip, custom_command=None):
    if command_choice == "custom" and custom_command:
        output = connection.send_command(custom_command)
    elif command_choice == "routeTable":
        output = connection.send_command("show ip route")
    elif command_choice == "ipConnectivity":
        output = ping_device(mgmt_ip)
    elif command_choice == "ospfNeighborship":
        output = connection.send_command("show ip ospf neighbor")
    elif command_choice == "bgpNeighborship":
        output = connection.send_command("show ip bgp summary")
    elif command_choice == "configComparison":
        output = compare_config(connection, device_name)
    elif command_choice == "runningConfig":
        output = connection.send_command("show running-config")
    elif command_choice == "macaddrTable":
        output = connection.send_command("show mac address-table")
    else:
        output = "Invalid command choice."
    
    return output

# Function to perform local ping to the device's management IP
def ping_device(host):
    try:
        response = subprocess.run(["ping", "-c", "1", host], stdout=subprocess.DEVNULL, timeout=2)
        if response.returncode == 0:
            return f"Ping to {host} successful."
        else:
            return f"Ping to {host} failed."
    except subprocess.TimeoutExpired:
        return f"Ping to {host} timed out."

# Function to compare running configuration with local file using diff
def compare_config(connection, device_name):
    # Get the running configuration from the device
    running_config = connection.send_command("show running-config")

    # Save the running configuration to a temporary file
    running_config_file = f"{device_name}_running_config.txt"
    with open(running_config_file, 'w') as file:
        file.write(running_config)

    # Construct the path to the golden_configs directory relative to the current working directory
    golden_config_dir = os.path.join("..", "golden_configs")
    config_file_pattern = os.path.join(golden_config_dir, f"{device_name}_*.txt")

    # Search for the latest local configuration file in the golden_configs directory
    config_files = sorted(glob.glob(config_file_pattern), reverse=True)


    if config_files:
        latest_config_file = config_files[0]  # Get the most recent file based on timestamp

        print(f"Comparing with local configuration file: {latest_config_file}")
        
        # Use the diff command to compare the files
        try:
            result = subprocess.run(["diff", running_config_file, latest_config_file],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return "No differences found between the running configuration and the local file."
            else:
                return f"Differences found:\n{result.stdout}"
        except Exception as e:
            return f"Error comparing configurations: {e}"
    else:
        return f"No local configuration file found for device {device_name}."
    
# Function to get CPU utilization via SNMP
def get_cpu_utilization(mgmt_ip):
    try:
        # Use the snmpwalk command with the given management IP
        snmp_command = ["snmpwalk", "-v", "2c", "-c", "netman", mgmt_ip, "iso.3.6.1.2.1.25.3.3.1.2"]
        result = subprocess.run(snmp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            # Parse the CPU values from the SNMP response
            cpu_values = [int(line.split(":")[-1].strip()) for line in result.stdout.splitlines()]
            if cpu_values:
                average_cpu = sum(cpu_values) / len(cpu_values)
                rounded_cpu = round(average_cpu, 2)  # Round to two decimal places
                return f"CPU Utilization for {mgmt_ip}: {rounded_cpu}%"
            else:
                return f"No CPU data retrieved for {mgmt_ip}."
        else:
            return f"Error executing SNMP command: {result.stderr}"
    except Exception as e:
        return f"Error retrieving CPU utilization: {e}"


def net_apps(device_name, command_choice, custom_command=None):
    ipam_data = load_ipam_file()
    username, password, mgmt_ip = get_device_info(device_name, ipam_data)

    if command_choice in ["routeTable", "ospfNeighborship", "bgpNeighborship", "configComparison", "runningConfig", "macaddrTable", "custom"]:
        connection = connect_to_device(device_name, ipam_data)
        if connection:
            connection.enable()
            output = execute_command(connection, command_choice, device_name, mgmt_ip, custom_command)
            if output:
                print(f"Command output:\n{output}")
                return output
            connection.disconnect()
    elif command_choice == "ipConnectivity":
        output = ping_device(mgmt_ip)
        print(output)
        return output
    elif command_choice == "cpuUtilization":
        output = get_cpu_utilization(mgmt_ip)
        print(output)
        return output
    else:
        print("Invalid command choice.")

if __name__ == "__main__":
    net_apps()
