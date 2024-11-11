import pexpect
from threading import Thread
from netmiko import ConnectHandler
from time import sleep
from flask.connectivity import ping_check
import subprocess

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
            password = file.read().strip()  # Remove any extra whitespace or newline characters
        
        # Start the Docker SCP command to copy the file
        child = pexpect.spawn(f'sudo docker exec -it clab-netman-{device_name} scp student@10.0.60.100:/home/student/telegraf.conf /home/admin/', encoding='utf-8')
        
        # Handle the first password prompt for SCP
        child.expect("password", timeout=10)
        child.sendline(password)

        # Handle the second password prompt for SCP
        child.expect("password", timeout=10)
        child.sendline(password)

        # Wait for SCP command to complete
        child.expect(pexpect.EOF)

        # Print the output of the SCP command
        print(f"SCP command output for {device_name}:")
        print(child.before)  # This captures and prints the output of the SCP command
        
        # Run the telegraf command with an expected password prompt
        telegraf_command = f'sudo docker exec -d -it clab-netman-{device_name} telegraf --config /home/admin/telegraf.conf'
        child = pexpect.spawn(telegraf_command, encoding='utf-8')

        # Check if the telegraf command requests a password
        i = child.expect([pexpect.TIMEOUT, "password"], timeout=10)
        if i == 1:
            # Send password if prompted
            child.sendline(password)

        # Wait for the command to go into the background and return control
        child.expect(pexpect.EOF)

        # Since it's in detached mode, we don't wait for the command to finish
        print(f"Telegraf started in detached mode on {device_name} and will run continuously.")

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

    try:
        # Define the directory to execute commands in
        work_dir = "/home/student/iac_network/"

        # 1. Pull latest code
        result = subprocess.run(['git', 'pull', 'origin', 'main'], cwd=work_dir, capture_output=True, text=True)
        print("Git pull output:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error in git pull: {result.stderr}")

        # 2. Stage changes for commit
        result = subprocess.run(['git', 'add', '.'], cwd=work_dir, capture_output=True, text=True)
        print("Git add output:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error in git add: {result.stderr}")

        # 3. Commit changes with a message
        result = subprocess.run(['git', 'commit', '-m', 'deployed'], cwd=work_dir, capture_output=True, text=True)
        print("Git commit output:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error in git commit: {result.stderr}")

        # 4. Push changes to the repository
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=work_dir, capture_output=True, text=True)
        print("Git push output:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error in git push: {result.stderr}")

        # 5. Run test coverage
        result = subprocess.run(['coverage', 'run', '-m', 'unittest', 'discover', 'tests'], cwd=work_dir, capture_output=True, text=True)
        print("Test coverage output:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error in coverage run: {result.stderr}")

        # 6. Generate HTML coverage report
        result = subprocess.run(['coverage', 'html'], cwd=work_dir, capture_output=True, text=True)
        print("HTML coverage report output:")
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error in coverage html: {result.stderr}")

        print("All Git and coverage operations completed successfully.")

    except FileNotFoundError as e:
        print(f"Command not found or could not be executed: {e}")
    except Exception as e:
        print(f"An error occurred during Git or coverage operations: {e}")


    

if __name__ == "__main__":
    main()