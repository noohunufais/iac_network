import yaml
from jinja2 import Environment, FileSystemLoader

# Load YAML configuration
with open('variables/config.yaml') as file:
    config_data = yaml.safe_load(file)

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

# Render main template
main_template = env.get_template('main.j2')
config_output = main_template.render(config_data)

# Output configuration
print(config_output)
