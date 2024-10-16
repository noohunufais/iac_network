from flask import Flask, render_template, request, redirect, url_for
import getconfig
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/add_device", methods=['GET','POST'])
def add_device():
    if request.method == 'GET':
        return render_template('add_device.html')
    else:
        return request.form


@app.route("/golden_config", methods=['GET'])
def golden_config():
    return getconfig.get_golden_config()


@app.route('/test_form', methods=['GET', 'POST'])
def test_form():
    if request.method == 'POST':
        # Capture VLAN data
        vlan_numbers = request.form.getlist('vlan[]')
        vlan_names = request.form.getlist('vlan_name[]')

        # Capture Interface data
        interface_names = request.form.getlist('interface_name[]')  # List of Interface names
        ipv4_addresses = request.form.getlist('ipv4_address[]')  # List of IPv4 addresses
        ipv4_subnets = request.form.getlist('ipv4_subnet[]')  # List of IPv4 subnets
        ipv6_addresses = request.form.getlist('ipv6_address[]')  # List of IPv6 addresses
        ipv6_prefixes = request.form.getlist('ipv6_prefix[]')  # List of IPv6 prefixes
        switchports = request.form.getlist('switchport[]')

        # Capture IPv4 Static Route data
        ipv4_dest_networks = request.form.getlist('ipv4_dest_network[]')
        ipv4_subnets = request.form.getlist('ipv4_subnet[]')
        ipv4_next_hops = request.form.getlist('ipv4_next_hop[]')

        # Capture IPv6 Static Route data
        ipv6_dest_networks = request.form.getlist('ipv6_dest_network[]')
        ipv6_prefixes = request.form.getlist('ipv6_prefix[]')
        ipv6_next_hops = request.form.getlist('ipv6_next_hop[]')

        # Capture Logging data
        log_trap_type = request.form.get('log_trap_type')
        log_host_ip = request.form.get('log_host_ip')
        log_source_address = request.form.get('log_source_address')

        # Debugging: Print the captured data to the console (for testing purposes)
        print("VLAN Data:")
        for i, (vlan_num, vlan_name) in enumerate(zip(vlan_numbers, vlan_names), start=1):
            print(f"VLAN {i}: Number={vlan_num}, Name={vlan_name}")

        print("\nInterface Data:")
        for i, (iface_name, ipv4, subnet, ipv6, prefix, switchport) in enumerate(zip(interface_names, ipv4_addresses, ipv4_subnets, ipv6_addresses, ipv6_prefixes, switchports), start=1):
            print(f"Interface {i}: Name={iface_name}, IPv4={ipv4}, Subnet={subnet}, IPv6={ipv6}, Prefix={prefix}, Switchport={switchport}")

        print("\nIPv4 Static Route Data:")
        for i, (dest, subnet, next_hop) in enumerate(zip(ipv4_dest_networks, ipv4_subnets, ipv4_next_hops), start=1):
            print(f"Route {i}: Destination Network={dest}, Subnet Mask={subnet}, Next Hop={next_hop}")

        print("\nIPv6 Static Route Data:")
        for i, (dest, prefix, next_hop) in enumerate(zip(ipv6_dest_networks, ipv6_prefixes, ipv6_next_hops), start=1):
            print(f"Route {i}: Destination Network={dest}, Prefix={prefix}, Next Hop={next_hop}")

        print("\nLogging Data:")
        print(f"Trap Type: {log_trap_type}")
        print(f"Host IP: {log_host_ip}")
        print(f"Source Address: {log_source_address}")

        return request.form
    return render_template('test_form.html')
        

if __name__ == "__main__":
    app.run(host='0.0.0.0')
