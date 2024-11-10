from threading import Thread
from netmiko import ConnectHandler
from time import sleep
from flask.connectivity import ping_check



def config_push(device_name, device_info):

    ip_address = device_info["host"]
    config_file = device_info["config_file"]

    while True:
        if ping_check(ip_address):
            device_info = { key: value for key, value in device_info.items() if key != "config_file" }
             
            net_connect = ConnectHandler(**device_info)
            net_connect.enable()
            output = net_connect.send_config_from_file(config_file)
            net_connect.save_config()
            print(f'Successfully configured {device_name}')
            print(output)
            break

        else:
            print(f"{device_name} is not reachable!")
            sleep(3)

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