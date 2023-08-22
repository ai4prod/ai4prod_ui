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
        self.onf = None
        self.omega_conf_path = None

    def init(self, root_exec):

        self.root_exec = root_exec
        self.conf_path = root_exec + "/gui_cfg.yaml"
        # Create first configuration file if not present
        if not os.path.exists(self.conf_path):
            # Create the YAML file and write the initial dictionary
            self.save_conf_file()
        else:
            print(f"{self.conf_path} already exists. Read Old Configuration")
            self.read_conf_file()

        self.omega_conf_path = self.root_exec + "\\app\\home\\ai4prod_python\\" + \
            self.dict_conf["task"] + "\\conf\\" + \
            self.dict_conf["task"] + ".yaml"

    def save_conf_file(self):

        with open(self.conf_path, 'w') as yaml_file:
            yaml.dump(self.dict_conf, yaml_file, default_flow_style=False)
            print(
                f"Created {self.conf_path} and initialized with initial dictionary.")

    def save_conf(self, key, value):
        """
        Used to update internal conf and configuration file

        """
        if key in self.dict_conf:
            self.dict_conf[key] = value
            self.save_conf_file()
        else:
            print("CANNOT UPDATE CONFIGURATION VALUE")

    def read_conf_file(self,):

        with open(self.conf_path, "r") as yaml_file:
            self.dict_conf = yaml.safe_load(yaml_file)

    def create_db_path(self):
        self.onf = OmegaConf.load(self.omega_conf_path)
        self.onf["base_path_experiment"] = self.dict_conf["base_path_experiment"]
        self.onf["db_name"] = self.dict_conf["db_name"]
        self.onf["task"] = self.dict_conf["task"]
        self.onf["general_cfg"]["dataset_path"] = self.dict_conf["dataset_path"]
        self.onf["general_cfg"]["dataset_versioning"] = self.dict_conf["dataset_versioning"]
        self.onf["general_cfg"]["data_version_tag"] = self.dict_conf["data_version_tag"]
        self.onf["general_cfg"]["data_version_name"] = self.dict_conf["data_version_name"]

        setup_path(self.omega_conf_path, self.onf, False)

        return self.onf["tracking_uri"]

    def save_dataset_cfg(self,
                         dataset_path: str,
                         dataset_version_tag: str,
                         dataset_id:str,
                         experiment_name: str,
                         dataset_versioning=True,
                         ):
        """Save dataset configuration to task/conf/task.yaml and to
        gui_cfg.yaml

        Args:
            dataset_path (str): Path to a dataset. Needs to be a git repository
            dataset_version_tag (str): DatasetVersion tag to use. Correspond to a git tag
            dataset_id (str): id of the dataset saved a database. This is used to track with MLFlow
            stats with a corresponding dataset
            experiment_name (str): name of the experiment. All models are saved in this folders. Name correpond to
            repository path last part for example /home/test/data_name. data_name is the experimet_name
            dataset_versioning (bool, optional): If true dataset versioning is used during training otherwise is disabled.
            
        """
        dataset_values = {"dataset_path": dataset_path,
                          "dataset_id": dataset_id,
                          "data_version_tag": dataset_version_tag,
                          "dataset_versioning": dataset_versioning}

        omega_dict_values = {"general_cfg": dataset_values,
                             "experiment_name": experiment_name}

        self.update_conf(dict_values=dataset_values,
                         omega_dict_values=omega_dict_values)

    def update_dataset_version(self,
                               dataset_version_tag: str,
                               dataset_id:str):
        """
        Used to update cfg dataset version

        Args:
            dataset_version_tag (str): version of dataset
        """

        dataset_values = {
            "data_version_tag": dataset_version_tag,
            "dataset_id": dataset_id
        }
        
        omega_dict_values = {"general_cfg": dataset_values,
                             }

        self.update_conf(dict_values=dataset_values,
                         omega_dict_values=omega_dict_values)
        

    def save_only_omega_conf(self):
        """
        Save Omega conf self.onf into self.omge_conf_path

        """
        with open(self.omega_conf_path, "w") as f:
            OmegaConf.save(self.onf, f)

    def update_only_omege_conf(self, omega_dict_values: dict):
        """

        Args:
            omega_dict_values (dict): python dict values to change into omegaconf
        """

        self.onf = OmegaConf.merge(self.onf, omega_dict_values)

    def update_conf(self, dict_values: dict, omega_dict_values=None):
        """
        args:
            :param dict_values: contains a dictionary with all value to be updated 
            inside conf
            :param omega_dict_values if not None means that omega Conf value has a different
            dict respect to dict_values. Usually dict values are used to update gui_cfg.yaml
            while omega_dit_values are used to update task value for training.

        This method will update local config and task config based on 
        dataset_version, path and
        """
        # Update Global Config Value
        self.dict_conf = {
            key: dict_values[key] if key in dict_values else value for key, value in self.dict_conf.items()}
        self.save_conf_file()

        print(f"DICT CONF {self.dict_conf}")

        # Update OmegaConf Value
        if(omega_dict_values is None):

            omega_dict = OmegaConf.create(dict_values)
        else:
            omega_dict = OmegaConf.create(omega_dict_values)

        self.update_only_omege_conf(omega_dict)

        print(f"OMEGA SAVE PATH {self.onf['general_cfg']['dataset_path']}")
        print(f"OMEGA SAVE PATH {self.omega_conf_path}")
        self.save_only_omega_conf()


configurationHandler = ConfigurationHandler()

if __name__ == "__main__":

    cconf = configurationHandler
