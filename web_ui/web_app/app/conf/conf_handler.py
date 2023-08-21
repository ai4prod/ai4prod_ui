import yaml
import os
from omegaconf import DictConfig, OmegaConf, open_dict
from app.home.ai4prod_python.ml_utils.ml_utils import setup_path

class ConfigurationHandler:

    def __init__(self) -> None:
        self.conf_path = None

        self.dict_conf = {
            'db_name': 'general',
            'base_path_experiment': 'C:/Users/erict/OneDrive/Desktop/Develop/experimentNew/',
            'task': "classification",
            'dataset_path': 'C:/Users/',
            'dataset_versioning': False,
            'data_version_tag': '1',
            'data_version_name': 'Dataset.dvc',
        }
        self.onf=None
        self.omgega_conf_path=None

    def init(self, root_exec):
        
        self.root_exec=root_exec
        self.conf_path = root_exec + "/gui_cfg.yaml"
        #Create first configuration file if not present
        if not os.path.exists(self.conf_path):
            # Create the YAML file and write the initial dictionary
            self.save_conf_file()
        else:
            print(f"{self.conf_path} already exists. Skipping creation.")

        self.omgega_conf_path= self.root_exec + "/app/home/ai4prod_python/" +  self.dict_conf["task"]+ "/conf/"+  self.dict_conf["task"] +".yaml"

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

    def create_db_path(self):
        self.onf = OmegaConf.load(self.omgega_conf_path)
        self.onf["base_path_experiment"]=  self.dict_conf["base_path_experiment"]
        self.onf["db_name"]=  self.dict_conf["db_name"]
        self.onf["task"]=  self.dict_conf["task"]
        self.onf["general_cfg"]["dataset_path"]=  self.dict_conf["dataset_path"]
        self.onf["general_cfg"]["dataset_versioning"]=  self.dict_conf["dataset_versioning"]
        self.onf["general_cfg"]["data_version_tag"]=  self.dict_conf["data_version_tag"]
        self.onf["general_cfg"]["data_version_name"]=  self.dict_conf["data_version_name"]


        setup_path(self.omgega_conf_path,self.onf,False)

        return self.onf["tracking_uri"]

    def update_conf(self,dict_values:dict):
        """

        :param dict_values: contains a dictionary with all value to be updated 
        inside conf
        This method will update local config and task config based on 
        dataset_version, path and
        """
        #Update Global Config Value
        self.dict_conf = {key: dict_values[key] if key in dict_values else value for key, value in self.dict_conf.items()}
        self.save_conf_file()

        #Update OmegaConf Value
        omgega_dict= OmegaConf.create(dict_values)
        self.onf = OmegaConf.merge_with(self.onf, omgega_dict)
        
        OmegaConf.save(self.omgega_conf_path,self.onf)
    
configurationHandler = ConfigurationHandler()

if __name__ == "__main__":

    cconf = configurationHandler
