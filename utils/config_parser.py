import os
import yaml

rev_dir = os.environ.get('PATH_REV')

class ConfigParser:

    def __init__(self):

        with open(f"{rev_dir}/config.yaml", 'r') as file:
            self.yaml_data = yaml.safe_load(file)

    def set_reverse_frame(self, value):

        self.yaml_data['reverse_frame'] = value

    def set_reset_mode(self, value):

        self.yaml_data['reset_mode'] = value


    def save_yaml(self):

        with open(f"{rev_dir}/config.yaml", 'w') as file:
            yaml.dump(self.yaml_data, file)