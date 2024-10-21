from netmiko import ConnectHandler
from threading import Thread
from datetime import datetime
import random
import string
import json

# Function to extract device information
def extract_device_info(data):
    device_info = {}

    for device, details in data.items():
        username = details.get('username')
        password = details.get('password')
        management_ipv4 = details['interfaces'].get('Management0', {}).get('ipv4', 'N/A')

        device_info[device] = {
            'device_type': 'arista_eos',
            'host': management_ipv4.split('/')[0],  # Removing the subnet mask
            'username': username,
            'password': password,
        }

    return device_info

# Function to configure the device with a new password
def conf(device, info, random_word):

    net_connect = ConnectHandler(**info)

    command = f"username admin privilege 15 role network-admin secret {random_word}"
    net_connect.enable()
    net_connect.config_mode()
    output = net_connect.send_command(command)
    net_connect.disconnect()

# Function to update all passwords in the JSON file at once
def update_all_passwords_in_file(devices, new_password):
    # Load the JSON data from the file
    with open('ipam.json', 'r') as file:
        data = json.load(file)

    # Update the password for each device
    for device in devices:
        if device in data:
            data[device]['password'] = new_password

    # Write the updated data back to the JSON file
    with open('ipam.json', 'w') as file:
        json.dump(data, file, indent=4)

# Function to log the new password with timestamp to a file
def log_password_update(new_password):
    current_utc_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    log_entry = f"{current_utc_time}: New password generated - {new_password}\n"

    # Append the log entry to the password log file
    with open('password_log.txt', 'a') as log_file:
        log_file.write(log_entry)

def main():
    # Load the JSON data from a file
    with open('ipam.json', 'r') as file:
        data = json.load(file)

    # Get the device information
    devices_info = extract_device_info(data)

    # Generate a random 5-character password
    random_word = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    # Create threads to handle each device
    threads = []
    for device, info in devices_info.items():
        thread = Thread(target=conf, args=(device, info, random_word))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # After all devices are updated, update the password in the JSON file once
    update_all_passwords_in_file(devices_info.keys(), random_word)

    # Log the new password and the current time to the log file
    log_password_update(random_word)

if __name__ == "__main__":
    main()
