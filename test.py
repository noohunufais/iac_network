import yaml
from jinja2 import Environment, FileSystemLoader

# Load YAML data from variables/routing_config.yaml
with open("variables/routes.yml", "r") as yaml_file:
    routing_data = yaml.safe_load(yaml_file)

# Set up the Jinja environment to load templates from the templates directory
env = Environment(loader=FileSystemLoader("templates"))

# Load both IPv4 and IPv6 templates
ipv4_template = env.get_template("ipv4_static_route.j2")
ipv6_template = env.get_template("ipv6_static_route.j2")
vlan_template = env.get_template("vlan.j2")

# Render both templates using the respective data
ipv4_output = ipv4_template.render(ipv4_routes=routing_data["ipv4_routes"])
ipv6_output = ipv6_template.render(ipv6_routes=routing_data["ipv6_routes"])
vlan_output = vlan_template.render(vlans=routing_data["vlans"])

# Print the outputs with clear section headings
print("IPv4 Routes Configuration:")
print(ipv4_output)
print("\nIPv6 Routes Configuration:")
print(ipv6_output)
print("\nVLAN Configuration:")
print(vlan_output)
