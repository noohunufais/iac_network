from flask import Flask, render_template, request, jsonify
import getconfig
import net_apps
from config_device import configure_device
import tshoot_interface

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/add_device", methods=['GET','POST'])
def add_device():
    if request.method == 'GET':
        return render_template('add_device.html')

    return request.form


@app.route("/golden_config", methods=['GET'])
def golden_config():

    golden_config_data = sorted(getconfig.get_golden_config())
    return render_template('golden_config.html', golden_config=golden_config_data )

@app.route('/alerts', methods=['POST'])
def receive_alert():
    try:
        # Parse the incoming JSON payload
        alert_data = request.json
        
        # Extract the IP address (instance label)
        if 'alerts' in alert_data and len(alert_data['alerts']) > 0:
            instance_ip = alert_data['alerts'][0]['labels'].get('instance', 'No IP found')
            tshoot_interface.tshoot(instance_ip)
            
        else:
            instance_ip = 'No IP found'
        
        return jsonify({"status": "success", "instance_ip": instance_ip}), 200

    except Exception as e:
        print(f"Error processing alert: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    

@app.route("/tools", methods=['GET', 'POST'])
def tools():
    if request.method == 'POST':
        device_name = request.form['deviceName']
        operation = request.form['operation']
        custom_command = request.form.get('customCommand') if operation == "custom" else None

        output = net_apps.net_apps(device_name, operation, custom_command)
        
        return render_template('tools_output.html', output=output)
    
    else:

        devices_list = list(net_apps.load_ipam_file().keys())
        return render_template('tools.html', devices_list=devices_list)


@app.route('/config_push', methods=['GET', 'POST'])
def config_push():
    if request.method == 'POST':

        device_name = request.form['deviceName']

        # Capture VLAN data
        vlan_numbers = request.form.getlist('vlan[]')
        vlan_names = request.form.getlist('vlan_name[]')

        # Capture Interface data
        interface_names = request.form.getlist('interface_name[]')
        interface_descriptions = request.form.getlist('interface_description[]') 
        ipv4_addresses = request.form.getlist('ipv4_address[]')
        ipv4_subnets = request.form.getlist('ipv4_subnet[]')
        ipv6_addresses = request.form.getlist('ipv6_address[]')
        ipv6_prefixes = request.form.getlist('ipv6_prefix[]')
        switchports = request.form.getlist('switchport[]')
        interface_statuses = request.form.getlist('interface_status[]')

        # Capture IPv4 Static Route data
        ipv4_dest_networks = request.form.getlist('ipv4_dest_network[]')
        ipv4_subnets = request.form.getlist('ipv4_subnet[]')
        ipv4_next_hops = request.form.getlist('ipv4_next_hop[]')

        # Capture IPv6 Static Route data
        ipv6_dest_networks = request.form.getlist('ipv6_dest_network[]')
        ipv6_prefixes = request.form.getlist('ipv6_prefix[]')
        ipv6_next_hops = request.form.getlist('ipv6_next_hop[]')

        # Capture Logging data
        # log_trap_type = request.form.get('log_trap_type')
        # log_host_ip = request.form.get('log_host_ip')
        # log_source_address = request.form.get('log_source_address')

        # Capture SNMP data
        # snmp_version = request.form.get('snmp_version')
        # community_string = request.form.get('community_string')
        # snmp_permission = request.form.get('snmp_permission')
        # snmp_host_ip = request.form.get('snmp_host_ip')


        # Capture OSPFv2 Process ID and Router ID
        ospfv2_process_id = request.form.get('ospfv2_process_id')
        ospfv2_router_id = request.form.get('ospfv2_router_id')

        # Capture OSPFv2 Network data
        ospfv2_networks = request.form.getlist('ospfv2_network[]')
        ospfv2_subnet_masks = request.form.getlist('ospfv2_subnet_mask[]')
        ospfv2_areas = request.form.getlist('ospfv2_area[]')

        # Capture Redistribute data (None if unchecked)
        ospfv2_redistribute_bgp = request.form.get('ospfv2_redistribute_bgp')
        ospfv2_redistribute_rip = request.form.get('ospfv2_redistribute_rip')
        ospfv2_redistribute_static = request.form.get('ospfv2_redistribute_static')
        ospfv2_redistribute_connected = request.form.get('ospfv2_redistribute_connected')

        # Debugging: Print the captured data to the console (for testing purposes)
        # print("VLAN Data:")
        # for i, (vlan_num, vlan_name) in enumerate(zip(vlan_numbers, vlan_names), start=1):
        #     print(f"VLAN {i}: Number={vlan_num}, Name={vlan_name}")

        print("\nInterface Data:")
        for i, (iface_name, ipv4, subnet, ipv6, prefix, switchport) in enumerate(zip(interface_names, ipv4_addresses, ipv4_subnets, ipv6_addresses, ipv6_prefixes, switchports), start=1):
            print(f"Interface {i}: Name={iface_name}, IPv4={ipv4}, Subnet={subnet}, IPv6={ipv6}, Prefix={prefix}, Switchport={switchport}")

        # print("\nIPv4 Static Route Data:")
        # for i, (dest, subnet, next_hop) in enumerate(zip(ipv4_dest_networks, ipv4_subnets, ipv4_next_hops), start=1):
        #     print(f"Route {i}: Destination Network={dest}, Subnet Mask={subnet}, Next Hop={next_hop}")

        # print("\nIPv6 Static Route Data:")
        # for i, (dest, prefix, next_hop) in enumerate(zip(ipv6_dest_networks, ipv6_prefixes, ipv6_next_hops), start=1):
        #     print(f"Route {i}: Destination Network={dest}, Prefix={prefix}, Next Hop={next_hop}")

        # print("\nLogging Data:")
        # print(f"Trap Type: {log_trap_type}")
        # print(f"Host IP: {log_host_ip}")
        # print(f"Source Address: {log_source_address}")

        # print("SNMP Data:")
        # print(f"SNMP Version: {snmp_version}")
        # print(f"Community String: {community_string}")
        # print(f"Permission: {snmp_permission}")
        # print(f"Host IP: {snmp_host_ip}")

        # print("Basic Settings Data:")
        # print(f"Hostname: {hostname}")
        # print(f"Username: {username}")
        # print(f"Password: {password}")
        # print(f"Privilege: {privilege}")
        # print(f"Role: {role}")

        # print("OSPFv2 Network Data:")
        # for i, (network, subnet, area) in enumerate(zip(ospfv2_networks, ospfv2_subnet_masks, ospfv2_areas), start=1):
        #     print(f"Network {i}: Network={network}, Subnet Mask={subnet}, Area Number={area}")

        # print("\nRedistribute Options:")
        # print(f"BGP: {ospfv2_redistribute_bgp}, RIP: {ospfv2_redistribute_rip}, Static: {ospfv2_redistribute_static}, Connected: {ospfv2_redistribute_connected}")

        # Prepare configuration data from form input
        config_data = {
            'ipv4_routes': [
                {'destination': dest, 'subnet_mask': subnet, 'next_hop': next_hop}
                for dest, subnet, next_hop in zip(ipv4_dest_networks, ipv4_subnets, ipv4_next_hops)
            ],
            'ipv6_routes': [
                {'destination': dest, 'prefix': prefix, 'next_hop': next_hop}
                for dest, prefix, next_hop in zip(ipv6_dest_networks, ipv6_prefixes, ipv6_next_hops)
            ],
            'ospf': {
                'process_id': ospfv2_process_id,
                'router_id': ospfv2_router_id if ospfv2_router_id else None,
                'networks': [
                    {'network': network, 'wildcard_mask': wildcard_mask, 'area': area}
                    for network, wildcard_mask, area in zip(ospfv2_networks, ospfv2_subnet_masks, ospfv2_areas)
                ],
                'redistribute': {
                    'bgp': ospfv2_redistribute_bgp == '1',
                    'rip': ospfv2_redistribute_rip == '1',
                    'static': ospfv2_redistribute_static == '1',
                    'connected': ospfv2_redistribute_connected == '1'
                }
            },
            'vlans': [
                {'vlan_id': vlan, 'name': name}
                for vlan, name in zip(vlan_numbers, vlan_names)
            ],
            'interfaces': [
                {
                    'name': name,
                    'description': description,  
                    'ip_address': ip,
                    'subnet_mask': subnet,
                    'ipv6_address': ipv6,
                    'ipv6_prefix_length': ipv6_prefix,
                    'status': status,
                    'switchport': switchport == '1'

                }
                for name, description, ip, subnet, ipv6, ipv6_prefix, switchport, status in zip(
                    interface_names, interface_descriptions, ipv4_addresses, ipv4_subnets, ipv6_addresses, ipv6_prefixes, switchports, interface_statuses
                )
            ]
        }

        print(config_data)


        try:
            output = configure_device(device_name, config_data)
            return f'<pre> {output} </pre>'
        except Exception as e:
            return 'FAILURE'
    else:
        devices_list = list(net_apps.load_ipam_file().keys())
        return render_template('config_push.html', devices_list=devices_list)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
