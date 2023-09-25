import yaml
import os
from omegaconf import DictConfig, OmegaConf, open_dict
from app.home.ai4prod_python.ml_utils.ml_utils import setup_path
from app.home.ai4prod_python.ml_utils.ml_conf.mlconfiguration import MlConfiguration


class ConfigurationHandler:
    """
    self.onf_task_training = "Current configuration loaded used for training"
    self.onf_task_onnx= "Current configuration laoded used for convert model to onnx"
    self.conf_prefix_path= Dict used to save the relative position on each conf folder in ai4prod_python repository based on task
    """

    def __init__(self) -> None:
        self.conf_path = None

        self.dict_conf = {
            'db_name': 'general',
            'base_path_experiment': '/home/Develop/Experiment/',
            'task': "classification",
            'dataset_path': '/home/Develop/Dataset/',
            'dataset_remote': '/home/Develop/RemoteDataset/',
            'dataset_versioning': False,
            'data_version_tag': '1',
            'data_version_name': 'Dataset.dvc',
        }

        self.conf_prefix_path = {"anomalyDetection": "/anomalib_mlops/conf/",
                                 "classification": "/conf/",
                                 "objectDetection": "/FlashObjectDetection/conf/",
                                 "semanticSegmentation": "/conf/",
                                 }

        self.bitbucket_conf = {
            "bitbucket_user": "",
            "bitbucket_password": ""
        }
        self.base_path_experiment = "/home/Develop/Experiment/"
        self.base_path_configuration = "/home/Develop/Configuration/"
        self.bitbucket_conf_path = "/home/Develop/Configuration/bitbucket_conf.yaml"
        self.onf_task_training = None
        self.onf_task_onnx = None
        self.omega_conf_path = None
        self.experiment_folder = None
        self.omega_conf_onnx_path = None

        self.conf_prefix = "/app/home/ai4prod_python/"
        self.mlconfiguration = MlConfiguration()

    def init(self, root_exec=None):
        """

        root_exec: base path to gui_cfg.yaml. This configuration is used to keep track of last 
        global parameter used

        if root_exec != None this function is called at the start of the app

        Used to setup new configuration or init the configuration if root_exec==None 
        Called when init the app and when user change dataset used for training

        root_exec:

        """
        if (not root_exec == None):
            self.root_exec = root_exec
        self.conf_path = root_exec + "/gui_cfg.yaml"
        # Create first configuration file if not present
        if not os.path.exists(self.conf_path):
            # Create the YAML file and write the initial dictionary
            self.save_conf_file()
        else:
            print(f"{self.conf_path} already exists. Read Old Configuration")
            self.read_conf_file()

        conf_relative_path = ""

        # generate ml_conf path for task and experiment name

        mlconf_path = self.root_exec + \
            f"{self.conf_prefix}{self.dict_conf['task']}"

        print(f"MAIN TASK CONFIGURATION {mlconf_path}")
        conf_relative_path = self.conf_prefix_path[self.dict_conf["task"]]
        self.mlconfiguration.create_conf(base_path=mlconf_path,
                                         base_experiment_path=self.dict_conf["base_path_experiment"],
                                         task=self.dict_conf["task"])

        self.omega_conf_path = self.root_exec + self.conf_prefix + \
            self.dict_conf["task"] + conf_relative_path + \
            self.dict_conf["task"] + ".yaml"

        self.omega_conf_onnx_path = self.root_exec + self.conf_prefix + \
            self.dict_conf["task"] + conf_relative_path + "onnx/standard.yaml"

        self.onf_task_training = OmegaConf.load(self.omega_conf_path)
        self.onf_task_onnx = OmegaConf.load(self.omega_conf_onnx_path)

        # setup bitbucket password for Cloud
        # self.setup_bitbucket_cloud()

    def setup_bitbucket_cloud(self,):
        # TODO: NEED TO REMOVE Bitbucket conf is Handled inside Database
        """
        Create bibucket conf if not exists inside configuration folder 
        If configuration files exists load the current value inside 
        self.bitbucket_conf
        """
        if not os.path.exists(self.bitbucket_conf_path):
            with open(self.bitbucket_conf_path, "w") as yaml_file:
                yaml.dump(self.bitbucket_conf, yaml_file,
                          default_flow_style=False)
        else:
            # If the YAML file exists, read its contents
            with open(self.bitbucket_conf_path, "r") as yaml_file:
                self.bitbucket_conf = yaml.safe_load(yaml_file)

        print(f"BITBUCKET CONF {self.bitbucket_conf}")

    def get_bitbucket_cloud_credentials(self,):

        return self.bitbucket_conf["bitbucket_user"], self.bitbucket_conf["bitbucket_password"]

    def get_dataset_path(self):
        """
        Return current path for datasets

        """
        return self.dict_conf["dataset_path"]

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
        """
        This function will update omega conf value to setup mlflow tracking with correct db Path
        """
        self.onf_task_training["base_path_experiment"] = self.dict_conf["base_path_experiment"]
        self.onf_task_training["db_name"] = self.dict_conf["db_name"]
        self.onf_task_training["task"] = self.dict_conf["task"]
        self.onf_task_training["general_cfg"]["dataset_path"] = self.dict_conf["dataset_path"]
        self.onf_task_training["general_cfg"]["dataset_versioning"] = self.dict_conf["dataset_versioning"]
        self.onf_task_training["general_cfg"]["data_version_tag"] = self.dict_conf["data_version_tag"]
        self.onf_task_training["general_cfg"]["data_version_name"] = self.dict_conf["data_version_name"]

        setup_path(self.omega_conf_path, self.onf_task_training, False)

        return self.onf_task_training["tracking_uri"]

    def save_dataset_cfg(self,
                         dataset_path: str,
                         dataset_version_tag: str,
                         dataset_id: str,
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

        # This path is used for training and validate the model

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
                               dataset_id: str):
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

    def update_gui_cfg_task(self,
                            task,
                            dataset_version_tag,
                            dataset_id
                            ):
        """
        This function is used to change the main task used for training and update or create
        the main configuration used for training 
        """
        dataset_values = {
            "task": task,
        }
        #update gui_cfg.yaml with new task
        self.update_conf(dict_values=dataset_values)
                
        #create training configuration in ai4prod_python/task
        self.init()

        #after creating new conf update conf value on both gui_cfg.yaml an on OmegaConf task inside ai4prod_python
        self.update_dataset_version(dataset_id=dataset_id,dataset_version_tag=dataset_version_tag)


    def update_experiment_number_omega_conf(self,):
        """_summary_

        This function is used to update omega_conf experiment number. Usually
        called before starting a new training

        """
        print(f"EXP NAME {self.onf_task_training['experiment_name']}")
        self.experiment_folder = self.onf_task_training["base_path_experiment"] + \
            self.onf_task_training["experiment_name"] + "/"
        print(self.experiment_folder)

        if (os.path.isdir(self.experiment_folder)):

            list_dir = os.listdir(self.experiment_folder)
            self.onf_task_training["experiment_number"] = len(list_dir)
        else:
            self.onf_task_training["experiment_number"] = 0

        self.save_only_omega_conf(self.onf_task_training, self.omega_conf_path)

    def save_only_omega_conf(self,
                             conf: OmegaConf,
                             conf_path: str,
                             ):
        """
        Save Omega conf self.onf_task_training into self.omge_conf_path

        """
        with open(conf_path, "w") as f:
            OmegaConf.save(conf, f)

    def update_only_omega_conf(self,
                               omega_dict_values: DictConfig,
                               conf: OmegaConf):
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
        if (omega_dict_values is None):

            omega_dict = OmegaConf.create(dict_values)
        else:
            omega_dict = OmegaConf.create(omega_dict_values)

        self.onf_task_training = self.update_only_omega_conf(
            omega_dict, self.onf_task_training)

        print(
            f"OMEGA SAVE PATH {self.onf_task_training['general_cfg']['dataset_path']}")
        print(f"OMEGA SAVE PATH {self.omega_conf_path}")
        self.save_only_omega_conf(self.onf_task_training, self.omega_conf_path)

    # ONNX CONFIGURATION

    def update_onnx_conversion_parameters(self, model_path: str):
        """
        This function is used select the model 
        to be used for conversion

        Args:
            model_path (str): path to .ckpt model
        """
        parameters = {"model_ckpt_path": model_path}
        self.update_onnx_configuration(parameters)

    def update_onnx_configuration(self, dict_values: dict):
        """
        General function used to change onnx configuration .yaml

        Args:
            dict_values (dict): dictionary containing the parameters to be changed
        """
        omega_dict = OmegaConf.create(dict_values)
        print(self.omega_conf_onnx_path)

        self.onf_task_onnx = self.update_only_omega_conf(
            omega_dict, self.onf_task_onnx)
        self.save_only_omega_conf(
            self.onf_task_onnx, self.omega_conf_onnx_path)


configurationHandler = ConfigurationHandler()

if __name__ == "__main__":

    cconf = configurationHandler
