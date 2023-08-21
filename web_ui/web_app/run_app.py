import config
import yaml
import os
from app import create_app, create_db_path
from app.conf.conf_handler import configurationHandler

#DEFAULT CFG

# conf_dict_default = {
#     'experiment_name': 'test',
#     'base_path_experiment': 'C:/Users/erict/OneDrive/Desktop/Develop/Experiment/classificaton_gui/',
#     'task':"classification",
#     'dataset_path': 'C:/Users/erict/OneDrive/Desktop/Develop/Dataset/DVintel/Data/Dataset/',
#     'dataset_versioning': False,
#     'data_version_tag': 'v4',
#     'data_version_name': 'Dataset.dvc',
# }

# db_uri = None
# # Set current file path to load config independent from python launch path
# current_exec_path = os.path.abspath(__file__)
# root_exec = os.path.dirname(current_exec_path)
# yaml_cfg = root_exec+"/gui_cfg.yaml"

# if not os.path.exists(yaml_cfg):
#     # Create the YAML file and write the initial dictionary
#     with open(yaml_cfg, 'w') as yaml_file:
#         yaml.dump(conf_dict_default, yaml_file, default_flow_style=False)
#     print(f"Created {yaml_cfg} and initialized with initial dictionary.")
# else:
#     print(f"{yaml_cfg} already exists. Skipping creation.")


# # Read configuration and set db Path before app initialization
# with open(yaml_cfg, "r") as yaml_file:
#     main_cfg = yaml.safe_load(yaml_file)

db_uri = None
# # Set current file path to load config independent from python launch path
current_exec_path = os.path.abspath(__file__)
root_exec = os.path.dirname(current_exec_path)

configurationHandler.init(root_exec=root_exec)

db_uri = create_db_path(configurationHandler.dict_conf, root_exec)

application = create_app("config.DevelopmentConfig", db_uri)

#After app initialization import turbo_wrapper call
import app.turbo_wrapper.turbo_wrapper_call

"""
Address already in use error when using a socket server and a flask webserver in the same script (python)

https://stackoverflow.com/a/63892938
"""
if __name__ == "__main__":

    application.run(host="127.0.0.1", port=4040, debug=True)
