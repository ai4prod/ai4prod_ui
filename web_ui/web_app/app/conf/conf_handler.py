import yaml
import os
from omegaconf import DictConfig, OmegaConf, open_dict
from app.home.ai4prod_python.ml_utils.ml_utils import setup_path
from app.home.ai4prod_python.ml_utils.ml_conf.mlconfiguration import MlConfiguration

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
        self.onf_onnx = None
        self.omega_conf_path = None
        self.experiment_folder=None
        self.omega_conf_onnx_path = None

        self.conf_prefix="/app/home/ai4prod_python/"
        self.mlconfiguration= MlConfiguration()
        

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


        #generate ml_conf path for task and experiment name
        if(self.dict_conf["task"]=="classification"):
            mlconf_path= self.root_exec + f"{self.conf_prefix}{self.dict_conf['task']}"
            
            print(mlconf_path)

            self.mlconfiguration.create_classification_conf(base_path=mlconf_path,
                                                            base_experiment_path=self.dict_conf["base_path_experiment"])

        self.omega_conf_path = self.root_exec + self.conf_prefix + \
            self.dict_conf["task"] + "/conf/" + \
            self.dict_conf["task"] + ".yaml"
        
        self.omega_conf_onnx_path = self.root_exec + self.conf_prefix + \
            self.dict_conf["task"] + "/conf/onnx/standard.yaml"
            
        self.onf = OmegaConf.load(self.omega_conf_path)
        self.onf_onnx = OmegaConf.load(self.omega_conf_onnx_path)


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
        
        #This path is used for training and validate the model
        

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
        
    def update_experiment_number_omega_conf(self,):
        
        """_summary_
        
        This function is used to update omega_conf experiment number. Usually
        called before starting a new training
        
        """
        
        self.experiment_folder = self.onf["base_path_experiment"] + self.onf["experiment_name"] + "/"
        print(self.experiment_folder)
        
        if (os.path.isdir(self.experiment_folder)):

            list_dir = os.listdir(self.experiment_folder)
            self.onf["experiment_number"] = len(list_dir)
        else:
            self.onf["experiment_number"] = 0
            
        self.save_only_omega_conf(self.onf,self.omega_conf_path)
        
    def save_only_omega_conf(self,
                             conf:OmegaConf,
                             conf_path:str,
                             ):
        """
        Save Omega conf self.onf into self.omge_conf_path

        """
        with open(conf_path, "w") as f:
            OmegaConf.save(conf, f)

    def update_only_omega_conf(self, 
                               omega_dict_values: DictConfig,
                               conf:OmegaConf):
        """

        Args:
            omega_dict_values (dict): python dict values to change into omegaconf
        """

        return OmegaConf.merge(conf, omega_dict_values)

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

        self.onf = self.update_only_omega_conf(omega_dict,self.onf)

        print(f"OMEGA SAVE PATH {self.onf['general_cfg']['dataset_path']}")
        print(f"OMEGA SAVE PATH {self.omega_conf_path}")
        self.save_only_omega_conf(self.onf,self.omega_conf_path)
        
        
    #ONNX CONFIGURATION
    
    
    def update_onnx_conversion_parameters(self,model_path:str):
        """
        This function is used select the model 
        to be used for conversion
        
        Args:
            model_path (str): path to .ckpt model
        """
        parameters= {"model_ckpt_path":model_path}
        self.update_onnx_configuration(parameters)
    
    def update_onnx_configuration(self, dict_values:dict):
        """
        General function used to change onnx configuration .yaml

        Args:
            dict_values (dict): dictionary containing the parameters to be changed
        """
        omega_dict = OmegaConf.create(dict_values)
        print(self.omega_conf_onnx_path)
        
        self.onf_onnx = self.update_only_omega_conf(omega_dict,self.onf_onnx)
        self.save_only_omega_conf(self.onf_onnx,self.omega_conf_onnx_path)
        


configurationHandler = ConfigurationHandler()

if __name__ == "__main__":

    cconf = configurationHandler
