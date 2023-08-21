import yaml
import os
from app import create_db_path

class ConfigurationHandler:

    def __init__(self) -> None:
        self.conf_path = None

        self.dict_conf = {
            'db_name': 'general',
            'base_path_experiment': 'C:/Users/erict/OneDrive\Desktop/Develop/experimentNew/',
            'task': "classification",
            'dataset_path': 'C:/Users/',
            'dataset_versioning': False,
            'data_version_tag': '1',
            'data_version_name': 'Dataset.dvc',
        }

    def init(self, root_exec):
        
        self.root_exec=root_exec
        self.conf_path = root_exec + "/gui_cfg.yaml"
        #Create first configuration file if not present
        if not os.path.exists(self.conf_path):
            # Create the YAML file and write the initial dictionary
            self.save_conf_file()
        else:
            print(f"{self.conf_path} already exists. Skipping creation.")

    def save_conf_file(self):
         
        with open(self.conf_path, 'w') as yaml_file:
            yaml.dump(self.dict_conf, yaml_file, default_flow_style=False)
            print(f"Created {self.conf_path} and initialized with initial dictionary.")


    def save_conf(self,key,value):

        """
        Used to update internal conf and configuration file

        """
        if key in self.dict_conf:
            self.dict_conf[key]=value
            self.save_conf_file()
        else:
            print("CANNOT UPDATE CONFIGURATION VALUE")

    def read_conf_file(self,):
        
        with open(self.conf_path, "r") as yaml_file:
            self.dict_conf = yaml.safe_load(yaml_file)

    
configurationHandler = ConfigurationHandler()

if __name__ == "__main__":

    cconf = configurationHandler
