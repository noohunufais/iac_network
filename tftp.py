import pexpect
from threading import Thread
from netmiko import ConnectHandler
from time import sleep
from flask.connectivity import ping_check

def config_push(device_name, device_info):
    ip_address = device_info["host"]
    config_file = device_info["config_file"]

    while True:
        if ping_check(ip_address):
            # Remove the 'config_file' key from the device_info dictionary
            device_info = { key: value for key, value in device_info.items() if key != "config_file" }
             
            # Establish connection to the device
            net_connect = ConnectHandler(**device_info)
            net_connect.enable()

            # Send configuration from file to device
            output = net_connect.send_config_from_file(config_file)
            net_connect.save_config()

            print(output)
            print(f'Successfully configured {device_name}')
            net_connect.disconnect()

            # Once the device is successfully configured, run the Docker command
            run_docker_command(device_name)
            break
        else:
            print(f"{device_name} is not reachable!")
            sleep(5)

def run_docker_command(device_name):
    try:
        # Read the password from password.txt
        with open("password.txt", "r") as file:
            password = file.read().strip()
        
        # Start the Docker SCP command
        child = pexpect.spawn(f'sudo docker exec -it clab-netman-{device_name} scp student@10.0.60.100:/home/student/telegraf.conf /home/admin/', encoding='utf-8')
        
        # Handle the first password prompt
        child.expect("password", timeout=10)
        child.sendline(password)

        # Handle the second password prompt
        child.expect("password", timeout=10)
        child.sendline(password)

        # Wait for command to complete
        child.expect(pexpect.EOF)
        
        # If we reach EOF without errors, print a success message
        print(f"Successfully copied the telegraf.conf file to {device_name}.")

    except pexpect.TIMEOUT:
        print(f"Command for {device_name} timed out. Unable to complete within the expected time.")

    except pexpect.EOF:
        print(f"Command for {device_name} finished unexpectedly before completion.")
    
    except FileNotFoundError:
        print("The password.txt file was not found. Please ensure it exists in the same directory as this script.")

    except Exception as e:
        print(f"An error occurred while running the command for {device_name}: {e}")


def main():
    devices = {
        "R6": {
            "device_type": "arista_eos",
            "host": "10.0.40.6",
            "username": "admin",
            "password": "netman",
            "config_file": "tftp/R6.cfg"
        },
        "R7": {
            "device_type": "arista_eos",
            "host": "10.0.50.7",
            "username": "admin",
            "password": "netman",
            "config_file": "tftp/R7.cfg"
        },
        "R8": {
            "device_type": "arista_eos",
            "host": "10.0.110.8",
            "username": "admin",
            "password": "netman",
            "config_file": "tftp/R8.cfg"
        },
        "S5": {
            "device_type": "arista_eos",
            "host": "10.0.120.15",
            "username": "admin",
            "password": "netman",
            "config_file": "tftp/S5.cfg"
        }
    }

    threads = []

    for device_name, device_info in devices.items():
        thread = Thread(target=config_push, args=(device_name, device_info,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()