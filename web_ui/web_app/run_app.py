import config
import yaml
import os
from app import create_app
from app.conf.conf_handler import configurationHandler


db_uri = None
# # Set current file path to load config independent from python launch path
current_exec_path = os.path.abspath(__file__)
root_exec = os.path.dirname(current_exec_path)

configurationHandler.init(root_exec=root_exec)

db_uri = configurationHandler.create_db_path()

application = create_app("config.DevelopmentConfig", db_uri)

#After app initialization import turbo_wrapper call
import app.turbo_wrapper.turbo_wrapper_call

"""
Address already in use error when using a socket server and a flask webserver in the same script (python)

https://stackoverflow.com/a/63892938
"""
if __name__ == "__main__":

    application.run(host="127.0.0.1", port=4040)
