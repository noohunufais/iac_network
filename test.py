# import yaml
# from jinja2 import Environment, FileSystemLoader
# from netmiko import ConnectHandler
# from flask.net_apps import load_ipam_file, get_device_info

# # Load YAML configuration
# with open('variables/config.yaml') as file:
#     config_data = yaml.safe_load(file)

# # Setup Jinja2 environment
# env = Environment(loader=FileSystemLoader('templates'))

# # Render main template
# main_template = env.get_template('main.j2')
# config_output = main_template.render(config_data)

# with open('config.txt', 'w') as file:
#     file.write(config_output)

# ipam_data = load_ipam_file()
# username, password, mgmt_ip = get_device_info(device_name, ipam_data)

# device = {
#         'device_type': 'arista_eos', 
#         'username': username, 
#         'password': password,
#         'ip': mgmt_ip 
#     }

# net_connect = ConnectHandler(**device)
# print(net_connect)
# net_connect.enable()
# output = net_connect.send_config_from_file('config.txt')

# print(output)



import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler
from flask.net_apps import load_ipam_file, get_device_info

def configure_device(device_name, config_data):

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    
    # Render main template with the provided configuration data
    main_template = env.get_template('main.j2')
    config_output = main_template.render(config_data)
    
    # Write rendered configuration to a temporary file
    with open('config.txt', 'w') as file:
        file.write(config_output)
    
    # Load IPAM data and get device credentials
    ipam_data = load_ipam_file()
    username, password, mgmt_ip = get_device_info(device_name, ipam_data)
    
    # Define connection parameters for the device
    device = {
        'device_type': 'arista_eos', 
        'username': username, 
        'password': password,
        'ip': mgmt_ip 
    }
    
    # Connect to the device and apply configuration
    net_connect = ConnectHandler(**device)
    net_connect.enable()
    output = net_connect.send_config_from_file('config.txt')
    
    # Clean up temporary file after use
    net_connect.disconnect()
    
    return output


if __name__ == "__main__":
    # Load YAML configuration
    with open('variables/config.yaml') as file:
        config_data = yaml.safe_load(file)

    device_name = "R1"
    output = configure_device(device_name, config_data)

    print(output)
