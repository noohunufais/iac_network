from netmiko import ConnectHandler
from datetime import datetime
from threading import Thread

file_names = []

def conf(ip):

    device = {
        'device_type':'arista_eos', 
        'username':'admin', 
        'password':'netman',
        'secret':'netman'
    }

    net_connect = ConnectHandler(**device,ip = ip)
    net_connect.enable()
    hostname_output = net_connect.send_command("show hostname")
    hostname = ''
    for line in hostname_output.splitlines():
            if line.startswith("Hostname:"):
                hostname = line.split(":")[1].strip()
    output = net_connect.send_command("show running-config")


    current_utc_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    file_name = f"{hostname}_{current_utc_time}.txt"

    # Save the running-config to a file
    file_path = f"/home/student/iac_network/golden_configs/{file_name}"
    with open(file_path, "w") as file:
        file.write(output)
    file_names.append(file_name)

def get_golden_config():
    ip_list = [ '10.0.60.1', '10.0.60.2', '10.0.60.3', '10.0.60.4', '10.0.10.11', '10.0.10.12', '10.0.60.13', '10.0.60.14' ]

    threads = []

    for ip in ip_list:
        thread = Thread(target=conf, args=(ip,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return file_names

if __name__ == "__main__":
    get_golden_config()


