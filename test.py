from netmiko import ConnectHandler


device = {

    "device_type": "arista_eos",
    "host": "10.0.40.6",
    "username": "admin",
    "password": "netman",

}

net_connect = ConnectHandler(**device)
print(net_connect)
output = net_connect.enable()
print(output)
output = net_connect.send_command('bash')
print(output)