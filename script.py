from jinja2 import Template
import json

template_file = "/home/student/iac_network/templates/template.j2"

variable_file = "/home/student/iac_network/variables/R1.json"

with open(variable_file) as json_file:
    config_items = json.load(json_file)

with open(template_file) as f:
    cisco_template = Template(f.read(), keep_trailing_newline=True)

startup_config = cisco_template.render(config_items)


golden_config_file_path = '/home/student/iac_network/rendered_configs/R1.cfg'  

with open(golden_config_file_path, 'w') as output_file:
    output_file.write(startup_config)