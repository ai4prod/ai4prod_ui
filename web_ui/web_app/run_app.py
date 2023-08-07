from app import create_app,create_db_path

# NOTE: Explicitly import configuration so that PyInstaller is able to find and bundle it
import config
import yaml
import os

#Set current file path to load config independent from python launch path
current_exec_path= os.path.abspath(__file__)
root_exec=os.path.dirname(current_exec_path)
yaml_cfg= root = root_exec+"/gui_cfg.yaml"

db_uri=None
#Read configuration and set db Path before app initialization
with open(yaml_cfg, "r") as yaml_file:
    main_cfg = yaml.safe_load(yaml_file)

    db_uri= create_db_path(main_cfg,root_exec)

application = create_app("config.DevelopmentConfig",db_uri)

import app.turbo_wrapper.turbo_wrapper_call

"""
Address already in use error when using a socket server and a flask webserver in the same script (python)

https://stackoverflow.com/a/63892938
"""
if __name__ == "__main__":

    application.run(host="127.0.0.1", port=4040, use_reloader=True,debug=True)
    